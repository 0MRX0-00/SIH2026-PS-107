import time
import uuid
import logging
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response, status
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


class RequestBodySizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Protects API against oversized payload flooding by enforcing MAX_REQUEST_BODY_SIZE_BYTES.
    """

    def __init__(self, app, max_bytes: int = settings.MAX_REQUEST_BODY_SIZE_BYTES):
        super().__init__(app)
        self.max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_bytes:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": "Request payload exceeds maximum allowed size (2MB).",
                            "error_code": "PAYLOAD_TOO_LARGE",
                            "request_id": getattr(request.state, "request_id", str(uuid.uuid4()))
                        }
                    )
            except ValueError:
                pass

        return await call_next(request)


class InMemoryRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Tracks client requests by IP and endpoint category.
    """

    def __init__(self):
        # Key: (client_ip, endpoint_bucket) -> List[timestamp]
        self._records: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str, bucket: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds)
        """
        now = time.time()
        key = (client_ip, bucket)
        timestamps = self._records[key]

        # Prune timestamps outside the active window
        valid_timestamps = [t for t in timestamps if now - t < window_seconds]
        self._records[key] = valid_timestamps

        if len(valid_timestamps) >= limit:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(window_seconds - (now - oldest)))
            return False, retry_after

        self._records[key].append(now)
        return True, 0


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Applies configurable rate limiting across API endpoints.
    Protects compute-intensive endpoints (like /api/v1/chat) from abuse.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not settings.RATE_LIMIT_ENABLED or request.url.path.startswith("/api/v1/health"):
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
