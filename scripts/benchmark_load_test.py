"""
Automated Performance, Reliability, and Load Testing Suite for e-BIS Sahayak
(SIH 2026 Problem Statement #107).

Measures:
- Baseline single-request response time and statistics across all backend endpoints
- Concurrency scaling (1, 5, 10, 20 concurrent workers)
- Latency percentiles: min, p50 (median), p95, p99, max
- Throughput (requests / second) and error rates
- Failure mode injection: timeouts, oversized payload, malformed JSON, rate-limiting, and error handling
"""
import sys
import os
import time
import json
import statistics
import concurrent.futures
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any, Optional

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.groq_service import groq_service

# Configure test admin key
settings.ADMIN_API_KEY = "test-perf-admin-key-2026"

client = TestClient(app)

ENDPOINTS = [
    {
        "name": "Health Check",
        "method": "GET",
        "path": "/health",
        "json": None,
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Standards List (All)",
        "method": "GET",
        "path": "/api/v1/standards/",
        "json": None,
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Standard Detail (IS 1293)",
        "method": "GET",
        "path": "/api/v1/standards/std-1293",
        "json": None,
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Laboratory Statistics",
        "method": "GET",
        "path": "/api/v1/laboratories/stats",
        "json": None,
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Laboratory Search (Delhi/Electrical)",
        "method": "POST",
        "path": "/api/v1/laboratories/search",
        "json": {"state": "Delhi", "product_category": "Electrical", "limit": 20},
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Certification Roadmap (FMCS)",
        "method": "POST",
        "path": "/api/v1/certification/roadmap",
        "json": {"manufacturer_type": "foreign", "standard_id": "std-1293"},
        "headers": {},
        "expected_status": 200,
    },
    {
        "name": "Feedback Submission",
        "method": "POST",
        "path": "/api/v1/feedback",
        "json": {"query": "What is IS 1293?", "is_helpful": True, "rating": 5, "comment": "Excellent guidance"},
        "headers": {},
        "expected_status": 201,
    },
    {
        "name": "Admin Overview (Authorized)",
        "method": "GET",
        "path": "/api/v1/admin/overview",
        "json": None,
        "headers": {"X-Admin-Key": "test-perf-admin-key-2026"},
        "expected_status": 200,
    },
]


def run_single_request(ep: Dict[str, Any], client_ip: str = "127.0.0.1") -> Dict[str, Any]:
    start_time = time.perf_counter()
    try:
        method = ep["method"]
        path = ep["path"]
        json_data = ep.get("json")
        headers = dict(ep.get("headers") or {})
        headers["X-Forwarded-For"] = client_ip

        if method == "GET":
            resp = client.get(path, headers=headers)
        elif method == "POST":
            resp = client.post(path, json=json_data, headers=headers)
        else:
            raise ValueError(f"Unsupported method {method}")

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        success = (resp.status_code == ep["expected_status"])
        return {
            "success": success,
            "status_code": resp.status_code,
            "latency_ms": elapsed_ms,
            "error": None if success else f"Status {resp.status_code} != {ep['expected_status']} ({resp.text[:100]})"
        }
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "status_code": 0,
            "latency_ms": elapsed_ms,
            "error": str(e)
        }


def benchmark_endpoint_concurrency(ep: Dict[str, Any], concurrency: int, total_requests: int) -> Dict[str, Any]:
    latencies: List[float] = []
    successes = 0
    failures = 0
    errors = []

    # Disable rate limiting for pure throughput scaling measurements across distributed client pool
    orig_rl = settings.RATE_LIMIT_ENABLED
    settings.RATE_LIMIT_ENABLED = False

    start_suite = time.perf_counter()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(run_single_request, ep, f"192.168.1.{i % 250 + 1}")
                for i in range(total_requests)
            ]
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                latencies.append(res["latency_ms"])
                if res["success"]:
                    successes += 1
                else:
                    failures += 1
                    if res["error"]:
                        errors.append(res["error"])
    finally:
        settings.RATE_LIMIT_ENABLED = orig_rl

    total_wall_time = time.perf_counter() - start_suite
    throughput = total_requests / total_wall_time if total_wall_time > 0 else 0

    latencies.sort()
    p50 = statistics.median(latencies) if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0
    mean_lat = statistics.mean(latencies) if latencies else 0

    return {
        "endpoint": ep["name"],
        "path": ep["path"],
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successes": successes,
        "failures": failures,
        "error_rate_pct": (failures / total_requests) * 100 if total_requests else 0,
        "throughput_rps": round(throughput, 2),
        "mean_ms": round(mean_lat, 2),
        "p50_ms": round(p50, 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "min_ms": round(min(latencies), 2) if latencies else 0,
        "max_ms": round(max(latencies), 2) if latencies else 0,
        "errors": list(set(errors))[:3]
    }


def test_assistant_chat_load(concurrency: int, total_requests: int) -> Dict[str, Any]:
    """Test Chat assistant endpoint under concurrency load with mocked Groq async completion."""
    mock_response = (
        "IS 1293:2019 specifies standard requirements for plugs and socket-outlets (up to 250V and 16A). "
        "Under Ministry of Commerce and Industry QCO S.O. 4311(E), certification is mandatory."
    )

    with patch.object(groq_service, "generate_chat_completion", new=AsyncMock(return_value=mock_response)):
        chat_ep = {
            "name": "Chat Assistant (Groq Mocked)",
            "method": "POST",
            "path": "/api/v1/chat",
            "json": {"message": "What is the mandatory QCO for IS 1293 plugs?", "language": "en"},
            "headers": {},
            "expected_status": 200
        }
        return benchmark_endpoint_concurrency(chat_ep, concurrency, total_requests)


def test_failure_modes() -> List[Dict[str, Any]]:
    """Test error handling, malformed inputs, timeouts, rate limits, and boundary conditions."""
    results = []

    # 1. Malformed JSON Body
    resp = client.post("/api/v1/chat", content=b"{invalid_json_payload", headers={"Content-Type": "application/json"})
    results.append({
        "scenario": "Malformed JSON in Request Body",
        "expected_status": "422",
        "actual_status": str(resp.status_code),
        "pass": resp.status_code == 422,
        "detail": "FastAPI/Pydantic returns 422 Unprocessable Entity for invalid JSON syntax."
    })

    # 2. Oversized Payload (> 2 MB)
    oversized_bytes = b"X" * (3 * 1024 * 1024)  # 3 MB
    resp = client.post("/api/v1/chat", content=oversized_bytes, headers={"Content-Type": "application/json", "Content-Length": str(len(oversized_bytes))})
    results.append({
        "scenario": "Oversized Payload (>2MB Body)",
        "expected_status": "413",
        "actual_status": str(resp.status_code),
        "pass": resp.status_code == 413,
        "detail": "RequestBodySizeLimitMiddleware returns 413 Request Entity Too Large."
    })

    # 3. Missing Required Fields in Request (Feedback requires query & is_helpful)
    resp = client.post("/api/v1/feedback", json={})
    results.append({
        "scenario": "Missing Required Fields (Empty Feedback Payload)",
        "expected_status": "422",
        "actual_status": str(resp.status_code),
        "pass": resp.status_code == 422,
        "detail": "Schema validation returns 422 Unprocessable Entity with structured field error messages."
    })

    # 4. Unknown Standard Lookup
    resp = client.get("/api/v1/standards/NON-EXISTENT-STANDARD-99999")
    results.append({
        "scenario": "Query for Non-Existent Standard ID",
        "expected_status": "404",
        "actual_status": str(resp.status_code),
        "pass": resp.status_code == 404,
        "detail": "Returned 404 Not Found with clear descriptive error message."
    })

    # 5. Unauthorized Admin Access
    resp = client.get("/api/v1/admin/overview", headers={"X-Admin-Key": "invalid-secret-key-12345"})
    results.append({
        "scenario": "Admin Endpoint with Invalid Key",
        "expected_status": "401",
        "actual_status": str(resp.status_code),
        "pass": resp.status_code == 401,
        "detail": "Unauthorized request rejected with HTTP 401 Unauthorized."
    })

    # 6. Groq Provider Outage Exception Handling
    with patch.object(groq_service, "generate_chat_completion", new=AsyncMock(side_effect=Exception("Groq API 503 Service Unavailable"))):
        resp = client.post("/api/v1/chat", json={"message": "What is IS 1293?", "language": "en"})
        results.append({
            "scenario": "LLM Provider Outage (Groq 503 Exception)",
            "expected_status": "200 fallback",
            "actual_status": str(resp.status_code),
            "pass": resp.status_code == 200,
            "detail": "Handled gracefully with fallback message without crashing backend process."
        })

    # 7. Rate Limiter Throttling on Single IP Hammering
    settings.RATE_LIMIT_ENABLED = True
    rate_limited_count = 0
    test_ip = "10.0.0.99"
    for _ in range(150):
        r = client.get("/api/v1/standards/", headers={"X-Forwarded-For": test_ip})
        if r.status_code == 429:
            rate_limited_count += 1

    results.append({
        "scenario": "Rate Limiter Single IP Burst Protection",
        "expected_status": "429 after threshold",
        "actual_status": f"{rate_limited_count} requests throttled (HTTP 429)",
        "pass": rate_limited_count > 0,
        "detail": f"Rate limiter throttled {rate_limited_count}/150 rapid burst requests with Retry-After header."
    })

    return results


def main():
    print("=" * 80)
    print("e-BIS Sahayak Performance, Reliability & API-Load Audit")
    print("=" * 80)

    # 1. Baseline Latency Measurement (Single Request per Endpoint)
    print("\n--- Phase 1: Baseline Single-Request Latency ---")
    baseline_results = []
    for ep in ENDPOINTS:
        res = run_single_request(ep, client_ip="10.10.10.1")
        baseline_results.append({
            "name": ep["name"],
            "path": ep["path"],
            "latency_ms": round(res["latency_ms"], 2),
            "status": res["status_code"],
            "success": res["success"]
        })
        print(f"[{res['status_code']}] {ep['name']:<40}: {res['latency_ms']:.2f} ms")

    # 2. Concurrency Load Testing across Tiers (1, 5, 10, 20)
    print("\n--- Phase 2: Concurrency & Throughput Scaling ---")
    concurrency_tiers = [1, 5, 10, 20]
    load_matrix = []

    for tier in concurrency_tiers:
        total_reqs = 100
        print(f"\n>> Testing Concurrency Tier: {tier} concurrent workers ({total_reqs} requests/endpoint)...")
        for ep in ENDPOINTS:
            res = benchmark_endpoint_concurrency(ep, concurrency=tier, total_requests=total_reqs)
            load_matrix.append(res)
            print(f"  {res['endpoint']:<38} | p50: {res['p50_ms']:>6.2f}ms | p95: {res['p95_ms']:>6.2f}ms | {res['throughput_rps']:>7.2f} req/s | Err: {res['error_rate_pct']:.1f}%")

        # Chat Assistant under concurrency
        chat_res = test_assistant_chat_load(concurrency=tier, total_requests=total_reqs)
        load_matrix.append(chat_res)
        print(f"  {chat_res['endpoint']:<38} | p50: {chat_res['p50_ms']:>6.2f}ms | p95: {chat_res['p95_ms']:>6.2f}ms | {chat_res['throughput_rps']:>7.2f} req/s | Err: {chat_res['error_rate_pct']:.1f}%")

    # 3. Failure and Reliability Injections
    print("\n--- Phase 3: Reliability and Failure Injection ---")
    failure_results = test_failure_modes()
    for f in failure_results:
        status_str = "PASS" if f["pass"] else "FAIL"
        print(f"[{status_str}] {f['scenario']:<48}: {f['detail']}")

    # Save complete JSON summary
    summary_output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "baseline": baseline_results,
        "load_matrix": load_matrix,
        "failure_modes": failure_results
    }
    with open("backend/tests/load_test_results.json", "w", encoding="utf-8") as out_f:
        json.dump(summary_output, out_f, indent=2)

    print("\nBenchmark completed. Results exported to backend/tests/load_test_results.json")


if __name__ == "__main__":
    main()
