import logging
import time
from typing import Dict, Optional, Tuple
import httpx

from ..utils.validators import validate_url_safe, validate_content_safe
from ..utils.exceptions import ScanError, ValidationError, SecurityError
from .image_analyzer import ImageAnalyzer
from ..config import settings

logger = logging.getLogger(__name__)


class URLScanner:
    """URL scanner service for fetching and analyzing web content."""
    
    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        """
        Initialize URL scanner.
        
        Args:
            timeout: Request timeout in seconds
            max_redirects: Maximum number of redirects to follow
        """
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            max_redirects=self.max_redirects,
            headers={
                'User-Agent': 'Alt-Audit-Scanner/1.0 (https://alt-audit.com)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    async def scan_url(self, url: str) -> Dict[str, any]:
        """
        Scan a URL and analyze its images.
        
        Args:
            url: URL to scan
            
        Returns:
            Dict: Scan results including image analysis
            
        Raises:
            ValidationError: If URL is invalid
            SecurityError: If URL poses security risk
            ScanError: If scan operation fails
        """
        start_time = time.time()
        
        try:
            # Validate URL
            validated_url = validate_url_safe(url)
            logger.info(f"Starting scan for URL: {validated_url}")
            
            # Fetch content
            content, content_type = await self._fetch_content(validated_url)
            
            # Validate content
            validated_content = validate_content_safe(content, content_type)
            
            # Analyze images
            analyzer = ImageAnalyzer(validated_url, self.timeout)
            analysis_results = analyzer.analyze_images(validated_content.decode('utf-8', errors='ignore'))
            
            # Calculate scan duration
            scan_duration_ms = int((time.time() - start_time) * 1000)
            
            # Prepare results
            results = {
                'url': validated_url,
                'total_images': analysis_results['total_images'],
                'images_with_alt': analysis_results['images_with_alt'],
                'images_missing_alt': analysis_results['images_missing_alt'],
                'decorative_images': analysis_results['decorative_images'],
                'coverage_percentage': analysis_results['coverage_percentage'],
                'quality_breakdown': analysis_results['quality_breakdown'],
                'scan_duration_ms': scan_duration_ms,
                'scan_status': 'completed',
                'error_message': None,
                'images': analysis_results['images']
            }
            
            logger.info(f"Scan completed for {validated_url}: {analysis_results['total_images']} images, "
                       f"{analysis_results['coverage_percentage']:.1f}% coverage")
            
            return results
            
        except ValidationError as e:
            logger.warning(f"Validation error for URL {url}: {str(e)}")
            return self._create_error_result(url, 'validation_error', str(e), start_time)
            
        except SecurityError as e:
            logger.warning(f"Security error for URL {url}: {str(e)}")
            return self._create_error_result(url, 'security_error', str(e), start_time)
            
        except ScanError as e:
            logger.error(f"Scan error for URL {url}: {str(e)}")
            return self._create_error_result(url, 'scan_error', str(e), start_time)
            
        except Exception as e:
            logger.error(f"Unexpected error scanning URL {url}: {str(e)}")
            return self._create_error_result(url, 'unexpected_error', str(e), start_time)
    
    async def _fetch_content(self, url: str) -> Tuple[bytes, str]:
        """
        Fetch content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Tuple[bytes, str]: (content, content_type)
            
        Raises:
            ScanError: If fetch fails
        """
        if not self.client:
            raise ScanError("Scanner not initialized. Use async context manager.")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith(('text/html', 'text/plain', 'application/xhtml+xml')):
                raise ScanError(f"Unsupported content type: {content_type}")
            
            # Check content size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > settings.max_scan_duration_seconds * 1024 * 1024:
                raise ScanError("Content too large")
            
            return response.content, content_type
            
        except httpx.TimeoutException:
            raise ScanError("Request timeout")
        except httpx.HTTPStatusError as e:
            raise ScanError(f"HTTP error {e.response.status_code}: {e.response.reason_phrase}")
        except httpx.RequestError as e:
            raise ScanError(f"Request error: {str(e)}")
        except Exception as e:
            raise ScanError(f"Unexpected error fetching content: {str(e)}")
    
    def _create_error_result(self, url: str, error_type: str, error_message: str, start_time: float) -> Dict[str, any]:
        """
        Create error result dictionary.
        
        Args:
            url: Original URL
            error_type: Type of error
            error_message: Error message
            start_time: Scan start time
            
        Returns:
            Dict: Error result
        """
        scan_duration_ms = int((time.time() - start_time) * 1000)
        
        return {
            'url': url,
            'total_images': 0,
            'images_with_alt': 0,
            'images_missing_alt': 0,
            'decorative_images': 0,
            'coverage_percentage': 0.0,
            'quality_breakdown': {},
            'scan_duration_ms': scan_duration_ms,
            'scan_status': 'failed',
            'error_message': f"{error_type}: {error_message}",
            'images': []
        }
