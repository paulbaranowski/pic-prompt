import pytest
from PIL import Image
from io import BytesIO


def create_test_image():
    """Create a test image in memory"""
    # Create a new RGB image with red color
    img = Image.new("RGB", (100, 100), color="red")

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")

    return img_bytes.getvalue()


@pytest.fixture
def in_memory_image():
    """Fixture that returns a test image"""
    return create_test_image()
