from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..dependencies import CurrentUser, DatabaseSession
from .. import schemas, models
from ..services.scanner import URLScanner
from ..services.export import DataExporter
from ..utils.exceptions import ValidationError, SecurityError, ScanError
from ..utils.validators import validate_url_safe
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scans", tags=["scans"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=schemas.ScanResultResponse)
@limiter.limit("10/minute")
async def create_scan(
    request: Request,
    scan_data: schemas.ScanResultCreate,
    current_user: CurrentUser,
    db: DatabaseSession,
    response: Response
):
    """
    Create a new URL scan and return results immediately.
    
    Args:
        scan_data: Scan creation data
        current_user: Current authenticated user
        db: Database session
        response: FastAPI response object
        
    Returns:
        ScanResultResponse: Scan result with analysis (201 Created on success)
        
    Raises:
        HTTPException: If scan creation fails (400, 403, 422, 500)
    """
    try:
        # Check if user has reached scan limit
        from ..dependencies import check_user_scan_limit
        check_user_scan_limit(current_user, db)
        
        # Validate URL
        validated_url = validate_url_safe(scan_data.url)
        logger.info(f"Starting scan for URL: {validated_url}")
        
        # Run scan directly
        async with URLScanner() as scanner:
            results = await scanner.scan_url(validated_url)
        
        # Create scan record in database with results
        db_scan = models.ScanResult(
            url=validated_url,
            user_id=current_user.id,
            scan_status=results['scan_status'],
            total_images=results['total_images'],
            images_with_alt=results['images_with_alt'],
            images_missing_alt=results['images_missing_alt'],
            scan_duration_ms=results['scan_duration_ms'],
            error_message=results.get('error_message')
        )
        
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        # Save image details
        for img_data in results.get('images', []):
            image_detail = models.ImageDetail(
                scan_result_id=db_scan.id,
                image_url=img_data['url'],
                alt_text=img_data['alt_text'],
                has_alt_text=img_data['has_alt_text'],
                alt_text_length=img_data['alt_text_length'],
                image_width=img_data.get('width'),
                image_height=img_data.get('height'),
                is_decorative=img_data['is_decorative']
            )
            db.add(image_detail)
        
        db.commit()
        
        logger.info(f"Completed scan {db_scan.id} for user {current_user.id}: {results['total_images']} images, "
                   f"{results['coverage_percentage']:.1f}% coverage")
        
        response.status_code = status.HTTP_201_CREATED
        return schemas.ScanResultResponse.from_orm(db_scan)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL: {str(e)}"
        )
    except SecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"URL not allowed: {str(e)}"
        )
    except ScanError as e:
        logger.error(f"Scan error for URL {scan_data.url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Scan failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scan"
        )


@router.get("/", response_model=List[schemas.ScanResultSummary])
async def get_user_scans(
    current_user: CurrentUser,
    db: DatabaseSession,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, description="Filter by scan status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter")
):
    """
    Get user's scan results with pagination and filtering.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Number of records to return
        status_filter: Optional status filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        List[ScanResultSummary]: List of scan results
    """
    try:
        query = db.query(models.ScanResult).filter(models.ScanResult.user_id == current_user.id)
        
        # Apply filters
        if status_filter:
            query = query.filter(models.ScanResult.scan_status == status_filter)
        if start_date:
            query = query.filter(models.ScanResult.created_at >= start_date)
        if end_date:
            query = query.filter(models.ScanResult.created_at <= end_date)
        
        # Apply pagination and ordering
        scans = query.order_by(models.ScanResult.created_at.desc()).offset(skip).limit(limit).all()
        
        return [schemas.ScanResultSummary.from_orm(scan) for scan in scans]
        
    except Exception as e:
        logger.error(f"Error getting user scans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scans"
        )


@router.get("/{scan_id}", response_model=schemas.ScanResultResponse)
async def get_scan(
    scan_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Get a specific scan result.
    
    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ScanResultResponse: Scan result details
        
    Raises:
        HTTPException: If scan not found or access denied
    """
    try:
        scan = db.query(models.ScanResult).filter(
            models.ScanResult.id == scan_id,
            models.ScanResult.user_id == current_user.id
        ).first()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        return schemas.ScanResultResponse.from_orm(scan)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan"
        )


@router.get("/{scan_id}/images", response_model=List[schemas.ImageDetailResponse])
async def get_scan_images(
    scan_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Number of records to return"),
    has_alt_only: Optional[bool] = Query(None, description="Filter by alt text presence")
):
    """
    Get images from a specific scan.
    
    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session
        skip: Number of records to skip
        limit: Number of records to return
        has_alt_only: Filter by alt text presence
        
    Returns:
        List[ImageDetailResponse]: List of image details
        
    Raises:
        HTTPException: If scan not found or access denied
    """
    try:
        # Verify scan ownership
        scan = db.query(models.ScanResult).filter(
            models.ScanResult.id == scan_id,
            models.ScanResult.user_id == current_user.id
        ).first()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        # Query images
        query = db.query(models.ImageDetail).filter(models.ImageDetail.scan_result_id == scan_id)
        
        if has_alt_only is not None:
            query = query.filter(models.ImageDetail.has_alt_text == has_alt_only)
        
        images = query.order_by(models.ImageDetail.created_at.asc()).offset(skip).limit(limit).all()
        
        return [schemas.ImageDetailResponse.from_orm(img) for img in images]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting scan images for {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scan images"
        )


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Delete a scan result.
    
    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If scan not found or access denied
    """
    try:
        scan = db.query(models.ScanResult).filter(
            models.ScanResult.id == scan_id,
            models.ScanResult.user_id == current_user.id
        ).first()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        # Delete associated image details first
        db.query(models.ImageDetail).filter(models.ImageDetail.scan_result_id == scan_id).delete()
        
        # Delete scan
        db.delete(scan)
        db.commit()
        
        logger.info(f"Deleted scan {scan_id} for user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scan"
        )


@router.post("/{scan_id}/retry", response_model=schemas.ScanResultResponse)
@limiter.limit("5/minute")
async def retry_scan(
    request: Request,
    scan_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
    response: Response
):
    """
    Retry a failed scan and return results immediately.
    
    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session
        response: FastAPI response object
        
    Returns:
        ScanResultResponse: Updated scan result with analysis (200 OK on success)
        
    Raises:
        HTTPException: If scan not found or retry fails (400, 403, 404, 422, 500)
    """
    try:
        scan = db.query(models.ScanResult).filter(
            models.ScanResult.id == scan_id,
            models.ScanResult.user_id == current_user.id
        ).first()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        if scan.scan_status not in ["failed", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only retry failed or pending scans"
            )
        
        # Validate URL
        validated_url = validate_url_safe(scan.url)
        logger.info(f"Retrying scan {scan_id} for URL: {validated_url}")
        
        # Run scan directly
        async with URLScanner() as scanner:
            results = await scanner.scan_url(validated_url)
        
        # Update scan with results
        scan.scan_status = results['scan_status']
        scan.total_images = results['total_images']
        scan.images_with_alt = results['images_with_alt']
        scan.images_missing_alt = results['images_missing_alt']
        scan.scan_duration_ms = results['scan_duration_ms']
        scan.error_message = results.get('error_message')
        
        # Clear existing image details
        db.query(models.ImageDetail).filter(models.ImageDetail.scan_result_id == scan_id).delete()
        
        # Save new image details
        for img_data in results.get('images', []):
            image_detail = models.ImageDetail(
                scan_result_id=scan_id,
                image_url=img_data['url'],
                alt_text=img_data['alt_text'],
                has_alt_text=img_data['has_alt_text'],
                alt_text_length=img_data['alt_text_length'],
                image_width=img_data.get('width'),
                image_height=img_data.get('height'),
                is_decorative=img_data['is_decorative']
            )
            db.add(image_detail)
        
        db.commit()
        
        logger.info(f"Completed retry scan {scan_id}: {results['total_images']} images, "
                   f"{results['coverage_percentage']:.1f}% coverage")
        
        response.status_code = status.HTTP_200_OK
        return schemas.ScanResultResponse.from_orm(scan)
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL: {str(e)}"
        )
    except SecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"URL not allowed: {str(e)}"
        )
    except ScanError as e:
        logger.error(f"Scan error for URL {scan.url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Scan failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error retrying scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry scan"
        )


