import base64
from typing import Dict, Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from math import sqrt
from pic_prompt.core.errors import ImageProcessingError
from pic_prompt.utils.logger import setup_logger
from pic_prompt.images.sources.local_file_source import LocalFileSource
from pic_prompt.images.image_resizer import ImageResizer

logger = setup_logger(__name__)


class ImageData:
    def __init__(
        self, image_path: str, binary_data: bytes = None, media_type: str = None
    ):
        self.image_obj: Image.Image = None
        self.image_path: str = image_path
        self.binary_data: bytes = binary_data
        self.media_type: str = media_type
        self.provider_encoded_images: Dict[str, str] = {}
        self.local_file_source = LocalFileSource()

    def __repr__(self) -> str:
        if len(self.provider_encoded_images) == 0:
            encoded_images = "none"
        else:
            encoded_images = ", ".join(
                [
                    f"{k}: {len(v)} bytes"
                    for k, v in self.provider_encoded_images.items()
                ]
            )
        return f"ImageData(image_path={self.image_path}, binary_data={len(self.binary_data) if self.binary_data else 'none'}, media_type={self.media_type}, is_local={self.is_local_image()}, encoded_images={encoded_images})"

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, value: str):
        self._image_path = value

    def is_local_image(self) -> bool:
        return self.local_file_source.can_handle(self.image_path)

    @property
    def binary_data(self) -> bytes:
        return self._binary_data

    @binary_data.setter
    def binary_data(self, value: bytes):
        if value is not None:
            try:
                bytes_io = BytesIO(value)
                self.image_obj = Image.open(bytes_io)
            except UnidentifiedImageError as e:
                raise ImageProcessingError(
                    f"UnidentifiedImageError opening image: {e}"
                ) from e
            except Exception as e:
                raise ImageProcessingError(
                    f"Unknown exception opening image: {e}"
                ) from e
        self._binary_data = value

    @property
    def media_type(self) -> str:
        return self._media_type

    @media_type.setter
    def media_type(self, value: str):
        self._media_type = value

    def get_dimensions(self) -> tuple[int, int]:
        return self.image_obj.size

    def add_provider_encoded_image(self, provider_name: str, encoded_image: str):
        self.provider_encoded_images[provider_name] = encoded_image

    def get_encoded_data_for(self, provider_name: str = "openai") -> Optional[str]:
        if provider_name not in self.provider_encoded_images:
            raise ValueError(
                f"Encoded data not found for provider {provider_name} in ImageData for {self.image_path}"
            )
        return self.provider_encoded_images.get(provider_name)

    def encode_as_base64(self, provider_name: str = "openai") -> bytes:
        if self.binary_data is not None:
            encoded_data = base64.b64encode(self.binary_data).decode("utf-8")
            self.add_provider_encoded_image(provider_name, encoded_data)
            return encoded_data
        return None

    def resize_and_encode(
        self, max_size: int, provider_name: str = "openai", resizer: ImageResizer = None
    ) -> str:
        """
        Resize and encode an image to meet provider size requirements.

        This method will attempt to reduce the image size while maintaining quality:
        1. First tries with the original image
        2. If too large, resamples using LANCZOS
        3. If still too large, resizes dimensions

        The encoded image data is stored in the ImageData object for later use.

        Args:
            max_size (int): Maximum allowed size in bytes for the binary image data
            provider_name (str): Name of the provider to store encoded data for
            resizer: Optional ImageResizer instance for testing. Creates new one if None.

        Returns:
            ImageData: Self reference with encoded versions stored
        """
        logger.info(f"Processing image data for {self.image_path}")

        resizer = resizer or ImageResizer(target_size=max_size)
        self.binary_data = resizer.resize(self.binary_data)

        # Encode the final binary data
        self.encode_as_base64(provider_name)
        return self
