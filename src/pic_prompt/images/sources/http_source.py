"""
Loads images from HTTP(S) URLs.
"""

import requests
import aiohttp
import mimetypes
from pic_prompt.images.sources.image_source import ImageSource
from pic_prompt.images.errors import ImageSourceError


class HttpSource(ImageSource):
    """
    Loads images from HTTP(S) URLs.

    If no HTTP client is provided, a default aiohttp.ClientSession is created.
    """

    def __init__(
        self, async_http_client: aiohttp.ClientSession = None, timeout: int = 30
    ) -> None:
        # Lazy initialization: do not create a ClientSession unless async calls are made
        self.async_http_client = async_http_client
        self.timeout = timeout
        # Default headers to help with rate limiting and server policies
        self.headers = {"User-Agent": "pic-prompt/1.0"}

    def get_source_type(self) -> str:
        """
        Get the type of the source.
        """
        return "http"

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
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            if response.status_code == 403:
                raise ImageSourceError(
                    f"Access forbidden (HTTP 403) for {url}. The server may require authentication or have rate limiting."
                )
            elif response.status_code == 404:
                raise ImageSourceError(
                    f"Image not found (HTTP 404) for {url}. The requested resource does not exist."
                )
            elif response.status_code != 200:
                raise ImageSourceError(f"HTTP {response.status_code}: {url}")
            return response.content
        except ImageSourceError as e:
            raise e
        except requests.exceptions.RequestException as e:
            raise ImageSourceError(f"Network error downloading {url}: {e}")
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
        # Lazy initialization of async_http_client
        if self.async_http_client is None:
            self.async_http_client = aiohttp.ClientSession(headers=self.headers)

        try:
            async with self.async_http_client.get(
                url, timeout=self.timeout
            ) as response:
                if response.status == 403:
                    raise ImageSourceError(
                        f"Access forbidden (HTTP 403) for {url}. The server may require authentication or have rate limiting."
                    )
                elif response.status == 404:
                    raise ImageSourceError(
                        f"Image not found (HTTP 404) for {url}. The requested resource does not exist."
                    )
                elif response.status != 200:
                    raise ImageSourceError(f"HTTP {response.status}: {url}")
                return await response.read()
        except ImageSourceError as e:
            raise e
        except aiohttp.ClientError as e:
            raise ImageSourceError(f"Network error downloading {url}: {e}")

    def can_handle(self, path: str) -> bool:
        """
        Check if this source can handle the given URL.

        Args:
            path (str): The URL to check.

        Returns:
            bool: True if the URL starts with 'http://' or 'https://', otherwise False.
        """
        return path.startswith("http://") or path.startswith("https://")

    def get_media_type(self, path: str) -> str:
        """
        Get the media type of the image.
        """
        return mimetypes.guess_type(path)[0]
