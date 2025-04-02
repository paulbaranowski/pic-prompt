from abc import ABC, abstractmethod


class ImageSource(ABC):
    """
    Abstract base class for all image sources.

    All image source classes should inherit from this class and implement the following methods:
      - get_image: Download an image synchronously.
      - get_image_async: Download an image asynchronously.
      - can_handle: Determine if the source can handle the provided URL/path.
    """

    @abstractmethod
    def get_source_type(self) -> str:
        """
        Get the type of the source.
        """
        pass

    @abstractmethod
    def get_image(self, url: str) -> bytes:
        """
        Download an image synchronously.

        Args:
            url (str): The URL or path of the image.

        Returns:
            bytes: The raw image data.
        """
        pass

    @abstractmethod
    async def get_image_async(self, url: str) -> bytes:
        """
        Download an image asynchronously.

        Args:
            url (str): The URL or path of the image.

        Returns:
            bytes: The raw image data.
        """
        pass

    @abstractmethod
    def can_handle(self, path: str) -> bool:
        """
        Check if this image source can handle the given URL/path.

        Args:
            path (str): The URL or path of the image.

        Returns:
            bool: True if the source can handle the image, False otherwise.
        """
        pass

    @abstractmethod
    def get_media_type(self, path: str) -> str:
        """
        Get the media type of the image.
        """
        pass
