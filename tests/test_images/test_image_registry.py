import pytest
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.images.image_data import ImageData


@pytest.fixture
def image_registry():
    return ImageRegistry()


@pytest.fixture
def sample_image_data():
    return ImageData(
        image_path="test/image.jpg",
        binary_data=b"test_binary_data",
        media_type="image/jpeg",
    )


def test_empty_registry(image_registry):
    """Test a newly created registry is empty"""
    assert image_registry.num_images() == 0
    assert image_registry.get_all_image_paths() == []
    assert image_registry.get_all_image_data() == []


def test_add_image_data(image_registry, sample_image_data):
    """Test adding image data to registry"""
    image_registry.add_image_data(sample_image_data)

    assert image_registry.num_images() == 1
    assert image_registry.get_all_image_paths() == ["test/image.jpg"]
    assert image_registry.get_all_image_data() == [sample_image_data]


def test_get_image_data(image_registry, sample_image_data):
    """Test retrieving image data from registry"""
    image_registry.add_image_data(sample_image_data)

    retrieved = image_registry.get_image_data("test/image.jpg")
    assert retrieved == sample_image_data

    # Test non-existent image
    assert image_registry.get_image_data("nonexistent.jpg") is None


def test_get_binary_data(image_registry, sample_image_data):
    """Test retrieving binary data from registry"""
    image_registry.add_image_data(sample_image_data)

    binary_data = image_registry.get_binary_data("test/image.jpg")
    assert binary_data == b"test_binary_data"


def test_add_provider_encoded_image(image_registry, sample_image_data):
    """Test adding encoded image for a provider"""
    image_registry.add_image_data(sample_image_data)

    provider = "test_provider"
    encoded_data = "base64_encoded_data"

    image_registry.add_provider_encoded_image("test/image.jpg", provider, encoded_data)

    image_data = image_registry.get_image_data("test/image.jpg")
    assert image_data.get_encoded_data_for(provider) == encoded_data


def test_add_provider_encoded_image_nonexistent(image_registry):
    """Test adding encoded image for non-existent image raises KeyError"""
    with pytest.raises(KeyError):
        image_registry.add_provider_encoded_image(
            "nonexistent.jpg", "provider", "encoded_data"
        )
