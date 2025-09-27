from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class User(Base):
    """
    User model for authentication and user management.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship to scan results
    scan_results = relationship("ScanResult", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"


class ScanResult(Base):
    """
    Scan result model for storing URL scan data and image analysis results.
    """
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False, index=True)
    total_images = Column(Integer, nullable=False, default=0)
    images_with_alt = Column(Integer, nullable=False, default=0)
    images_missing_alt = Column(Integer, nullable=False, default=0)
    scan_status = Column(String(50), nullable=False, default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    scan_duration_ms = Column(Integer, nullable=True)  # Scan duration in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="scan_results")

    def __repr__(self):
        return f"<ScanResult(id={self.id}, url='{self.url}', total_images={self.total_images})>"

    @property
    def alt_text_coverage_percentage(self) -> float:
        """
        Calculate the percentage of images with alt text.
        Returns 0.0 if no images were found.
        """
        if self.total_images == 0:
            return 0.0
        return round((self.images_with_alt / self.total_images) * 100, 2)

    @property
    def missing_alt_percentage(self) -> float:
        """
        Calculate the percentage of images missing alt text.
        Returns 0.0 if no images were found.
        """
        if self.total_images == 0:
            return 0.0
        return round((self.images_missing_alt / self.total_images) * 100, 2)


class ImageDetail(Base):
    """
    Detailed image information for each image found during scanning.
    This provides granular data about individual images.
    """
    __tablename__ = "image_details"

    id = Column(Integer, primary_key=True, index=True)
    scan_result_id = Column(Integer, ForeignKey("scan_results.id"), nullable=False, index=True)
    image_url = Column(Text, nullable=False)
    alt_text = Column(Text, nullable=True)
    has_alt_text = Column(Boolean, nullable=False, default=False)
    alt_text_length = Column(Integer, nullable=True)  # Length of alt text if present
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    is_decorative = Column(Boolean, nullable=False, default=False)  # True if alt="" (decorative image)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship to scan result
    scan_result = relationship("ScanResult")

    def __repr__(self):
        return f"<ImageDetail(id={self.id}, image_url='{self.image_url}', has_alt_text={self.has_alt_text})>"
