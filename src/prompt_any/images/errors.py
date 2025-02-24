"""
Image-specific errors for the prompt_any library.
"""


class ImageSourceError(Exception):
    """Base exception for image source errors."""

    pass


class ImageDownloadError(Exception):
    """Raised when there are errors downloading one or more images"""

    pass
