from typing import Dict, Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from math import sqrt
from prompt_any.core.errors import ImageProcessingError
from prompt_any.utils.logger import setup_logger
from prompt_any.images.sources.local_file_source import LocalFileSource
import base64

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

    def resample_image(self) -> bytes:
        """Resample image data using LANCZOS resampling."""
        # Open image from bytes
        bytes_io = BytesIO(self.binary_data)
        img = Image.open(bytes_io)

        # Save with LANCZOS resampling
        output = BytesIO()
        img.save(
            output,
            format=img.format,
            quality=60,
            optimize=True,
            resampling=Image.Resampling.LANCZOS,
        )

        self.binary_data = output.getvalue()
        return self.binary_data

    def resize(self, max_size: int = 5_000_000) -> bytes:
        """Resize image data."""
        print(f"[ImageData] Resizing image to max size {max_size}")

        print(
            f"[ImageData] Original dimensions: {self.image_obj.size[0]}x{self.image_obj.size[1]}"
        )

        scale = sqrt(max_size / self.image_obj.size[0] * self.image_obj.size[1])
        new_width = int(self.image_obj.size[0] * scale)
        new_height = int(self.image_obj.size[1] * scale)

        print(f"[ImageData] Target dimensions: {new_width}x{new_height}")

        self.image_obj.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)
        print(
            f"[ImageData] Final dimensions: {self.image_obj.size[0]}x{self.image_obj.size[1]}"
        )

        output = BytesIO()
        self.image_obj.save(output, format=self.image_obj.format)
        resized_bytes = output.getvalue()
        self.binary_data = resized_bytes
        print(f"[ImageData] Final size: {len(resized_bytes)} bytes")

        return resized_bytes

    def encode_as_base64(self, provider_name: str = "openai") -> bytes:
        if self.binary_data is not None:
            encoded_data = base64.b64encode(self.binary_data).decode("utf-8")
            self.add_provider_encoded_image(provider_name, encoded_data)
            return encoded_data
        return None

    def resize_and_encode(self, max_size: int, provider_name: str = "openai") -> str:
        """
        Resize and encode an image to meet provider size requirements.

        This method will attempt to reduce the image size while maintaining quality:
        1. First tries base64 encoding the original image
        2. If too large, resamples using LANCZOS and re-encodes
        3. If still too large, resizes dimensions and re-encodes

        The encoded image data is stored in the ImageData object for later use.

        Args:
            max_size (int): Maximum allowed size in bytes for the encoded image
            provider_name (str): Name of the provider to store encoded data for

        Returns:
            ImageData: Self reference with encoded versions stored
        """
        logger.info(f"Encoding image data for {self.image_path}")
        encoded_data = self.encode_as_base64(provider_name)
        if encoded_data is not None and len(encoded_data) > max_size:
            logger.info(
                f"Encoded data is too large({len(encoded_data)} bytes) for {self.image_path}. Resampling..."
            )
            self.binary_data = self.resample_image()
            encoded_data = self.encode_as_base64(provider_name)
            logger.info(f"Encoded data after resampling: {len(encoded_data)} bytes")
            # if that didn't work, try resizing
            if encoded_data is not None and len(encoded_data) > max_size:
                logger.info(
                    f"Encoded data is still too large for {self.image_path}. Resizing..."
                )
                self.binary_data = self.resize(max_size)
                encoded_data = self.encode_as_base64(provider_name)
                logger.info(f"Encoded data after resizing: {len(encoded_data)} bytes")
        return self
