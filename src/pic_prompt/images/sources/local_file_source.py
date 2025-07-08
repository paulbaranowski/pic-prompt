"""
LocalFileSource - Loads images from the local filesystem.
"""

import asyncio
import mimetypes
from pic_prompt.images.sources.image_source import ImageSource
from pic_prompt.images.errors import (
    ImageSourceError,
)  # Ensure this error class exists in errors.py


class LocalFileSource(ImageSource):
    """Loads images from the local filesystem"""

    def get_source_type(self) -> str:
        """
        Get the type of the source.
        """
        return "file"

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

        For local files, we assume any path that does not contain a URI scheme
        (i.e. does not match the pattern <prefix>://).

        Args:
            path (str): The path or URI to check.

        Returns:
            bool: True if the file is a local file, False otherwise.
        """
        return path is not None and path != "" and "://" not in path

    def get_media_type(self, path: str) -> str:
        """
        Get the media type of the image.
        """
        return mimetypes.guess_type(path)[0]
