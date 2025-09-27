from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import logging

from ..dependencies import CurrentUser, DatabaseSession
from .. import schemas, models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(
    current_user: CurrentUser,
    db: DatabaseSession,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
):
    """
    Get analytics summary for the user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        days: Number of days to analyze
        
    Returns:
        AnalyticsSummary: Analytics summary data
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get scan statistics
        scans_query = db.query(models.ScanResult).filter(
            models.ScanResult.user_id == current_user.id,
            models.ScanResult.created_at >= start_date,
            models.ScanResult.scan_status == "completed"
        )
        
        total_scans = scans_query.count()
        
        # Get aggregated statistics
        stats = db.query(
            func.sum(models.ScanResult.total_images).label('total_images'),
            func.sum(models.ScanResult.images_with_alt).label('images_with_alt'),
            func.sum(models.ScanResult.images_missing_alt).label('images_missing_alt')
        ).filter(
            models.ScanResult.user_id == current_user.id,
            models.ScanResult.created_at >= start_date,
            models.ScanResult.scan_status == "completed"
        ).first()
        
        total_images = stats.total_images or 0
        total_images_with_alt = stats.images_with_alt or 0
        total_images_missing_alt = stats.images_missing_alt or 0
        
        # Calculate average coverage
        if total_images > 0:
            average_coverage = (total_images_with_alt / total_images) * 100
        else:
            average_coverage = 0.0
        
        # Get most common issues
        common_issues = get_common_issues(db, current_user.id, start_date)
        
        return schemas.AnalyticsSummary(
            total_scans=total_scans,
            total_images_scanned=total_images,
            total_images_with_alt=total_images_with_alt,
            total_images_missing_alt=total_images_missing_alt,
            average_coverage_percentage=round(average_coverage, 2),
            most_common_issues=common_issues
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics summary"
        )


@router.get("/trends", response_model=List[dict])
async def get_coverage_trends(
    current_user: CurrentUser,
    db: DatabaseSession,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    group_by: str = Query("day", description="Group by day, week, or month")
):
    """
    Get coverage trends over time.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        days: Number of days to analyze
        group_by: Group by day, week, or month
        
    Returns:
        List[dict]: Trend data
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Determine date grouping (PostgreSQL format)
        if group_by == "week":
            date_format = "YYYY-\"W\"WW"  # Year-Week
        elif group_by == "month":
            date_format = "YYYY-MM"  # Year-Month
        else:  # day
            date_format = "YYYY-MM-DD"  # Year-Month-Day
        
        # Query trends data
        trends_query = db.query(
            func.to_char(models.ScanResult.created_at, date_format).label('period'),
            func.count(models.ScanResult.id).label('scans'),
            func.sum(models.ScanResult.total_images).label('total_images'),
            func.sum(models.ScanResult.images_with_alt).label('images_with_alt'),
            func.sum(models.ScanResult.images_missing_alt).label('images_missing_alt')
        ).filter(
            models.ScanResult.user_id == current_user.id,
            models.ScanResult.created_at >= start_date,
            models.ScanResult.scan_status == "completed"
        ).group_by('period').order_by('period')
        
        trends = trends_query.all()
        
        # Format results
        trend_data = []
        for trend in trends:
            total_images = trend.total_images or 0
            images_with_alt = trend.images_with_alt or 0
            
            if total_images > 0:
                coverage_percentage = (images_with_alt / total_images) * 100
            else:
                coverage_percentage = 0.0
            
            trend_data.append({
                'period': trend.period,
                'scans': trend.scans,
                'total_images': total_images,
                'images_with_alt': images_with_alt,
                'images_missing_alt': trend.images_missing_alt or 0,
                'coverage_percentage': round(coverage_percentage, 2)
            })
        
        return trend_data
        
    except Exception as e:
        logger.error(f"Error getting coverage trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve coverage trends"
        )


@router.get("/top-issues", response_model=List[dict])
async def get_top_issues(
    current_user: CurrentUser,
    db: DatabaseSession,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Number of issues to return")
):
    """
    Get top accessibility issues.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        days: Number of days to analyze
        limit: Number of issues to return
        
    Returns:
        List[dict]: Top issues data
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get scan IDs in date range
        scan_ids = select(models.ScanResult.id).where(
            models.ScanResult.user_id == current_user.id,
            models.ScanResult.created_at >= start_date,
            models.ScanResult.scan_status == "completed"
        )
        
        # Analyze image issues
        issues = []
        
        # Missing alt text
        missing_alt_count = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.has_alt_text == False,
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if missing_alt_count > 0:
            issues.append({
                'issue': 'Missing alt text',
                'count': missing_alt_count,
                'severity': 'high',
                'description': 'Images without alt text that are not decorative'
            })
        
        # Empty alt text (not decorative)
        empty_alt_count = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.alt_text == '',
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if empty_alt_count > 0:
            issues.append({
                'issue': 'Empty alt text',
                'count': empty_alt_count,
                'severity': 'medium',
                'description': 'Images with empty alt text that should have descriptions'
            })
        
        # Very short alt text
        short_alt_count = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.has_alt_text == True,
            models.ImageDetail.alt_text_length < 5,
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if short_alt_count > 0:
            issues.append({
                'issue': 'Very short alt text',
                'count': short_alt_count,
                'severity': 'medium',
                'description': 'Images with alt text shorter than 5 characters'
            })
        
        # Very long alt text
        long_alt_count = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.has_alt_text == True,
            models.ImageDetail.alt_text_length > 125,
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if long_alt_count > 0:
            issues.append({
                'issue': 'Very long alt text',
                'count': long_alt_count,
                'severity': 'low',
                'description': 'Images with alt text longer than 125 characters'
            })
        
        # Sort by count and return top issues
        issues.sort(key=lambda x: x['count'], reverse=True)
        return issues[:limit]
        
    except Exception as e:
        logger.error(f"Error getting top issues: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top issues"
        )






def get_common_issues(db: Session, user_id: int, start_date: datetime) -> List[str]:
    """
    Get most common accessibility issues.
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Start date for analysis
        
    Returns:
        List[str]: List of common issues
    """
    issues = []
    
    try:
        # Get scan IDs in date range
        scan_ids = select(models.ScanResult.id).where(
            models.ScanResult.user_id == user_id,
            models.ScanResult.created_at >= start_date,
            models.ScanResult.scan_status == "completed"
        )
        
        # Check for missing alt text
        missing_alt = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.has_alt_text == False,
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if missing_alt > 0:
            issues.append(f"{missing_alt} images missing alt text")
        
        # Check for empty alt text
        empty_alt = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.alt_text == '',
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if empty_alt > 0:
            issues.append(f"{empty_alt} images with empty alt text")
        
        # Check for very short alt text
        short_alt = db.query(func.count(models.ImageDetail.id)).filter(
            models.ImageDetail.scan_result_id.in_(scan_ids),
            models.ImageDetail.has_alt_text == True,
            models.ImageDetail.alt_text_length < 5,
            models.ImageDetail.is_decorative == False
        ).scalar() or 0
        
        if short_alt > 0:
            issues.append(f"{short_alt} images with very short alt text")
        
    except Exception as e:
        logger.error(f"Error getting common issues: {str(e)}")
    
    return issues[:5]  # Return top 5 issues


