import re
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, Tag

from ..utils.exceptions import ImageAnalysisError

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Analyze images and their alt text attributes."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize image analyzer.
        
        Args:
            base_url: Base URL for resolving relative image URLs
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.parsed_base_url = urlparse(base_url)
    
    def extract_images_from_html(self, html_content: str) -> List[Dict[str, any]]:
        """
        Extract all images from HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            List[Dict]: List of image information dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            images = []
            
            # Find all img tags
            img_tags = soup.find_all('img')
            
            for img_tag in img_tags:
                image_info = self._analyze_image_tag(img_tag)
                if image_info:
                    images.append(image_info)
            
            # Find images in CSS background-image properties
            css_images = self._extract_css_images(html_content)
            images.extend(css_images)
            
            return images
            
        except Exception as e:
            logger.error(f"Error extracting images from HTML: {str(e)}")
            raise ImageAnalysisError(f"Failed to extract images: {str(e)}")
    
    def _analyze_image_tag(self, img_tag: Tag) -> Optional[Dict[str, any]]:
        """
        Analyze a single img tag.
        
        Args:
            img_tag: BeautifulSoup img tag
            
        Returns:
            Dict: Image information or None if invalid
        """
        try:
            # Get image source
            src = img_tag.get('src')
            if not src:
                return None
            
            # Resolve relative URLs
            image_url = self._resolve_url(src)
            
            # Get alt text
            alt_text = img_tag.get('alt', '')
            
            # Analyze alt text
            alt_analysis = self._analyze_alt_text(alt_text)
            
            # Get other attributes
            width = img_tag.get('width')
            height = img_tag.get('height')
            title = img_tag.get('title', '')
            
            # Convert dimensions to integers if possible
            try:
                width = int(width) if width else None
            except (ValueError, TypeError):
                width = None
            
            try:
                height = int(height) if height else None
            except (ValueError, TypeError):
                height = None
            
            return {
                'url': image_url,
                'alt_text': alt_text,
                'title': title,
                'width': width,
                'height': height,
                'has_alt_text': alt_analysis['has_alt_text'],
                'is_decorative': alt_analysis['is_decorative'],
                'alt_text_length': alt_analysis['alt_text_length'],
                'alt_text_quality': alt_analysis['quality'],
                'tag_name': 'img',
                'attributes': dict(img_tag.attrs)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing img tag: {str(e)}")
            return None
    
    def _extract_css_images(self, html_content: str) -> List[Dict[str, any]]:
        """
        Extract images from CSS background-image properties.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            List[Dict]: List of CSS image information
        """
        images = []
        
        try:
            # Find style attributes and style tags
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find elements with style attributes
            styled_elements = soup.find_all(attrs={'style': True})
            
            for element in styled_elements:
                style = element.get('style', '')
                css_images = self._parse_css_background_images(style)
                
                for css_image in css_images:
                    css_image['tag_name'] = element.name
                    css_image['element_attributes'] = dict(element.attrs)
                    images.append(css_image)
            
            # Find style tags
            style_tags = soup.find_all('style')
            for style_tag in style_tags:
                if style_tag.string:
                    css_images = self._parse_css_background_images(style_tag.string)
                    for css_image in css_images:
                        css_image['tag_name'] = 'style'
                        css_image['source'] = 'css'
                        images.append(css_image)
        
        except Exception as e:
            logger.error(f"Error extracting CSS images: {str(e)}")
        
        return images
    
    def _parse_css_background_images(self, css_content: str) -> List[Dict[str, any]]:
        """
        Parse CSS content for background-image properties.
        
        Args:
            css_content: CSS content to parse
            
        Returns:
            List[Dict]: List of CSS image information
        """
        images = []
        
        # Regex to find background-image URLs
        pattern = r'background-image\s*:\s*url\s*\(\s*["\']?([^"\')\s]+)["\']?\s*\)'
        matches = re.findall(pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            try:
                image_url = self._resolve_url(match)
                
                # CSS images typically don't have alt text
                alt_analysis = self._analyze_alt_text('')
                
                images.append({
                    'url': image_url,
                    'alt_text': '',
                    'title': '',
                    'width': None,
                    'height': None,
                    'has_alt_text': False,
                    'is_decorative': True,  # CSS images are typically decorative
                    'alt_text_length': 0,
                    'alt_text_quality': 'none',
                    'source': 'css_background'
                })
                
            except Exception as e:
                logger.error(f"Error parsing CSS image URL: {str(e)}")
                continue
        
        return images
    
    def _analyze_alt_text(self, alt_text: str) -> Dict[str, any]:
        """
        Analyze alt text quality and characteristics.
        
        Args:
            alt_text: Alt text to analyze
            
        Returns:
            Dict: Alt text analysis results
        """
        if not alt_text:
            return {
                'has_alt_text': False,
                'is_decorative': False,
                'alt_text_length': 0,
                'quality': 'missing'
            }
        
        # Check if it's decorative (empty alt text)
        if alt_text.strip() == '':
            return {
                'has_alt_text': True,
                'is_decorative': True,
                'alt_text_length': 0,
                'quality': 'decorative'
            }
        
        # Analyze quality
        quality = self._assess_alt_text_quality(alt_text)
        
        return {
            'has_alt_text': True,
            'is_decorative': False,
            'alt_text_length': len(alt_text.strip()),
            'quality': quality
        }
    
    def _assess_alt_text_quality(self, alt_text: str) -> str:
        """
        Assess the quality of alt text.
        
        Args:
            alt_text: Alt text to assess
            
        Returns:
            str: Quality assessment ('excellent', 'good', 'poor', 'spam')
        """
        alt_text = alt_text.strip()
        
        # Check for spam patterns
        spam_patterns = [
            r'click here',
            r'read more',
            r'learn more',
            r'image',
            r'picture',
            r'photo',
            r'img\d+',
            r'\.jpg',
            r'\.png',
            r'\.gif',
            r'\.webp',
        ]
        
        for pattern in spam_patterns:
            if re.search(pattern, alt_text, re.IGNORECASE):
                return 'spam'
        
        # Check length
        if len(alt_text) < 5:
            return 'poor'
        elif len(alt_text) < 20:
            return 'good'
        elif len(alt_text) > 125:
            return 'poor'  # Too long
        else:
            return 'excellent'
    
    def _resolve_url(self, url: str) -> str:
        """
        Resolve relative URL to absolute URL.
        
        Args:
            url: URL to resolve
            
        Returns:
            str: Absolute URL
        """
        if url.startswith(('http://', 'https://')):
            return url
        
        if url.startswith('//'):
            return f"{self.parsed_base_url.scheme}:{url}"
        
        if url.startswith('/'):
            return f"{self.parsed_base_url.scheme}://{self.parsed_base_url.netloc}{url}"
        
        return urljoin(self.base_url, url)
    
    def analyze_images(self, html_content: str) -> Dict[str, any]:
        """
        Analyze all images in HTML content.
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dict: Analysis results
        """
        try:
            images = self.extract_images_from_html(html_content)
            
            # Calculate statistics
            total_images = len(images)
            images_with_alt = sum(1 for img in images if img['has_alt_text'])
            images_missing_alt = total_images - images_with_alt
            decorative_images = sum(1 for img in images if img['is_decorative'])
            
            # Quality breakdown
            quality_breakdown = {}
            for img in images:
                quality = img['alt_text_quality']
                quality_breakdown[quality] = quality_breakdown.get(quality, 0) + 1
            
            # Calculate coverage percentage
            coverage_percentage = (images_with_alt / total_images * 100) if total_images > 0 else 0
            
            return {
                'total_images': total_images,
                'images_with_alt': images_with_alt,
                'images_missing_alt': images_missing_alt,
                'decorative_images': decorative_images,
                'coverage_percentage': round(coverage_percentage, 2),
                'quality_breakdown': quality_breakdown,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"Error analyzing images: {str(e)}")
            raise ImageAnalysisError(f"Failed to analyze images: {str(e)}")
