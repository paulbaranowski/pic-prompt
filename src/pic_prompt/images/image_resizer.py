from PIL import Image
import io
from typing import Dict, Any, Tuple


class ImageResizer:
    """A class to resize images to a target size in bytes, only if they exceed it."""

    def __init__(self, target_size: int = 20_000_000, tolerance: int = 500_000):
        """
        Initialize the ImageResizer with target size and tolerance.

        Args:
            target_size (int): Target file size in bytes (default 5MB).
            tolerance (int): Acceptable deviation from target size in bytes (default 0.5MB).
        """
        self.target_size = target_size
        self.tolerance = tolerance

    def get_image_size(self, image_bytes: bytes) -> int:
        """Return the size of the image in bytes."""
        return len(image_bytes)

    def needs_resizing(self, image_bytes: bytes) -> bool:
        """Check if the image exceeds the target size."""
        return self.get_image_size(image_bytes) > self.target_size

    def convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert image to RGB mode if needed."""
        if img.mode in ("RGBA", "P"):
            return img.convert("RGB")
        return img

    def encode_to_jpeg_bytes(self, img: Image.Image, quality: int) -> bytes:
        """
        Save image as JPEG with specified quality.

        Args:
            img: PIL Image object to save.
            quality: JPEG quality (1-100).

        Returns:
            Bytes of the JPEG image.
        """
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        result = buffer.getvalue()
        buffer.close()
        return result

    def adjust_quality_to_target_size(self, img: Image.Image) -> bytes:
        """
        Adjust JPEG quality to resize image to target size.
        Starts at 95% quality and decreases by 5% at a time until target is reached.

        Args:
            img: PIL Image object to resize.

        Returns:
            Bytes of the resized image.
        """
        quality = 95
        min_quality = 5
        quality_step = 5

        while quality >= min_quality:
            # Save as JPEG and check size
            result = self.encode_to_jpeg_bytes(img, quality)
            current_size = len(result)

            # If we're at or below target size, return
            if current_size <= self.target_size:
                return result

            # Decrease quality and try again
            quality -= quality_step

        # If we've exhausted all quality levels, return the lowest quality version
        return self.encode_to_jpeg_bytes(img, min_quality)

    def adjust_quality_to_target_size_with_info(
        self, img: Image.Image
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Adjust JPEG quality to resize image to target size, returning both result and metadata.
        Starts at 95% quality and decreases by 5% at a time until target is reached.

        Args:
            img: PIL Image object to resize.

        Returns:
            Tuple of (bytes of resized image, dict with metadata including passes, final_quality, etc.)
        """
        quality = 95
        min_quality = 5
        quality_step = 5
        passes = 0
        final_quality = quality

        while quality >= min_quality:
            passes += 1
            # Save as JPEG and check size
            result = self.encode_to_jpeg_bytes(img, quality)
            current_size = len(result)

            # If we're at or below target size, return
            if current_size <= self.target_size:
                final_quality = quality
                return result, {
                    "passes": passes,
                    "final_quality": final_quality,
                    "initial_quality": 95,
                    "quality_step": quality_step,
                    "min_quality": min_quality,
                    "final_size": current_size,
                    "target_size": self.target_size,
                    "resized": True,
                }

            # Decrease quality and try again
            quality -= quality_step

        # If we've exhausted all quality levels, return the lowest quality version
        passes += 1  # Count the final attempt
        final_quality = min_quality
        result = self.encode_to_jpeg_bytes(img, min_quality)
        return result, {
            "passes": passes,
            "final_quality": final_quality,
            "initial_quality": 95,
            "quality_step": quality_step,
            "min_quality": min_quality,
            "final_size": len(result),
            "target_size": self.target_size,
            "resized": True,
        }

    def resize(self, image_bytes: bytes) -> bytes:
        """
        Decrease image size to approximately target_size bytes only if it exceeds that size.

        Args:
            image_bytes: Input image as bytes.

        Returns:
            Bytes of the original or resized image (resized images will be JPEG).
        """
        # If original is already under target, return it as-is
        if not self.needs_resizing(image_bytes):
            return image_bytes

        # Open image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if needed
            img_rgb = self.convert_to_rgb(img)

            # Convert to JPEG at 100% quality first to check actual JPEG size
            jpeg_at_100 = self.encode_to_jpeg_bytes(img_rgb, quality=100)

            # If already under target at 100% quality, return it
            if len(jpeg_at_100) <= self.target_size:
                return jpeg_at_100

            # Otherwise, adjust quality to meet target size
            return self.adjust_quality_to_target_size(img_rgb)

    def resize_with_info(self, image_bytes: bytes) -> Tuple[bytes, Dict[str, Any]]:
        """
        Decrease image size to approximately target_size bytes only if it exceeds that size,
        returning both the result and metadata about the process.

        Args:
            image_bytes: Input image as bytes.

        Returns:
            Tuple of (bytes of resized image, dict with metadata).
        """
        original_size = len(image_bytes)

        # If original is already under target, return it as-is with metadata
        if not self.needs_resizing(image_bytes):
            return image_bytes, {
                "passes": 0,
                "final_quality": None,
                "initial_quality": None,
                "quality_step": None,
                "min_quality": None,
                "final_size": original_size,
                "original_size": original_size,
                "target_size": self.target_size,
                "resized": False,
                "format_converted": False,
            }

        # Open image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            original_format = img.format
            original_mode = img.mode
            dimensions = img.size

            # Convert to RGB if needed
            img_rgb = self.convert_to_rgb(img)
            format_converted = img_rgb.mode != original_mode

            # Convert to JPEG at 100% quality first to check actual JPEG size
            jpeg_at_100 = self.encode_to_jpeg_bytes(img_rgb, quality=100)

            # If already under target at 100% quality, return it with metadata
            if len(jpeg_at_100) <= self.target_size:
                return jpeg_at_100, {
                    "passes": 0,
                    "final_quality": 100,
                    "initial_quality": None,
                    "quality_step": None,
                    "min_quality": None,
                    "final_size": len(jpeg_at_100),
                    "original_size": original_size,
                    "target_size": self.target_size,
                    "resized": True,
                    "format_converted": format_converted,
                    "original_format": original_format,
                    "final_format": "JPEG",
                    "dimensions": dimensions,
                }

            # Otherwise, adjust quality to meet target size
            result_bytes, resize_info = self.adjust_quality_to_target_size_with_info(
                img_rgb
            )
            resize_info.update(
                {
                    "original_size": original_size,
                    "format_converted": format_converted,
                    "original_format": original_format,
                    "final_format": "JPEG",
                    "dimensions": dimensions,
                }
            )
            return result_bytes, resize_info


# Example usage
if __name__ == "__main__":  # pragma: no cover
    # Create an instance of ImageResizer
    resizer = ImageResizer(target_size=5_000_000)

    # Load an image as bytes (replace with your image file)
    with open("/Users/paul/Downloads/gamenight.png", "rb") as f:
        input_bytes = f.read()

    # Resize to 5MB if needed
    output_bytes = resizer.resize(input_bytes)

    # Save output bytes to a file for verification
    with open("resized_image.jpg", "wb") as f:
        f.write(output_bytes)

    print(f"Original size: {resizer.get_image_size(input_bytes) / 1_000_000:.2f} MB")
    print(f"Final size: {resizer.get_image_size(output_bytes) / 1_000_000:.2f} MB")
