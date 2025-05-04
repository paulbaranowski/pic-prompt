"""
Image handler module.
"""

import boto3

from typing import Dict, Union, Optional
from pic_prompt.images.sources.image_source import ImageSource
from pic_prompt.core.errors import ImageProcessingError
from pic_prompt.images.sources.local_file_source import LocalFileSource
from pic_prompt.images.sources.http_source import HttpSource
from pic_prompt.images.sources.s3_source import S3Source
from pic_prompt.images.image_data import ImageData
from pic_prompt.core.image_config import ImageConfigRegistry


class ImageLoader:
    """Main class for handling image operations."""

    def __init__(self, s3_client: Optional[boto3.client] = None) -> None:
        """Initialize the ImageLoader with built-in image sources.

        Automatically registers local file, HTTP/HTTPS, and optionally S3 sources.

        Args:
            s3_client (Optional[boto3.client]): AWS S3 client for S3 source registration.
                If provided, enables S3 image loading capabilities.
        """
        self.sources: Dict[str, ImageSource] = {}
        self.image_config_registry = ImageConfigRegistry()
        # Automatically register built-in image sources:
        # Register local and HTTP sources
        self.register_source("file", LocalFileSource())
        self.register_source("http", HttpSource())
        self.register_source("https", HttpSource())
        # Register S3 source only if an S3 client is provided.
        if s3_client is not None:
            self.register_source("s3", S3Source(s3_client))

    @staticmethod
    def fetch(image_path: str) -> ImageData:
        """Static method to create a new instance and download an image.

        A convenience method that creates a new ImageLoader instance and downloads
        the image in one step.

        Args:
            image_path (str): The path or URL to the image to download.

        Returns:
            ImageData: The downloaded image data.
        """
        loader = ImageLoader()
        return loader.download(image_path)

    def register_source(self, protocol: str, source: ImageSource) -> None:
        """
        Register an image source for a given protocol.

        Args:
            protocol (str): The protocol identifier (e.g., "http", "https", "s3", "file").
            source (ImageSource): The image source instance to register.
        """
        self.sources[protocol] = source

    def get_source(self, protocol: str) -> ImageSource:
        """
        Get the registered image source for a given protocol.

        Args:
            protocol (str): The protocol identifier (e.g., "http", "https", "s3", "file").

        Returns:
            ImageSource: The registered image source for the given protocol.

        Raises:
            ImageProcessingError: If no registered source is found for the given protocol.
        """
        return self.sources[protocol]

    def get_source_for_path(self, path: str) -> ImageSource:
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
        raise ImageProcessingError(
            f"No registered image source can handle path: {path}"
        )

    def is_media_type_supported(self, provider_name: str) -> bool:
        """
        Check if the media type is supported by the image config registry.
        """
        return (
            self.media_type
            in self.image_config_registry.get_config(provider_name).supported_formats
        )

    def download(self, path: str) -> ImageData:
        """
        Download and process an image synchronously.

        This method retrieves the image from the appropriate source based on the path.
        It returns an ImageData object containing the binary data and media type.

        Args:
            path (str): The path or URI to the image.

        Returns:
            ImageData: Object containing the image binary data, media type and original path.

        Raises:
            ImageProcessingError: If there is an error downloading or processing the image.
        """
        source = self.get_source_for_path(path)
        binary_data = source.get_image(path)
        media_type = source.get_media_type(path)
        image_data = ImageData(
            image_path=path, binary_data=binary_data, media_type=media_type
        )
        return image_data

    def download_and_encode(
        self, path: str, provider_name: str = "openai"
    ) -> ImageData:
        image_data = self.download(path)
        config = self.image_config_registry.get_config(provider_name)
        image_data.resize_and_encode(config.max_size, provider_name)
        return image_data

    async def download_async(self, path: str) -> ImageData:
        """
        Download and process an image asynchronously.

        This method retrieves the image asynchronously from the appropriate source based on the path.
        It returns an ImageData object containing the binary data and media type.

        Args:
            path (str): The path or URI to the image.

        Returns:
            ImageData: Object containing the image binary data, media type and original path.

        Raises:
            ImageProcessingError: If there is an error downloading or processing the image.
        """
        source = self.get_source_for_path(path)
        binary_data = await source.get_image_async(path)
        media_type = source.get_media_type(path)
        return ImageData(
            image_path=path, binary_data=binary_data, media_type=media_type
        )
