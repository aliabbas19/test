"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Remove entries older than 1 minute"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 60  # 1 minute ago
        for ip in list(self.requests.keys()):
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if req_time > cutoff_time
            ]
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = current_time
    
    def is_allowed(self, ip: str) -> Tuple[bool, int]:
        """
        Check if request is allowed
        Returns: (is_allowed, remaining_requests)
        """
        self._cleanup_old_entries()
        
        current_time = time.time()
        cutoff_time = current_time - 60  # 1 minute ago
        
        # Filter requests within the last minute
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.requests[ip]) >= self.requests_per_minute:
            remaining = 0
            return False, remaining
        
        # Add current request
        self.requests[ip].append(current_time)
        remaining = self.requests_per_minute - len(self.requests[ip])
        
        return True, remaining
    
    def get_remaining(self, ip: str) -> int:
        """Get remaining requests for an IP"""
        self._cleanup_old_entries()
        current_time = time.time()
        cutoff_time = current_time - 60
        
        self.requests[ip] = [
            req_time for req_time in self.requests[ip]
            if req_time > cutoff_time
        ]
        
        return max(0, self.requests_per_minute - len(self.requests[ip]))


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not is_allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "Retry-After": "60"
            }
        )
    
    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response

