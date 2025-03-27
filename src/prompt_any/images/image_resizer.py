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

    def adjust_quality_to_target_size(self, img: Image.Image) -> bytes:
        """
        Adjust JPEG quality to resize image to target size.

        Args:
            img: PIL Image object to resize.

        Returns:
            Bytes of the resized image.
        """
        low_quality = 10
        high_quality = 95
        max_iterations = 20

        for _ in range(max_iterations):
            mid_quality = (low_quality + high_quality) // 2

            # Save to bytes buffer to check size
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=mid_quality)
            current_size = buffer.tell()

            # Check if within tolerance
            if abs(current_size - self.target_size) <= self.tolerance:
                return buffer.getvalue()
            elif current_size > self.target_size:
                high_quality = mid_quality - 1
            else:
                low_quality = mid_quality + 1

            buffer.close()

            # If quality range converges
            if low_quality >= high_quality:
                break

        # Final attempt with mid_quality
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=mid_quality)
        result = buffer.getvalue()
        buffer.close()
        return result

    def resize(self, image_bytes: bytes) -> bytes:
        """
        Decrease image size to approximately target_size bytes only if it exceeds that size.

        Args:
            image_bytes: Input image as bytes.

        Returns:
            Bytes of the original or resized image.
        """
        if not self.needs_resizing(image_bytes):
            return image_bytes  # Return original bytes if under target size

        # Open image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB if needed
            img_rgb = self.convert_to_rgb(img)
            # Resize by adjusting quality
            return self.adjust_quality_to_target_size(img_rgb)


# Example usage
if __name__ == "__main__":
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
