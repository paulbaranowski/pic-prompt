"""
Main class for handling image operations.
"""

from typing import Dict, Union
import asyncio

from prompt_any.images.sources.base import ImageSource
from prompt_any.core.errors import ImageProcessingError
from prompt_any.providers.base import ProviderHelper


class ImageHandler:
    """Main class for handling image operations."""

    def __init__(self) -> None:
        """Initialize the ImageHandler with an empty dictionary of registered sources."""
        self.sources: Dict[str, ImageSource] = {}

    def register_source(self, protocol: str, source: ImageSource) -> None:
        """
        Register an image source for a given protocol.

        Args:
            protocol (str): The protocol identifier (e.g., "http", "https", "s3", "file").
            source (ImageSource): The image source instance to register.
        """
        self.sources[protocol] = source

    def _get_source_for_path(self, path: str) -> ImageSource:
        """
        Determine which registered image source can handle the given path.

        Iterates over all registered sources and returns the first one that can handle the path.

        Args:
            path (str): The path or URL to the image.

        Returns:
            ImageSource: The image source capable of handling the path.

        Raises:
            ImageProcessingError: If no registered source can handle the given path.
        """
        for source in self.sources.values():
            if source.can_handle(path):
                return source
        raise ImageProcessingError(f"No registered image source can handle path: {path}")

    def process_image(self, path: str, provider_helper: ProviderHelper) -> Union[str, bytes]:
        """
        Process an image synchronously.

        This method retrieves the image from the appropriate source based on the path and then uses the
        provider helper's encoding method to return the processed image (e.g., encoded as base64 if required).

        Args:
            path (str): The path or URI to the image.
            provider_helper (ProviderHelper): The provider helper dictating the image encoding requirements.

        Returns:
            Union[str, bytes]: The processed (encoded) image data.
        """
        source = self._get_source_for_path(path)
        try:
            image_data = source.get_image(path)
            return provider_helper.encode_image(image_data)
        except Exception as e:
            raise ImageProcessingError(f"Error processing image '{path}': {e}")

    async def process_image_async(self, path: str, provider_helper: ProviderHelper) -> Union[str, bytes]:
        """
        Process an image asynchronously.

        This method retrieves the image asynchronously from the appropriate source and then uses the provider helper
        to encode the image data.

        Args:
            path (str): The path or URI to the image.
            provider_helper (ProviderHelper): The provider helper dictating the image encoding requirements.

        Returns:
            Union[str, bytes]: The processed (encoded) image data.
        """
        source = self._get_source_for_path(path)
        try:
            image_data = await source.get_image_async(path)
            return provider_helper.encode_image(image_data)
        except Exception as e:
            raise ImageProcessingError(f"Error processing image '{path}': {e}") 