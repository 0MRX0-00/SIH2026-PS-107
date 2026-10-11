"""
Regression and Verification Tests for Critical Repairs:
1. RequestBodySizeLimitMiddleware (declared Content-Length and streaming chunked bodies)
2. Chat Debug Endpoint Administrator Authorization
3. InMemoryRateLimiter memory boundedness, IP churn, thread safety, and eviction
4. Production readiness validation and database credential safety
"""
import time
import threading
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings, Settings
from app.core.middleware import (
    InMemoryRateLimiter,
    RequestBodySizeLimitMiddleware,
    rate_limiter,
)
from app.services.groq_service import groq_service

client = TestClient(app)


# ==============================================================================
# 1. Request Body Size Limiter Tests (Declared vs Chunked)
# ==============================================================================

class TestRequestBodySizeLimiter:
    """Verifies that 2MB body size limit is enforced across all transfer encodings."""

    def test_valid_small_request_passes(self):
        resp = client.post(
            "/api/v1/chat",
            json={"message": "What is IS 1293?", "language": "en"}
        )
        assert resp.status_code in (200, 429)

    def test_oversized_declared_content_length_rejected(self):
        # 3 MB declared payload
        oversized_data = b"A" * (3 * 1024 * 1024)
        resp = client.post(
            "/api/v1/chat",
            content=oversized_data,
            headers={"Content-Type": "application/json", "Content-Length": str(len(oversized_data))}
        )
        assert resp.status_code == 413
        assert resp.json().get("error_code") == "PAYLOAD_TOO_LARGE"

    def test_oversized_chunked_streaming_rejected(self):
        # Streaming generator simulating chunked transfer encoding without Content-Length
        def chunk_generator():
            # Send 3 chunks of 1 MB each (3 MB total)
            chunk = b"X" * (1024 * 1024)
            for _ in range(3):
                yield chunk

        resp = client.post(
            "/api/v1/chat",
            content=chunk_generator(),
            headers={"Content-Type": "application/json"}
        )
        assert resp.status_code == 413
        assert resp.json().get("error_code") == "PAYLOAD_TOO_LARGE"

    def test_valid_chunked_streaming_accepted(self):
        # Streaming small chunks (< 2MB)
        def small_chunk_generator():
            yield b'{"message": "Hello BIS", '
            yield b'"language": "en"}'

        resp = client.post(
            "/api/v1/chat",
            content=small_chunk_generator(),
            headers={"Content-Type": "application/json"}
        )
        assert resp.status_code in (200, 429)


# ==============================================================================
# 2. Chat Debug Endpoint Authorization Tests
# ==============================================================================

class TestChatDebugEndpointSecurity:
    """Verifies that /api/v1/chat/debug requires administrator authentication."""

    def test_chat_debug_unauthenticated_rejected(self):
        # No X-Admin-Key header
        resp = client.post(
            "/api/v1/chat/debug",
            json={"message": "Debug test", "language": "en"}
        )
        assert resp.status_code == 401
        assert "X-Admin-Key" in resp.json().get("detail", "")

    def test_chat_debug_invalid_key_rejected(self):
        # Incorrect X-Admin-Key header
        resp = client.post(
            "/api/v1/chat/debug",
            json={"message": "Debug test", "language": "en"},
            headers={"X-Admin-Key": "totally-invalid-key-xyz"}
        )
        assert resp.status_code == 401

    def test_chat_debug_missing_server_key_fails_closed(self, monkeypatch):
        # When ADMIN_API_KEY is not configured on server
        monkeypatch.setattr(settings, "ADMIN_API_KEY", "")
        resp = client.post(
            "/api/v1/chat/debug",
            json={"message": "Debug test", "language": "en"},
            headers={"X-Admin-Key": "any-key"}
        )
        assert resp.status_code == 500
        assert "not configured" in resp.json().get("detail", "")

    def test_chat_debug_authorized_success(self, monkeypatch):
        # Valid admin authentication
        admin_key = "test-debug-admin-key-2026"
        monkeypatch.setattr(settings, "ADMIN_API_KEY", admin_key)

        resp = client.post(
            "/api/v1/chat/debug",
            json={"message": "What is IS 1293?", "language": "en"},
            headers={"X-Admin-Key": admin_key}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "intent" in data
        assert "system_prompt" in data
        assert "model" in data


# ==============================================================================
# 3. InMemoryRateLimiter Memory Boundedness & Churn Tests
# ==============================================================================

class TestInMemoryRateLimiterBounds:
    """Verifies bounded capacity, expiration pruning, and thread safety."""

    def test_rate_limiter_bounds_memory_under_ip_churn(self):
        limiter = InMemoryRateLimiter(max_entries=500, cleanup_interval_seconds=1)
        
        # Simulate flood of 2,000 unique client IPs
        for i in range(2000):
            ip = f"10.0.{i // 256}.{i % 256}"
            allowed, _ = limiter.is_allowed(ip, "general", limit=100)
            assert allowed is True

        # State size must be strictly bounded at or below max_entries
        assert len(limiter._records) <= 500

    def test_rate_limiter_cleans_up_expired_keys(self):
        limiter = InMemoryRateLimiter(max_entries=1000, cleanup_interval_seconds=0)
        
        # Add entries with old timestamps
        old_time = time.time() - 120
        limiter._records[("192.168.1.1", "general")] = [old_time]
        limiter._records[("192.168.1.2", "general")] = [old_time]
        limiter._records[("192.168.1.3", "general")] = [time.time()] # active

        assert len(limiter._records) == 3

        # Next request triggers cleanup of expired records
        limiter.is_allowed("192.168.1.4", "general", limit=10)

        # Expired keys should be purged
        assert ("192.168.1.1", "general") not in limiter._records
        assert ("192.168.1.2", "general") not in limiter._records
        assert ("192.168.1.3", "general") in limiter._records

    def test_rate_limiter_multithreaded_concurrency_safety(self):
        limiter = InMemoryRateLimiter(max_entries=100, cleanup_interval_seconds=1)
        errors = []

        def worker(worker_id):
            try:
                for req in range(50):
                    ip = f"172.16.0.{worker_id}"
                    limiter.is_allowed(ip, "general", limit=1000)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(limiter._records) <= 100


# ==============================================================================
# 4. Production Database Credential Safety Validation Tests
# ==============================================================================

class TestProductionCredentialSafety:
    """Verifies that production mode rejects default and weak database credentials."""

    def test_production_readiness_rejects_weak_db_password(self):
        s = Settings(
            ENVIRONMENT="production",
            GROQ_API_KEY="gsk_real_key_for_testing_1234567890",
            ADMIN_API_KEY="strong-random-admin-secret-key-2026",
            DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/ebis_sahayak"
        )
        with pytest.raises(RuntimeError) as exc_info:
            s.validate_production_readiness()
        assert "insecure default password" in str(exc_info.value)

    def test_production_readiness_passes_with_strong_credentials(self):
        s = Settings(
            ENVIRONMENT="production",
            GROQ_API_KEY="gsk_real_key_for_testing_1234567890",
            ADMIN_API_KEY="strong-random-admin-secret-key-2026",
            DATABASE_URL="postgresql+asyncpg://app_user:V3ry$tr0ngP@ssw0rd!@db.prod.internal:5432/ebis_sahayak"
        )
        # Should not raise
        s.validate_production_readiness()
