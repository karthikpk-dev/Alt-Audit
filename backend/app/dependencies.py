from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated, Optional
import redis
import json
from datetime import datetime, timedelta

from .database import get_db
from . import auth, models
from .config import settings

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Redis connection for caching
redis_client = None


def get_redis_client():
    """Get Redis client connection."""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check Redis cache first
        redis_client = get_redis_client()
        cache_key = f"user_token:{token}"
        cached_user = redis_client.get(cache_key)
        
        if cached_user:
            user_data = json.loads(cached_user)
            return models.User(**user_data)
        
        # Verify token
        token_data = auth.verify_token(token)
        if token_data.user_id is None:
            raise credentials_exception
        
        # Get user from database
        user = auth.get_user_by_id(db, user_id=token_data.user_id)
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Cache user data for 5 minutes
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        redis_client.setex(cache_key, 300, json.dumps(user_dict, default=str))
        
        return user
    except Exception as e:
        raise credentials_exception


async def get_current_active_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> models.User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[models.User, Depends(get_current_active_user)]
) -> models.User:
    """
    Get current verified user.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Current verified user
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account not verified"
        )
    return current_user


def get_optional_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """
    Get current user if token is provided, otherwise return None.
    
    Args:
        token: Optional JWT access token
        db: Database session
        
    Returns:
        User: Current authenticated user or None
    """
    if not token:
        return None
    
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


def rate_limit_by_user(
    current_user: Annotated[models.User, Depends(get_current_user)]
) -> str:
    """
    Rate limiting key function based on user ID.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        str: Rate limiting key
    """
    return f"user:{current_user.id}"


def rate_limit_by_ip(request) -> str:
    """
    Rate limiting key function based on IP address.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Rate limiting key
    """
    # Get client IP from request
    client_ip = request.client.host
    if hasattr(request, 'headers'):
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
    
    return f"ip:{client_ip}"


def get_user_scans_limit() -> int:
    """
    Get the maximum number of scans per user.
    
    Returns:
        int: Maximum scans per user
    """
    return 100  # Configurable limit


def check_user_scan_limit(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
) -> bool:
    """
    Check if user has reached scan limit.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        bool: True if user can perform more scans
        
    Raises:
        HTTPException: If user has reached scan limit
    """
    from .models import ScanResult
    
    # Count user's scans in the last 24 hours
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    recent_scans = db.query(ScanResult).filter(
        ScanResult.user_id == current_user.id,
        ScanResult.created_at >= yesterday
    ).count()
    
    max_scans = get_user_scans_limit()
    
    if recent_scans >= max_scans:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Scan limit exceeded. Maximum {max_scans} scans per day."
        )
    
    return True


def get_database_session() -> Session:
    """
    Get database session for dependency injection.
    
    Returns:
        Session: Database session
    """
    return next(get_db())


def get_redis_connection():
    """
    Get Redis connection for dependency injection.
    
    Returns:
        Redis: Redis connection
    """
    return get_redis_client()


# Common dependency combinations
CurrentUser = Annotated[models.User, Depends(get_current_user)]
CurrentActiveUser = Annotated[models.User, Depends(get_current_active_user)]
CurrentVerifiedUser = Annotated[models.User, Depends(get_current_verified_user)]
OptionalCurrentUser = Annotated[Optional[models.User], Depends(get_optional_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]
RedisConnection = Annotated[redis.Redis, Depends(get_redis_connection)]
