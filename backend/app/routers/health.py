from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
import redis
import logging
from datetime import datetime

from ..database import get_db
from ..dependencies import get_redis_connection
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "alt-audit-api"
    }


@router.get("/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """
    Detailed health check including database and Redis connectivity.
    
    Args:
        db: Database session
        redis_conn: Redis connection
        
    Returns:
        dict: Detailed health status
        
    Raises:
        HTTPException: If any service is unhealthy
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "alt-audit-api",
        "checks": {}
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check Redis connectivity
    try:
        redis_conn.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Check configuration
    try:
        health_status["checks"]["configuration"] = {
            "status": "healthy",
            "message": "Configuration loaded successfully",
            "details": {
                "environment": settings.environment,
                "debug": settings.debug,
                "database_url_configured": bool(settings.database_url),
                "redis_url_configured": bool(settings.redis_url),
                "secret_key_configured": bool(settings.secret_key)
            }
        }
    except Exception as e:
        logger.error(f"Configuration health check failed: {str(e)}")
        health_status["checks"]["configuration"] = {
            "status": "unhealthy",
            "message": f"Configuration check failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Return appropriate status code
    if health_status["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
    
    return health_status


@router.get("/ready")
async def readiness_check(
    db: Session = Depends(get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """
    Readiness check for Kubernetes/container orchestration.
    
    Args:
        db: Database session
        redis_conn: Redis connection
        
    Returns:
        dict: Readiness status
        
    Raises:
        HTTPException: If service is not ready
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))
        
        # Check Redis
        redis_conn.ping()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not_ready",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/live")
async def liveness_check():
    """
    Liveness check for Kubernetes/container orchestration.
    
    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running"
    }
