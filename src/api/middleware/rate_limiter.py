from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits = defaultdict(list)  # IP -> list of request timestamps
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))  # requests per window
        self.window_size = int(os.getenv("RATE_LIMIT_WINDOW_SIZE", "3600"))  # window size in seconds
        self.cleanup_interval = 3600  # cleanup old entries every hour
        asyncio.create_task(self._cleanup_task())

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":  # Don't rate limit health checks
            return await call_next(request)

        client_ip = request.client.host
        now = datetime.now()

        # Remove old timestamps
        self.rate_limits[client_ip] = [
            ts for ts in self.rate_limits[client_ip]
            if now - ts < timedelta(seconds=self.window_size)
        ]

        # Check rate limit
        if len(self.rate_limits[client_ip]) >= self.max_requests:
            oldest_allowed_time = now - timedelta(seconds=self.window_size)
            if self.rate_limits[client_ip][0] > oldest_allowed_time:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )

        # Add current request
        self.rate_limits[client_ip].append(now)

        # Add rate limit headers to response
        response = await call_next(request)
        remaining = self.max_requests - len(self.rate_limits[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=self.window_size)).timestamp()))

        return response

    async def _cleanup_task(self):
        while True:
            await asyncio.sleep(self.cleanup_interval)
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window_size)
            
            # Clean up old entries
            for ip in list(self.rate_limits.keys()):
                self.rate_limits[ip] = [
                    ts for ts in self.rate_limits[ip]
                    if ts > cutoff
                ]
                if not self.rate_limits[ip]:
                    del self.rate_limits[ip]
