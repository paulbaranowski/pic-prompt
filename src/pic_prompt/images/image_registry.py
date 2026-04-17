from typing import Dict, List, Optional
from pic_prompt.images.image_data import ImageData
from pic_prompt.images.image_loader import ImageLoader
from pic_prompt.images.errors import ImageSourceError, ImageDownloadError
from pic_prompt.utils.logger import setup_logger

logger = setup_logger(__name__)


class ImageRegistry:
    """In-memory store mapping image paths (URL, local path, or S3 URI) to ImageData
    objects. Tracks whether any registered image is local (flag set at add time, not
    download time). Provides download_image_data() and download_image_data_async() to
    hydrate registered paths into binary data via ImageLoader."""

    def __init__(self):
        self.image_data: Dict[str, ImageData] = {}
        self.image_downloader = ImageLoader()
        self._has_local_images = False

    def add_image_path(self, image_path: str):
        self.image_data[image_path] = ImageData(image_path)
        self._has_local_images = (
            self._has_local_images or self.image_data[image_path].is_local_image()
        )

    def add_image_data(self, image_data: ImageData):
        if image_data.image_path is None:
            raise ValueError("Cannot register ImageData without an image_path")
        self.image_data[image_data.image_path] = image_data
        self._has_local_images = self._has_local_images or image_data.is_local_image()

    def add_provider_encoded_image(
        self, image_path: str, provider_name: str, encoded_image: str
    ):
        self.image_data[image_path].add_provider_encoded_image(
            provider_name, encoded_image
        )

    def num_images(self) -> int:
        return len(self.image_data)

    def get_binary_data(self, image_path: str) -> Optional[bytes]:
        return self.image_data[image_path].binary_data

    def get_all_image_data(self) -> List[ImageData]:
        return list(self.image_data.values())

    def get_all_image_paths(self) -> List[str]:
        return list(self.image_data.keys())

    def get_image_data(self, image_path: str) -> Optional[ImageData]:
        return self.image_data.get(image_path)

    def has_image(self, image_path: str) -> bool:
        return image_path in self.image_data

    def has_local_images(self) -> bool:
        return self._has_local_images

    def clear(self):
        self.image_data = {}
        self._has_local_images = False

    def __repr__(self) -> str:
        return f"ImageRegistry(image_data={self.image_data})"

    def download_image_data(
        self, downloader: Optional[ImageLoader] = None, raise_on_error: bool = True
    ) -> "ImageRegistry":
        """
        Downloads images if needed and stores them in the image registry.

        Args:
            downloader: Optional ImageLoader instance for testing. Uses self.image_downloader if None.
            raise_on_error: Whether to raise an exception on download errors

        Returns:
            ImageRegistry: The registry containing all downloaded image data

        Raises:
            ImageDownloadError: If any critical image downloads fail and raise_on_error is True
        """
        if self.num_images() > 0:
            downloader = downloader or self.image_downloader

            errors = []

            for image_data in self.get_all_image_data():
                if image_data.binary_data is not None:
                    continue
                path = image_data.image_path
                if path is None:
                    continue
                try:
                    logger.info(f"Downloading image {path}")
                    image_data = downloader.download(path)
                    self.add_image_data(image_data)
                except ImageSourceError as e:
                    errors.append((path, str(e)))

            if errors:
                error_messages = "\n".join(
                    f"- {path}: {error}" for path, error in errors
                )
                if raise_on_error:
                    raise ImageDownloadError(
                        f"Failed to download images:\n{error_messages}"
                    )
                else:
                    print(f"Failed to download images:\n{error_messages}")
                    return self
        return self

    async def download_image_data_async(self, downloader: Optional[ImageLoader] = None) -> "ImageRegistry":
        """
        Asynchronously downloads images if needed and stores them in the image registry.

        Args:
            downloader: Optional ImageLoader instance for testing. Uses self.image_downloader if None.

        Returns:
            ImageRegistry: The registry containing all downloaded image data
        """
        if self.num_images() > 0:
            downloader = downloader or self.image_downloader

            for image_data in self.get_all_image_data():
                if image_data.binary_data is not None:
                    continue
                path = image_data.image_path
                if path is None:
                    continue
                try:
                    image_data = await downloader.download_async(path)
                    # replace the old image data with the new one
                    self.add_image_data(image_data)
                except ImageSourceError as e:
                    print(f"Error downloading image {path}: {e}")
        return self
