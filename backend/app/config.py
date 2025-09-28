from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://alt_audit_user:alt_audit_password@localhost:5432/alt_audit"
    )
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "your-secret-key-change-in-production"
    )
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # API
    api_v1_str: str = os.getenv("API_V1_STR", "/api/v1")
    project_name: str = os.getenv("PROJECT_NAME", "Alt Audit")
    
    # Security
    allowed_hosts: str = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        return [host.strip() for host in self.allowed_hosts.split(',')]
    
    # CORS
    backend_cors_origins: str = os.getenv(
        "BACKEND_CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:3001"
    )
    
    @property
    def backend_cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(',')]
    
    # Frontend
    react_app_api_url: str = os.getenv("REACT_APP_API_URL", "http://localhost:8000")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # URL Scanner
    max_url_length: int = int(os.getenv("MAX_URL_LENGTH", "2048"))
    max_scan_duration_seconds: int = int(os.getenv("MAX_SCAN_DURATION_SECONDS", "300"))  # 5 minutes
    max_images_per_scan: int = int(os.getenv("MAX_IMAGES_PER_SCAN", "1000"))
    request_timeout_seconds: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    
    # Allowed domains for scanning (empty list means all domains allowed)
    allowed_domains: List[str] = []
    
    # Blocked domains for security
    blocked_domains: List[str] = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "169.254.169.254",  # AWS metadata
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()
