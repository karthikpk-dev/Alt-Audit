import re
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from ..utils.exceptions import ImageAnalysisError

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Simple and efficient image analyzer for alt text accessibility."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize image analyzer."""
        self.base_url = base_url
        self.parsed_base_url = urlparse(base_url)
    
    def analyze_images(self, html_content: str) -> Dict[str, any]:
        """Analyze all images in HTML content."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            images = []
            
            # Extract img tags
            for img in soup.find_all('img'):
                if src := img.get('src'):
                    images.append(self._create_image_data(img, src, 'img'))
            
            # Extract CSS background images
            for element in soup.find_all(attrs={'style': True}):
                for url in self._extract_css_urls(element.get('style', '')):
                    images.append(self._create_image_data(element, url, 'css'))
            
            return self._calculate_stats(images)
            
        except Exception as e:
            logger.error(f"Error analyzing images: {str(e)}")
            raise ImageAnalysisError(f"Failed to analyze images: {str(e)}")
    
    def _create_image_data(self, element, src: str, source_type: str) -> Dict:
        """Create image data dictionary."""
        alt_text = element.get('alt', '') if source_type == 'img' else ''
        has_alt = bool(alt_text and alt_text.strip())
        is_decorative = alt_text.strip() == '' or source_type == 'css'
        alt_length = len(alt_text.strip()) if alt_text else 0
        
        return {
            'url': self._resolve_url(src),
            'alt_text': alt_text,
            'has_alt_text': has_alt,
            'is_decorative': is_decorative,
            'alt_text_length': alt_length,
            'source': source_type,
            'width': self._safe_int(element.get('width')),
            'height': self._safe_int(element.get('height'))
        }
    
    def _extract_css_urls(self, css: str) -> List[str]:
        """Extract URLs from CSS background-image."""
        pattern = r'background-image\s*:\s*url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        return re.findall(pattern, css, re.IGNORECASE)
    
    def _resolve_url(self, url: str) -> str:
        """Resolve relative URL to absolute."""
        if url.startswith(('http://', 'https://')):
            return url
        if url.startswith('//'):
            return f"{self.parsed_base_url.scheme}:{url}"
        if url.startswith('/'):
            return f"{self.parsed_base_url.scheme}://{self.parsed_base_url.netloc}{url}"
        return urljoin(self.base_url, url)
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert to int."""
        try:
            return int(value) if value else None
        except (ValueError, TypeError):
            return None
    
    def _calculate_stats(self, images: List[Dict]) -> Dict:
        """Calculate analysis statistics."""
        total = len(images)
        with_alt = sum(1 for img in images if img['has_alt_text'])
        decorative = sum(1 for img in images if img['is_decorative'])
        
        return {
            'total_images': total,
            'images_with_alt': with_alt,
            'images_missing_alt': total - with_alt,
            'decorative_images': decorative,
            'coverage_percentage': round((with_alt / total * 100) if total > 0 else 0, 2),
            'images': images
        }
