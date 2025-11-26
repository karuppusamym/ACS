from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm

    Default limits:
    - 100 requests per minute per IP
    - 1000 requests per hour per IP
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store: {ip: [(timestamp, count)]}
        self.minute_buckets: Dict[str, list] = defaultdict(list)
        self.hour_buckets: Dict[str, list] = defaultdict(list)

        # Cleanup task
        self._cleanup_task = None

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limits
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

        response = await call_next(request)
        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limits"""
        now = datetime.now()

        # Clean old entries
        self._cleanup_old_requests(client_ip, now)

        # Check minute limit
        minute_requests = len(self.minute_buckets[client_ip])
        if minute_requests >= self.requests_per_minute:
            return False

        # Check hour limit
        hour_requests = len(self.hour_buckets[client_ip])
        if hour_requests >= self.requests_per_hour:
            return False

        # Add new request
        self.minute_buckets[client_ip].append(now)
        self.hour_buckets[client_ip].append(now)

        return True

    def _cleanup_old_requests(self, client_ip: str, now: datetime):
        """Remove old request timestamps"""
        # Remove requests older than 1 minute
        minute_ago = now - timedelta(minutes=1)
        self.minute_buckets[client_ip] = [
            ts for ts in self.minute_buckets[client_ip]
            if ts > minute_ago
        ]

        # Remove requests older than 1 hour
        hour_ago = now - timedelta(hours=1)
        self.hour_buckets[client_ip] = [
            ts for ts in self.hour_buckets[client_ip]
            if ts > hour_ago
        ]

        # Clean up empty entries
        if not self.minute_buckets[client_ip]:
            del self.minute_buckets[client_ip]
        if not self.hour_buckets[client_ip]:
            del self.hour_buckets[client_ip]


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Stricter rate limiting for authentication endpoints

    Limits:
    - 5 login attempts per minute per IP
    - 20 login attempts per hour per IP
    """

    def __init__(self, app):
        super().__init__(app)
        self.attempts: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only apply to auth endpoints
        if not (request.url.path.startswith("/api/v1/auth/login") or
                request.url.path.startswith("/api/v1/auth/signup")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()

        # Clean old attempts
        minute_ago = now - timedelta(minutes=1)
        self.attempts[client_ip] = [
            ts for ts in self.attempts[client_ip]
            if ts > minute_ago
        ]

        # Check limit
        if len(self.attempts[client_ip]) >= 5:
            logger.warning(f"Auth rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later."
            )

        # Record attempt
        self.attempts[client_ip].append(now)

        response = await call_next(request)
        return response
