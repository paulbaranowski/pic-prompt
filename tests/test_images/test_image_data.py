import pytest
from prompt_any.images.image_data import ImageData


@pytest.fixture
def image_data():
    return ImageData(
        image_path="test/image.jpg",
        binary_data=b"test_binary_data",
        media_type="image/jpeg",
    )


def test_init(image_data):
    """Test initialization of ImageData"""
    assert image_data.image_path == "test/image.jpg"
    assert image_data.binary_data == b"test_binary_data"
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
