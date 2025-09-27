"""Custom exceptions for the application."""


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class SecurityError(Exception):
    """Raised when security check fails."""
    pass


class ScanError(Exception):
    """Raised when scan operation fails."""
    pass


class ImageAnalysisError(Exception):
    """Raised when image analysis fails."""
    pass
