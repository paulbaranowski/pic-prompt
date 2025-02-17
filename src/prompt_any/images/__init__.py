"""
Images module for prompt_any.

This module provides functionality for image handling including:
- ImageHandler for processing images.
- ImageSourceError for image-specific errors.

The sources subpackage contains implementations for different image sources:
    LocalFileSource, HttpSource, S3Source, etc.
"""

from prompt_any.images.image_downloader import ImageDownloader
from prompt_any.images.errors import ImageSourceError

__all__ = [
    "ImageDownloader",
    "ImageSourceError",
] 