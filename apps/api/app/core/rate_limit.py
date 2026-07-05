"""Rate limiting configuration."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

def get_remote_address_with_fallback(request: Request) -> str:
    """Get remote address with fallback for proxy scenarios."""
    # Check for forwarded headers (behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return get_remote_address(request)

limiter = Limiter(key_func=get_remote_address_with_fallback, default_limits=["100/minute"])

__all__ = ["limiter", "get_remote_address_with_fallback"]
