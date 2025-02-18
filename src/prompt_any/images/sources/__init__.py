"""
Image Sources module for prompt_any.

This module re-exports the image source classes:
    - ImageSource: The abstract base class.
    - LocalFileSource: Loads images from the local filesystem.
    - HttpSource: Loads images from HTTP(S) URLs.
    - S3Source: Loads images from S3.
"""

from prompt_any.images.sources.image_source import ImageSource
from prompt_any.images.sources.local_file_source import LocalFileSource
from prompt_any.images.sources.http_source import HttpSource
from prompt_any.images.sources.s3_source import S3Source

__all__ = [
    "ImageSource",
    "LocalFileSource",
    "HttpSource",
    "S3Source",
]
