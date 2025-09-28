import re
import ipaddress
from urllib.parse import urlparse
from typing import List, Optional, Tuple
import socket
import logging
from .exceptions import ValidationError, SecurityError

logger = logging.getLogger(__name__)


class URLValidator:
    """URL validation and SSRF protection utilities."""
    
    # Private IP ranges and localhost patterns
    PRIVATE_IP_RANGES = [
        ipaddress.IPv4Network('10.0.0.0/8'),
        ipaddress.IPv4Network('172.16.0.0/12'),
        ipaddress.IPv4Network('192.168.0.0/16'),
        ipaddress.IPv4Network('127.0.0.0/8'),
        ipaddress.IPv4Network('169.254.0.0/16'),  # Link-local
        ipaddress.IPv4Network('224.0.0.0/4'),     # Multicast
        ipaddress.IPv4Network('240.0.0.0/4'),     # Reserved
    ]
    
    # IPv6 private ranges
    PRIVATE_IPV6_RANGES = [
        ipaddress.IPv6Network('::1/128'),         # localhost
        ipaddress.IPv6Network('fc00::/7'),        # Unique local
        ipaddress.IPv6Network('fe80::/10'),       # Link-local
    ]
    
    # Blocked protocols
    BLOCKED_PROTOCOLS = ['file', 'ftp', 'gopher', 'jar', 'ldap', 'ldaps', 'mailto', 'netdoc']
    
    # Blocked domains and patterns
    BLOCKED_DOMAINS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        '169.254.169.254',  # AWS metadata
    ]
    
    # Allowed domains (empty means all domains allowed)
    ALLOWED_DOMAINS: List[str] = []
    
    def __init__(self, allowed_domains: Optional[List[str]] = None, blocked_domains: Optional[List[str]] = None):
        """
        Initialize URL validator.
        
        Args:
            allowed_domains: List of allowed domains (empty means all allowed)
            blocked_domains: List of blocked domains
        """
        self.allowed_domains = allowed_domains or self.ALLOWED_DOMAINS
        self.blocked_domains = blocked_domains or self.BLOCKED_DOMAINS
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate URL for security and format.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Basic URL format validation
            if not url or not isinstance(url, str):
                return False, "URL cannot be empty"
            
            if len(url) > 2048:  # RFC 7230 limit
                return False, "URL too long (max 2048 characters)"
            
            # Parse URL
            parsed = urlparse(url)
            
            # Check protocol
            if parsed.scheme.lower() in self.BLOCKED_PROTOCOLS:
                return False, f"Protocol '{parsed.scheme}' is not allowed"
            
            # Only allow HTTP and HTTPS
            if parsed.scheme.lower() not in ['http', 'https']:
                return False, "Only HTTP and HTTPS protocols are allowed"
            
            # Check if URL has netloc (hostname)
            if not parsed.netloc:
                return False, "URL must have a valid hostname"
            
            # Validate hostname
            is_valid_host, host_error = self._validate_hostname(parsed.netloc)
            if not is_valid_host:
                return False, host_error
            
            # Check for suspicious patterns
            if self._has_suspicious_patterns(url):
                return False, "URL contains suspicious patterns"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            return False, "Invalid URL format"
    
    def _validate_hostname(self, hostname: str) -> Tuple[bool, str]:
        """
        Validate hostname for SSRF protection.
        
        Args:
            hostname: Hostname to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Remove port if present
        hostname = hostname.split(':')[0]
        
        # Check blocked domains
        if hostname.lower() in [domain.lower() for domain in self.blocked_domains]:
            return False, f"Domain '{hostname}' is blocked"
        
        # Check allowed domains (if specified)
        if self.allowed_domains:
            if not any(hostname.lower().endswith(domain.lower()) for domain in self.allowed_domains):
                return False, f"Domain '{hostname}' is not in allowed list"
        
        # Check for IP addresses
        if self._is_ip_address(hostname):
            return self._validate_ip_address(hostname)
        
        # Check for valid hostname format
        if not self._is_valid_hostname(hostname):
            return False, "Invalid hostname format"
        
        return True, ""
    
    def _is_ip_address(self, hostname: str) -> bool:
        """Check if hostname is an IP address."""
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            return False
    
    def _validate_ip_address(self, ip: str) -> Tuple[bool, str]:
        """
        Validate IP address for SSRF protection.
        
        Args:
            ip: IP address to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            
            # Check if it's a private IP
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False, f"Private IP address '{ip}' is not allowed"
            
            # Check against blocked ranges
            for network in self.PRIVATE_IP_RANGES:
                if ip_obj in network:
                    return False, f"IP address '{ip}' is in blocked range"
            
            # Check IPv6 ranges
            if ip_obj.version == 6:
                for network in self.PRIVATE_IPV6_RANGES:
                    if ip_obj in network:
                        return False, f"IPv6 address '{ip}' is in blocked range"
            
            return True, ""
            
        except ValueError:
            return False, "Invalid IP address format"
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """
        Check if hostname has valid format.
        
        Args:
            hostname: Hostname to validate
            
        Returns:
            bool: True if valid format
        """
        if len(hostname) > 253:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
            return False
        
        # Check that it doesn't start or end with dot or hyphen
        if hostname.startswith('.') or hostname.endswith('.') or hostname.startswith('-') or hostname.endswith('-'):
            return False
        
        # Check that it has at least one dot (for domain)
        if '.' not in hostname:
            return False
        
        return True
    
    def _has_suspicious_patterns(self, url: str) -> bool:
        """
        Check for suspicious URL patterns.
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if suspicious patterns found
        """
        suspicious_patterns = [
            r'@',  # Username in URL
            r'#',  # Fragment identifier
            r'javascript:',  # JavaScript protocol
            r'data:',  # Data URI
            r'vbscript:',  # VBScript protocol
            r'file:',  # File protocol
            r'ftp:',  # FTP protocol
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def resolve_and_validate(self, url: str) -> Tuple[bool, str, Optional[str]]:
        """
        Resolve URL and validate against SSRF attacks.
        
        Args:
            url: URL to resolve and validate
            
        Returns:
            Tuple[bool, str, Optional[str]]: (is_valid, error_message, resolved_ip)
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.split(':')[0]
            
            # Resolve hostname to IP
            try:
                resolved_ips = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
                for family, _, _, _, sockaddr in resolved_ips:
                    ip = sockaddr[0]
                    is_valid, error = self._validate_ip_address(ip)
                    if not is_valid:
                        return False, f"Resolved IP '{ip}' is not allowed: {error}", ip
                
                # If we get here, all resolved IPs are valid
                return True, "", resolved_ips[0][4][0] if resolved_ips else None
                
            except socket.gaierror:
                return False, f"Could not resolve hostname '{hostname}'", None
                
        except Exception as e:
            logger.error(f"URL resolution error: {str(e)}")
            return False, f"Error resolving URL: {str(e)}", None


def validate_url_safe(url: str) -> str:
    """
    Validate URL and return cleaned version.
    
    Args:
        url: URL to validate
        
    Returns:
        str: Validated and cleaned URL
        
    Raises:
        ValidationError: If URL is invalid
        SecurityError: If URL poses security risk
    """
    validator = URLValidator()
    
    # Basic validation
    is_valid, error = validator.validate_url(url)
    if not is_valid:
        raise ValidationError(f"Invalid URL: {error}")
    
    # SSRF validation
    is_safe, error, resolved_ip = validator.resolve_and_validate(url)
    if not is_safe:
        raise SecurityError(f"URL security check failed: {error}")
    
    # Return cleaned URL
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{'?' + parsed.query if parsed.query else ''}"


