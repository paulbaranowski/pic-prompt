"""
Loads images from S3.
"""

from typing import Tuple
import mimetypes
from pic_prompt.images.sources.image_source import ImageSource
from pic_prompt.images.errors import ImageSourceError


class S3Source(ImageSource):
    """Loads images from S3"""

    def __init__(self, s3_client, timeout: int = 30) -> None:
        """
        Initialize the S3Source.

        Args:
            s3_client: A client capable of interacting with S3 (synchronous and/or asynchronous).
            timeout (int): Timeout value in seconds.
        """
        self.s3_client = s3_client
        self.timeout = timeout

    def get_source_type(self) -> str:
        """
        Get the type of the source.
        """
        return "s3"

    def get_image(self, s3_uri: str) -> bytes:
        """
        Download image from S3 synchronously.

        Args:
            s3_uri (str): The S3 URI (e.g., "s3://bucket/key").

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If downloading the image fails.
        """
        try:
            bucket, key = self._parse_s3_uri(s3_uri)
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            raise ImageSourceError(f"Failed to download {s3_uri}: {e}")

    async def get_image_async(self, s3_uri: str) -> bytes:
        """
        Download image from S3 asynchronously.

        Args:
            s3_uri (str): The S3 URI (e.g., "s3://bucket/key").

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If downloading the image fails.
        """
        try:
            bucket, key = self._parse_s3_uri(s3_uri)
            response = await self.s3_client.get_object(Bucket=bucket, Key=key)
            return await response["Body"].read()
        except Exception as e:
            raise ImageSourceError(f"Failed to download {s3_uri}: {e}")

    def can_handle(self, path: str) -> bool:
        """
        Check if this source can handle the given path.

        Args:
            path (str): The URI to check.

        Returns:
            bool: True if the path starts with 's3://', False otherwise.
        """
        return path.startswith("s3://")

    def _parse_s3_uri(self, uri: str) -> Tuple[str, str]:
        """
        Parse an S3 URI into its bucket and key components.

        Args:
            uri (str): The S3 URI (e.g., "s3://bucket/key").

        Returns:
            Tuple[str, str]: A tuple containing the bucket and key.

        Raises:
            ImageSourceError: If the URI is not in a valid format.
        """
        parts = uri.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            raise ImageSourceError(f"Invalid S3 URI: {uri}")
        return parts[0], parts[1]

    def get_media_type(self, path: str) -> str:
        """
        Get the media type of the image.
        """
        return mimetypes.guess_type(path)[0]
