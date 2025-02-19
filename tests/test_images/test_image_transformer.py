import pytest
from io import BytesIO
from PIL import Image
from prompt_any.images.image_transformer import ImageTransformer


@pytest.fixture
def sample_image_bytes():
    """Create a small test image and return its bytes"""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


def test_resample_image(sample_image_bytes):
    """Test that resample_image returns valid image data with expected properties"""
    # Transform the image
    transformed_bytes = ImageTransformer.resample_image(sample_image_bytes)

    # Verify the result is valid image data
    assert isinstance(transformed_bytes, bytes)
    assert len(transformed_bytes) > 0

    # Open and verify the transformed image
    transformed_img = Image.open(BytesIO(transformed_bytes))
    assert transformed_img.format == "JPEG"

    # Original dimensions should be preserved
    assert transformed_img.size == (100, 100)

    # Verify we can read the image data without errors
    transformed_img.load()


def test_resample_image_different_formats():
    """Test resampling works with different image formats"""
    formats = ["PNG", "JPEG"]

    for fmt in formats:
        # Create test image in specified format
        img = Image.new("RGB", (50, 50), color="blue")
        img_bytes = BytesIO()
        img.save(img_bytes, format=fmt)

        # Transform and verify
        transformed = ImageTransformer.resample_image(img_bytes.getvalue())
        result_img = Image.open(BytesIO(transformed))

        assert result_img.format == fmt
        assert result_img.size == (50, 50)


def test_resample_image_invalid_data():
    """Test that invalid image data raises appropriate exception"""
    with pytest.raises(Exception):
        ImageTransformer.resample_image(b"not an image")
