from typing import Dict, Optional
from PIL import Image
from io import BytesIO
from math import sqrt
from prompt_any.core.errors import ImageProcessingError


class ImageData:
    def __init__(
        self, image_path: str, binary_data: bytes = None, media_type: str = None
    ):
        self.image_obj: Image.Image = None
        self.image_path: str = image_path
        self.binary_data: bytes = binary_data
        self.media_type: str = media_type
        self.provider_encoded_images: Dict[str, str] = {}

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
        return f"ImageData(image_path={self.image_path}, binary_data={len(self.binary_data)}, media_type={self.media_type}, encoded_images={encoded_images})"

    @property
    def image_path(self) -> str:
        return self._image_path

    @image_path.setter
    def image_path(self, value: str):
        self._image_path = value

    @property
    def binary_data(self) -> bytes:
        return self._binary_data

    @binary_data.setter
    def binary_data(self, value: bytes):
        if value is not None:
            try:
                self.image_obj = Image.open(BytesIO(value))
            except Exception as e:
                raise ImageProcessingError(f"Error creating image object: {e}") from e
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

    def get_encoded_data_for(self, provider_name: str) -> Optional[str]:
        if provider_name not in self.provider_encoded_images:
            raise ValueError(
                f"Encoded data not found for provider {provider_name} in ImageData for {self.image_path}"
            )
        return self.provider_encoded_images.get(provider_name)

    def resample_image(self) -> bytes:
        """Resample image data using LANCZOS resampling."""
        # Open image from bytes
        img = Image.open(BytesIO(self.binary_data))

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

    def resize(self, max_size: int) -> bytes:
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
