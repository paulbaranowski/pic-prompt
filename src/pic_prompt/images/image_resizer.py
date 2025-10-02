from PIL import Image
import io


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
