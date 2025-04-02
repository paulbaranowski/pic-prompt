import pytest
from io import BytesIO
from PIL import Image
from pic_prompt.images.image_data import ImageData
from pic_prompt.core.errors import ImageProcessingError


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

    assert "UnidentifiedImageError opening image" in str(exc_info.value)


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


def test_repr(image_data, sample_image_bytes):
    """Test string representation of ImageData"""
    # Set binary data
    image_data.binary_data = sample_image_bytes

    # Add some encoded images
    image_data.add_provider_encoded_image("provider1", "encoded1")
    image_data.add_provider_encoded_image("provider2", "encoded2")

    # Get string representation
    repr_str = repr(image_data)

    # Verify repr contains key information
    assert "ImageData" in repr_str
    assert f"image_path={image_data.image_path}" in repr_str
    assert f"binary_data={len(sample_image_bytes)}" in repr_str
    assert f"media_type={image_data.media_type}" in repr_str
    assert "provider1: 8 bytes" in repr_str  # len("encoded1") = 8
    assert "provider2: 8 bytes" in repr_str  # len("encoded2") = 8

    # Test repr with no encoded images
    image_data.provider_encoded_images.clear()
    repr_str = repr(image_data)
    assert "encoded_images=none" in repr_str


def test_encode_as_base64(image_data, sample_image_bytes):
    """Test encoding image data as base64"""
    # Set binary data
    image_data.binary_data = sample_image_bytes

    # Test default provider encoding
    encoded = image_data.encode_as_base64()
    assert encoded is not None
    assert isinstance(encoded, str)
    assert image_data.get_encoded_data_for("openai") == encoded

    # Test encoding with no binary data
    image_data.binary_data = None
    assert image_data.encode_as_base64() is None


def test_resize_and_encode(image_data, sample_image_bytes, mocker):
    """Test resizing and encoding image data"""
    # Create mock resizer
    mock_resizer = mocker.Mock()
    mock_resizer.resize.return_value = sample_image_bytes  # Return valid image bytes

    # Set initial binary data
    image_data.binary_data = sample_image_bytes
    initial_size = len(sample_image_bytes)

    # Test resizing to smaller max size
    max_size = initial_size // 2
    image_data.resize_and_encode(max_size, resizer=mock_resizer)

    # Verify resizer was called with correct args
    mock_resizer.resize.assert_called_with(sample_image_bytes)

    # Verify resized data was stored and is valid image bytes
    assert image_data.binary_data == sample_image_bytes
    assert image_data.image_obj is not None

    # Verify encoded data was stored
    encoded = image_data.get_encoded_data_for("openai")
    assert encoded is not None
    assert isinstance(encoded, str)

    # Test with custom provider name
    image_data.resize_and_encode(max_size, provider_name="custom", resizer=mock_resizer)
    assert image_data.get_encoded_data_for("custom") is not None
