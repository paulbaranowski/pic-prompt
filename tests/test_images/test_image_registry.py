import pytest
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.images.image_data import ImageData
from conftest import create_test_image
import os
from pic_prompt.images.errors import ImageDownloadError, ImageSourceError


@pytest.fixture
def image_registry():
    return ImageRegistry()


@pytest.fixture
def sample_image_data():
    return ImageData(
        image_path="test/image.jpg",
        binary_data=create_test_image(),
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
    assert binary_data == create_test_image()


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


def test_clear(image_registry, sample_image_data):
    """Test clearing the image registry"""
    # Add some test data
    image_registry.add_image_data(sample_image_data)
    assert image_registry.num_images() == 1

    # Clear the registry
    image_registry.clear()

    # Verify registry is empty
    assert image_registry.num_images() == 0
    assert image_registry.get_all_image_paths() == []
    assert image_registry.get_all_image_data() == []
    assert image_registry.get_image_data("test/image.jpg") is None


def test_repr(image_registry, sample_image_data):
    """Test string representation of image registry"""
    # Empty registry
    assert repr(image_registry) == "ImageRegistry(image_data={})"

    # Add test data
    image_registry.add_image_data(sample_image_data)
    # Just verify it contains the image path
    assert "test/image.jpg" in repr(image_registry)


def test_download_image_data(image_registry, mocker):
    """Test downloading image data"""
    # Mock the instance
    mock_downloader = mocker.Mock()
    mock_image_data = mocker.Mock(
        image_path="test.jpg",
        binary_data=b"test",
        get_provider_encoded_image=lambda x: None,
    )
    mock_downloader.download.return_value = mock_image_data

    # Add image path to registry
    image_registry.add_image_path("test.jpg")

    # Verify initial state - empty ImageData object exists but has no binary data
    assert image_registry.has_image("test.jpg")
    initial_data = image_registry.get_image_data("test.jpg")
    assert initial_data.binary_data is None

    # Download images
    registry = image_registry.download_image_data(downloader=mock_downloader)

    # Verify download was called
    mock_downloader.download.assert_called_once()

    # Verify image data was updated in registry with downloaded content
    downloaded_data = registry.get_image_data("test.jpg")
    assert downloaded_data.binary_data == b"test"

    # Calling again should not re-download since images already have binary data
    mock_downloader.download.reset_mock()
    image_registry.download_image_data(downloader=mock_downloader)
    mock_downloader.download.assert_not_called()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable.",
)
def test_download_real_image(image_registry):
    """Test downloading a real image from Wikipedia"""
    # Use a stable Wikimedia Commons image URL
    wiki_image = "https://upload.wikimedia.org/wikipedia/commons/d/d3/Boulevard_du_Temple_by_Daguerre.jpg"

    # Add image to registry
    image_registry.add_image_path(wiki_image)

    # Download image
    registry = image_registry.download_image_data()

    # Verify image was downloaded and added to registry
    assert registry.num_images() == 1
    assert registry.has_image(wiki_image)

    # Verify we got actual image data
    image_data = registry.get_image_data(wiki_image)
    assert image_data is not None
    assert len(image_data.binary_data) > 0
    assert image_data.media_type == "image/jpeg"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable.",
)
def test_download_real_image_with_403_error_integration(image_registry):
    """Integration test: Verify behavior when downloading an image returns a 403 error"""
    # Use a stable Wikimedia Commons image URL with typo to trigger 403
    wiki_image = "https://upload.wikimedia.org/wikipedia/commons/d/d3/Boulevard_du_Teple_by_Daguerre.jpg"

    # Add image to registry
    image_registry.add_image_path(wiki_image)

    # Download image
    registry = image_registry.download_image_data(raise_on_error=False)

    # Verify image was not downloaded
    assert registry.get_binary_data(wiki_image) is None


def test_download_image_data_handles_errors(image_registry, mocker):
    """Test that download_image_data properly handles and reports download errors"""
    # Mock downloader that always fails
    mock_downloader = mocker.Mock()
    mock_downloader.download.side_effect = ImageSourceError("Download failed")

    # Add test images
    image_registry.add_image_path("test1.jpg")
    image_registry.add_image_path("test2.jpg")

    # Verify error is raised with details about failed downloads
    with pytest.raises(ImageDownloadError) as exc_info:
        image_registry.download_image_data(downloader=mock_downloader)

    error_msg = str(exc_info.value)
    assert "test1.jpg" in error_msg
    assert "test2.jpg" in error_msg
    assert "Download failed" in error_msg


@pytest.mark.asyncio
async def test_download_image_data_async(image_registry, mocker):
    """Test asynchronous image downloading"""
    # Create a mock downloader with the mocked download_async method
    mock_downloader = mocker.Mock()
    mock_downloader.download_async = mocker.AsyncMock()

    # Make the mock return appropriate ImageData based on the input path
    async def download_side_effect(path):
        return mocker.Mock(image_path=path, binary_data=b"test")

    mock_downloader.download_async.side_effect = download_side_effect

    # Add test image path
    image_registry.add_image_path("test.jpg")
    image_registry.add_image_path("test2.jpg")

    # Call async download with our mock downloader
    registry = await image_registry.download_image_data_async(
        downloader=mock_downloader
    )

    # Verify download was attempted for both images
    assert mock_downloader.download_async.call_count == 2
    mock_downloader.download_async.assert_has_calls(
        [mocker.call("test.jpg"), mocker.call("test2.jpg")]
    )

    # Verify images were added to registry
    assert registry.num_images() == 2

    # Verify first image data
    image_data = registry.get_image_data("test.jpg")
    assert image_data is not None
    assert image_data.image_path == "test.jpg"
    assert image_data.binary_data == b"test"

    # Verify second image data
    image_data2 = registry.get_image_data("test2.jpg")
    assert image_data2 is not None
    assert image_data2.image_path == "test2.jpg"
    assert image_data2.binary_data == b"test"
