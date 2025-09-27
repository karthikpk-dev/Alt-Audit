from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


def create_rate_limiter():
    """Create and configure rate limiter."""
    return limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "retry_after": getattr(exc, 'retry_after', 60)
        }
    )


class SecurityHeadersMiddleware:
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add security headers
                security_headers = {
                    b"x-frame-options": b"SAMEORIGIN",
                    b"x-content-type-options": b"nosniff",
                    b"x-xss-protection": b"1; mode=block",
                    b"referrer-policy": b"strict-origin-when-cross-origin",
                    b"content-security-policy": b"default-src 'self'",
                    b"strict-transport-security": b"max-age=31536000; includeSubDomains",
                }
                
                # Add security headers if not already present
                for header, value in security_headers.items():
                    if header not in headers:
                        headers[header] = value
                
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class RequestLoggingMiddleware:
    """Middleware to log HTTP requests."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                logger.info(
                    f"{scope['method']} {scope['path']} - "
                    f"Status: {message['status']} - "
                    f"Time: {process_time:.4f}s"
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class CORSMiddleware:
    """Custom CORS middleware with security considerations."""
    
    def __init__(self, app, allow_origins=None, allow_methods=None, allow_headers=None):
        self.app = app
        self.allow_origins = allow_origins or settings.backend_cors_origins_list
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                
                # Add CORS headers
                origin = None
                for header_name, header_value in scope.get("headers", []):
                    if header_name == b"origin":
                        origin = header_value.decode()
                        break
                
                if origin and origin in self.allow_origins:
                    headers[b"access-control-allow-origin"] = origin.encode()
                    headers[b"access-control-allow-credentials"] = b"true"
                    headers[b"access-control-allow-methods"] = ", ".join(self.allow_methods).encode()
                    headers[b"access-control-allow-headers"] = ", ".join(self.allow_headers).encode()
                    headers[b"access-control-max-age"] = b"86400"  # 24 hours
                
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


class SSRFProtectionMiddleware:
    """Middleware to protect against Server-Side Request Forgery attacks."""
    
    def __init__(self, app):
        self.app = app
        self.blocked_domains = settings.blocked_domains
        self.allowed_domains = settings.allowed_domains
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Check for URL parameters that might be used for SSRF
        if scope["method"] in ["POST", "PUT", "PATCH"]:
            # This would need to be implemented with request body parsing
            # For now, we'll handle this in the URL scanner service
            pass
        
        await self.app(scope, receive, send)


def create_middleware_stack(app):
    """Create the complete middleware stack."""
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    
    # Add custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CORSMiddleware)
    app.add_middleware(SSRFProtectionMiddleware)
    
    return app
