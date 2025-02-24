import pytest
from io import BytesIO
from PIL import Image
from prompt_any.images.image_data import ImageData
from prompt_any.core.errors import ImageProcessingError


@pytest.fixture
def in_memory_image():
    """Create a test image in memory"""
    # Create a new RGB image with red color
    img = Image.new("RGB", (100, 100), color="red")

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")

    return img_bytes.getvalue()


@pytest.fixture
def image_data(in_memory_image):
    return ImageData(
        image_path="test/image.jpg",
        binary_data=in_memory_image,
        media_type="image/jpeg",
    )


def test_init(image_data, in_memory_image):
    """Test initialization of ImageData"""
    assert image_data.image_path == "test/image.jpg"
    assert image_data.binary_data == in_memory_image
    assert image_data.media_type == "image/jpeg"
    assert image_data.provider_encoded_images == {}


def test_add_provider_encoded_image(image_data):
    """Test adding encoded image data for a provider"""
    provider = "test_provider"
    encoded_data = "base64_encoded_data"

    image_data.add_provider_encoded_image(provider, encoded_data)

    assert image_data.provider_encoded_images[provider] == encoded_data


def test_get_encoded_data_for_existing_provider(image_data):
    """Test getting encoded data for an existing provider"""
    provider = "test_provider"
    encoded_data = "base64_encoded_data"
    image_data.add_provider_encoded_image(provider, encoded_data)

    result = image_data.get_encoded_data_for(provider)

    assert result == encoded_data


def test_get_encoded_data_for_nonexistent_provider(image_data):
    """Test getting encoded data for a non-existent provider raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        image_data.get_encoded_data_for("nonexistent_provider")

    assert "Encoded data not found for provider" in str(exc_info.value)


@pytest.fixture
def sample_image_bytes():
    """Create a small test image and return its bytes"""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    return img_bytes.getvalue()


def test_binary_data_invalid_image():
    """Test that setting invalid binary data raises ImageProcessingError"""
    image_data = ImageData("test.jpg")

    with pytest.raises(ImageProcessingError) as exc_info:
        image_data.binary_data = b"not a valid image"

    assert "Error creating image object" in str(exc_info.value)


def test_get_dimensions(image_data, sample_image_bytes):
    """Test that get_dimensions returns correct image dimensions"""
    # Set the binary data using the sample image fixture
    image_data.binary_data = sample_image_bytes

    # Get dimensions
    width, height = image_data.get_dimensions()

    # Sample image is 100x100 from fixture
    assert width == 100
    assert height == 100
    assert isinstance(width, int)
    assert isinstance(height, int)


# def test_resample_image(image_data, sample_image_bytes):
#     """Test that resample_image returns valid image data with expected properties"""
#     # Set the binary data
#     image_data.binary_data = sample_image_bytes

#     # Transform the image
#     transformed_bytes = image_data.resample_image()

#     # Verify the result is valid image data
#     assert isinstance(transformed_bytes, bytes)
#     assert len(transformed_bytes) > 0

#     # Open and verify the transformed image
#     transformed_img = Image.open(BytesIO(transformed_bytes))
#     assert transformed_img.format == "JPEG"

#     # Original dimensions should be preserved
#     assert transformed_img.size == (100, 100)

#     # Verify we can read the image data without errors
#     transformed_img.load()


# def test_resample_image_different_formats():
#     """Test resampling works with different image formats"""
#     formats = ["PNG", "JPEG"]

#     for fmt in formats:
#         # Create test image in specified format
#         img = Image.new("RGB", (50, 50), color="blue")
#         img_bytes = BytesIO()
#         img.save(img_bytes, format=fmt)

#         # Create ImageData instance with test image
#         image_data = ImageData("test.jpg", img_bytes.getvalue(), f"image/{fmt.lower()}")

#         # Transform and verify
#         transformed = image_data.resample_image()
#         result_img = Image.open(BytesIO(transformed))

#         assert result_img.format == fmt
#         assert result_img.size == (50, 50)


# def test_resample_image_invalid_data():
#     """Test that invalid image data raises appropriate exception"""
#     image_data = ImageData("test.jpg", b"not an image", "image/jpeg")
#     with pytest.raises(Exception):
#         image_data.resample_image()
