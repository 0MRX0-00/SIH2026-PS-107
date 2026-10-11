import time
import uuid
import json
import logging
import threading
from typing import Dict, List, Tuple, Optional
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.config import settings

logger = logging.getLogger("ebis_sahayak.security")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique X-Request-ID to every incoming HTTP request and attaches it to response headers.
    Enables end-to-end tracing for debugging and SIH demonstration audits.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends enterprise security headers to protect against clickjacking, MIME-sniffing, and XSS.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class BodyTooLargeException(HTTPException):
    """Raised when request payload exceeds configured byte limit."""
    def __init__(self, detail: str = "Request payload exceeds maximum allowed size (2MB).", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=detail,
            headers={"X-Request-ID": request_id or str(uuid.uuid4())}
        )


class RequestBodySizeLimitMiddleware:
    """
    Pure ASGI middleware that enforces MAX_REQUEST_BODY_SIZE_BYTES across all transfer encodings,
    including declared Content-Length and Transfer-Encoding: chunked.
    Rejects oversized requests with HTTP 413 without loading excessive data into memory.
    """

    def __init__(self, app, max_bytes: Optional[int] = None):
        self.app = app
        self.max_bytes = max_bytes if max_bytes is not None else settings.MAX_REQUEST_BODY_SIZE_BYTES

    def _make_413_payload(self, detail: Optional[str] = None) -> Tuple[bytes, str]:
        request_id = str(uuid.uuid4())
        max_mb = max(1, self.max_bytes // (1024 * 1024))
        msg_detail = detail or f"Request payload exceeds maximum allowed size ({max_mb}MB)."
        body = json.dumps({
            "detail": msg_detail,
            "error_code": "PAYLOAD_TOO_LARGE",
            "request_id": request_id
        }).encode("utf-8")
        return body, request_id

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 1. Fast-path check on Content-Length header if present
        for header_name, header_val in scope.get("headers", []):
            if header_name.lower() == b"content-length":
                try:
                    if int(header_val.decode("latin1")) > self.max_bytes:
                        await self._send_413(scope, send)
                        return
                except ValueError:
                    pass
                break

        # 2. Streaming size enforcement on ASGI receive (chunked and unannounced transfers)
        received_bytes = 0
        body_too_large = False
        response_started = False
        body_sent = False
        cached_413_body, cached_req_id = self._make_413_payload()

        async def streaming_receive():
            nonlocal received_bytes, body_too_large
            message = await receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                received_bytes += len(body)
                if received_bytes > self.max_bytes:
                    body_too_large = True
                    raise BodyTooLargeException(
                        detail=f"Request payload exceeds maximum allowed size ({self.max_bytes // (1024 * 1024)}MB)."
                    )
            return message

        async def intercepting_send(message):
            nonlocal response_started, body_sent
            if body_too_large:
                if message["type"] == "http.response.start":
                    if not response_started:
                        response_started = True
                        response_headers = [
                            (b"content-type", b"application/json"),
                            (b"content-length", str(len(cached_413_body)).encode("latin1")),
                            (b"x-request-id", cached_req_id.encode("latin1")),
                            (b"connection", b"close"),
                        ]
                        await send({
                            "type": "http.response.start",
                            "status": 413,
                            "headers": response_headers,
                        })
                elif message["type"] == "http.response.body":
                    if not body_sent:
                        body_sent = True
                        await send({
                            "type": "http.response.body",
                            "body": cached_413_body,
                        })
                return
            response_started = True
            await send(message)

        try:
            await self.app(scope, streaming_receive, intercepting_send)
        except BodyTooLargeException as exc:
            if not response_started:
                await self._send_413(scope, send, detail=exc.detail)

    async def _send_413(self, scope, send, detail: Optional[str] = None):
        body, request_id = self._make_413_payload(detail)
        response_headers = [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("latin1")),
            (b"x-request-id", request_id.encode("latin1")),
            (b"connection", b"close"),
        ]

        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": response_headers,
        })
        await send({
            "type": "http.response.body",
            "body": body,
        })


class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Tracks client requests by IP and endpoint category with bounded capacity and periodic eviction.
    NOTE: This is a single-process in-memory rate limiter; it is not a distributed limiter across multiple replicas.
    """

    def __init__(self, max_entries: int = 10000, cleanup_interval_seconds: int = 30):
        self.max_entries = max_entries
        self.cleanup_interval_seconds = cleanup_interval_seconds
        # Key: (client_ip, endpoint_bucket) -> List[timestamp]
        self._records: Dict[Tuple[str, str], List[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()

    def _cleanup_expired(self, now: float, window_seconds: int = 60):
        """Removes expired timestamps and empties out stale IP records across the state."""
        keys_to_delete = []
        for key, timestamps in self._records.items():
            valid = [t for t in timestamps if now - t < window_seconds]
            if valid:
                self._records[key] = valid
            else:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            del self._records[key]
        self._last_cleanup = now

    def _evict_lru_if_needed(self):
        """Enforces hard upper bound on state size to prevent memory exhaustion under high-cardinality IP churn."""
        if len(self._records) >= self.max_entries:
            sorted_keys = sorted(
                self._records.keys(),
                key=lambda k: self._records[k][-1] if self._records[k] else 0
            )
            evict_count = max(1, len(self._records) - int(self.max_entries * 0.8))
            for k in sorted_keys[:evict_count]:
                self._records.pop(k, None)

    def is_allowed(self, client_ip: str, bucket: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Thread-safe rate limit evaluation. Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        key = (client_ip, bucket)

        with self._lock:
            # Periodic sweep of expired records or when approaching capacity
            if now - self._last_cleanup > self.cleanup_interval_seconds or len(self._records) >= self.max_entries:
                self._cleanup_expired(now, window_seconds)
                self._evict_lru_if_needed()

            timestamps = self._records.get(key, [])
            valid_timestamps = [t for t in timestamps if now - t < window_seconds]

            if len(valid_timestamps) >= limit:
                self._records[key] = valid_timestamps
                oldest = valid_timestamps[0]
                retry_after = max(1, int(window_seconds - (now - oldest)))
                return False, retry_after

            # Enforce capacity bound before creating new key
            if key not in self._records and len(self._records) >= self.max_entries:
                self._evict_lru_if_needed()

            valid_timestamps.append(now)
            self._records[key] = valid_timestamps
            return True, 0

    def clear(self):
        """Clears all records for test isolation."""
        with self._lock:
            self._records.clear()
            self._last_cleanup = time.time()


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Applies configurable rate limiting across API endpoints.
    Protects compute-intensive endpoints (like /api/v1/chat) from abuse.
    NOTE: In-memory sliding window rate limiting is per-process and not shared across distributed replicas.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.RATE_LIMIT_ENABLED or request.url.path.startswith("/api/v1/health") or request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path

        # Determine rate limit bucket
        if "/chat" in path or "/discovery" in path:
            bucket = "chat_heavy"
            limit = settings.RATE_LIMIT_CHAT_PER_MINUTE
        else:
            bucket = "general"
            limit = settings.RATE_LIMIT_DEFAULT_PER_MINUTE

        allowed, retry_after = rate_limiter.is_allowed(client_ip, bucket, limit, window_seconds=60)
        if not allowed:
            req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {path} (Bucket: {bucket})")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after), "X-Request-ID": req_id},
                content={
                    "detail": f"Too many requests. Rate limit exceeded for this endpoint. Please try again in {retry_after} seconds.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after_seconds": retry_after,
                    "request_id": req_id
                }
            )

        return await call_next(request)
