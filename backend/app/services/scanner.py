import logging
import time
import asyncio
import httpx
from typing import Dict, Tuple

from ..utils.validators import validate_url_safe
from ..utils.exceptions import ScanError, ValidationError, SecurityError
from .image_analyzer import ImageAnalyzer
from ..config import settings

logger = logging.getLogger(__name__)


class URLScanner:
    """Simple URL scanner with httpx and curl fallback for SSL issues."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def scan_url(self, url: str) -> Dict[str, any]:
        """Scan a URL and analyze its images."""
        start_time = time.time()
        
        try:
            # Validate and fetch content
            validated_url = validate_url_safe(url)
            content = await self._fetch_content(validated_url)
            
            # Analyze images
            analyzer = ImageAnalyzer(validated_url, self.timeout)
            results = analyzer.analyze_images(content.decode('utf-8', errors='ignore'))
            
            # Add metadata
            results.update({
                'url': validated_url,
                'scan_duration_ms': int((time.time() - start_time) * 1000),
                'scan_status': 'completed',
                'error_message': None
            })
            
            logger.info(f"Scan completed: {results['total_images']} images, {results['coverage_percentage']:.1f}% coverage")
            return results
            
        except Exception as e:
            logger.error(f"Scan failed for {url}: {str(e)}")
            return self._create_error_result(url, str(e), start_time)
    
    async def _fetch_content(self, url: str) -> bytes:
        """Fetch content using httpx, fallback to curl for SSL issues."""
        try:
            # Try httpx first (works for most URLs)
            response = await self.client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            # Fallback to curl for SSL-problematic sites
            if "SSL" in str(e) or "TLS" in str(e):
                logger.warning(f"SSL error with httpx, trying curl for {url}")
                return await self._fetch_with_curl(url)
            raise ScanError(f"Failed to fetch content: {str(e)}")
    
    async def _fetch_with_curl(self, url: str) -> bytes:
        """Fallback method using curl for SSL issues."""
        curl_cmd = [
            'curl', '-L', '--max-time', str(self.timeout), '--insecure', '--compressed',
            '--user-agent', 'Mozilla/5.0 (compatible; Alt-Audit-Scanner/1.0)',
            '--header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            '--dump-header', '-', '--output', '-', url
        ]
        
        process = await asyncio.create_subprocess_exec(
            *curl_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise ScanError(f"Curl failed: {stderr.decode()}")
        
        # Parse headers and body
        output = stdout.decode('utf-8', errors='ignore')
        if '\r\n\r\n' in output:
            _, body = output.split('\r\n\r\n', 1)
            return body.encode('utf-8')
        elif '\n\n' in output:
            _, body = output.split('\n\n', 1)
            return body.encode('utf-8')
        else:
            return stdout
    
    def _create_error_result(self, url: str, error_message: str, start_time: float) -> Dict[str, any]:
        """Create error result dictionary."""
        return {
            'url': url,
            'total_images': 0,
            'images_with_alt': 0,
            'images_missing_alt': 0,
            'decorative_images': 0,
            'coverage_percentage': 0.0,
            'quality_breakdown': {},
            'scan_duration_ms': int((time.time() - start_time) * 1000),
            'scan_status': 'failed',
            'error_message': str(error_message),
            'images': []
        }
