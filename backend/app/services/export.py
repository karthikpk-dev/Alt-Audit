import csv
import io
import logging
from sqlalchemy.orm import Session

from ..models import ScanResult, ImageDetail

logger = logging.getLogger(__name__)


class DataExporter:
    """Export scan data in various formats."""
    
    def __init__(self, db: Session):
        """
        Initialize data exporter.
        
        Args:
            db: Database session
        """
        self.db = db
    
    
    def export_scan_details_csv(self, scan_id: int) -> str:
        """
        Export detailed image information for a specific scan.
        
        Args:
            scan_id: Scan ID
            
        Returns:
            str: CSV content
        """
        scan = self.db.query(ScanResult).filter(ScanResult.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")
        
        images = self.db.query(ImageDetail).filter(ImageDetail.scan_result_id == scan_id).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Image URL', 'Alt Text', 'Has Alt Text', 'Alt Text Length',
            'Is Decorative', 'Width', 'Height', 'Created At'
        ])
        
        # Write data
        for image in images:
            writer.writerow([
                image.image_url,
                image.alt_text or '',
                image.has_alt_text,
                image.alt_text_length or 0,
                image.is_decorative,
                image.image_width or '',
                image.image_height or '',
                image.created_at.isoformat()
            ])
        
        return output.getvalue()
    
    
    
