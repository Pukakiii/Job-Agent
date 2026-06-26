import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter for auth endpoints."""

    def __init__(self, app, *, limit: int = 30, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/api/v1/auth"):
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window_start = now - self.window_seconds
        self._hits[client] = [t for t in self._hits[client] if t >= window_start]

        if len(self._hits[client]) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many authentication attempts. Try again later."},
            )

        self._hits[client].append(now)
        return await call_next(request)
