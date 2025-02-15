"""
Loads images from HTTP(S) URLs.
"""

import requests
import aiohttp
from prompt_any.images.sources.base import ImageSource
from prompt_any.images.errors import ImageSourceError


class HttpSource(ImageSource):
    """
    Loads images from HTTP(S) URLs.

    If no HTTP client is provided, a default aiohttp.ClientSession is created.
    """

    def __init__(self, async_http_client: aiohttp.ClientSession = None, timeout: int = 30) -> None:
        self.async_http_client = async_http_client or aiohttp.ClientSession()
        self.timeout = timeout

    def get_image(self, url: str) -> bytes:
        """
        Download image synchronously using requests.

        Args:
            url (str): The URL to the image.

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If the image cannot be downloaded.
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code != 200:
                raise ImageSourceError(f"HTTP {response.status_code}: {url}")
            return response.content
        except Exception as e:
            raise ImageSourceError(f"Failed to download {url}: {e}")

    async def get_image_async(self, url: str) -> bytes:
        """
        Download image from URL asynchronously using aiohttp.

        Args:
            url (str): The URL to the image.

        Returns:
            bytes: The raw image data.

        Raises:
            ImageSourceError: If the image cannot be downloaded.
        """
        try:
            async with self.async_http_client.get(url, timeout=self.timeout) as response:
                if response.status != 200:
                    raise ImageSourceError(f"HTTP {response.status}: {url}")
                return await response.read()
        except Exception as e:
            raise ImageSourceError(f"Failed to download {url}: {e}")

    def can_handle(self, path: str) -> bool:
        """
        Check if this source can handle the given URL.

        Args:
            path (str): The URL to check.

        Returns:
            bool: True if the URL starts with 'http://' or 'https://', otherwise False.
        """
        return path.startswith("http://") or path.startswith("https://") 