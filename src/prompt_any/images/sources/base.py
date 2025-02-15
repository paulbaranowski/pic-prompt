"""
Base image source interface for loading images from various sources (local, http, s3, etc).
"""

from abc import ABC, abstractmethod

class ImageSource(ABC):
    """Interface for different image sources (local, http, s3, etc)"""

    @abstractmethod
    def get_image(self, path: str) -> bytes:
        """Retrieve image bytes from the source synchronously.

        Args:
            path (str): The path or URL to the image.

        Returns:
            bytes: The raw image data.
        """
        pass

    @abstractmethod
    async def get_image_async(self, path: str) -> bytes:
        """Retrieve image bytes from the source asynchronously.

        Args:
            path (str): The path or URL to the image.

        Returns:
            bytes: The raw image data.
        """
        pass

    @abstractmethod
    def can_handle(self, path: str) -> bool:
        """Check if this source can handle the given path.

        Args:
            path (str): The path or URL to check.

        Returns:
            bool: True if this source can handle the path, False otherwise.
        """
        pass 