from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
import logging

from ..dependencies import CurrentUser, DatabaseSession
from ..services.export import DataExporter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/scans/{scan_id}/details/csv")
async def export_scan_details_csv(
    scan_id: int,
    current_user: CurrentUser,
    db: DatabaseSession
):
    """
    Export detailed image information for a specific scan as CSV.
    
    Args:
        scan_id: Scan ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Response: CSV file download
        
    Raises:
        HTTPException: If scan not found or access denied
    """
    try:
        # Verify scan ownership
        from .. import models
        scan = db.query(models.ScanResult).filter(
            models.ScanResult.id == scan_id,
            models.ScanResult.user_id == current_user.id
        ).first()
        
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scan not found"
            )
        
        exporter = DataExporter(db)
        csv_content = exporter.export_scan_details_csv(scan_id)
        
        filename = f"scan_details_{scan_id}_{scan.url.replace('/', '_').replace(':', '_')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting scan details CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export scan details"
        )
