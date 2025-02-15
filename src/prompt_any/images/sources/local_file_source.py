"""
LocalFileSource - Loads images from the local filesystem.
"""

import os
import asyncio
from prompt_any.images.sources.image_source import ImageSource
from prompt_any.images.errors import ImageSourceError  # Ensure this error class exists in errors.py


class LocalFileSource(ImageSource):
    """Loads images from the local filesystem"""

    def get_image(self, path: str) -> bytes:
        """Read image file from disk synchronously.

        Args:
            path (str): The local file path to the image.

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If the file cannot be read.
        """
        try:
            with open(path, "rb") as f:
                return f.read()
        except IOError as e:
            raise ImageSourceError(f"Failed to read {path}: {e}")

    async def get_image_async(self, path: str) -> bytes:
        """Read image file from disk asynchronously.

        Args:
            path (str): The local file path to the image.

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If the file cannot be read.
        """
        try:
            return await asyncio.to_thread(self.get_image, path)
        except IOError as e:
            raise ImageSourceError(f"Failed to read {path}: {e}")

    def can_handle(self, path: str) -> bool:
        """Check if this source can handle the given path.

        For local files, we assume any path that does not start with a remote URI (http://, https://, s3://)
        is handled by this source.

        Args:
            path (str): The path or URI to check.

        Returns:
            bool: True if the file is a local file, False otherwise.
        """
        return not (path.startswith("http://") or path.startswith("https://") or path.startswith("s3://")) 