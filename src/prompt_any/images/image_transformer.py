"""Image transformer module."""

from io import BytesIO
from PIL import Image


class ImageTransformer:
    @staticmethod
    def resample_image(image_data: bytes) -> bytes:
        """Resample image data using LANCZOS resampling."""
        # Open image from bytes
        img = Image.open(BytesIO(image_data))

        # Save with LANCZOS resampling
        output = BytesIO()
        img.save(
            output,
            format=img.format,
            quality=60,
            optimize=True,
            resampling=Image.Resampling.LANCZOS,
        )

        return output.getvalue()
