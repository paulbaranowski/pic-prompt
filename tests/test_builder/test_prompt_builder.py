import pytest
from prompt_any.builder.prompt_builder import PromptBuilder
from prompt_any.core import PromptConfig
from prompt_any.core.message_role import MessageRole
from prompt_any.core.message_type import MessageType
import os
from prompt_any.images.errors import ImageSourceError, ImageDownloadError


@pytest.fixture
def builder():
    """Basic prompt builder fixture"""
    config = PromptConfig(provider_name="openai")
    builder = PromptBuilder()
    builder.add_config(config)
    return builder


@pytest.fixture
def custom_config():
    """Custom prompt config fixture"""
    return PromptConfig(provider_name="openai", model="foobar")


@pytest.fixture
def invalid_config():
    """Custom prompt config fixture"""
    return PromptConfig(provider_name="blah", model="foobar")


def test_init_default():
    """Test initialization with default config"""
    builder = PromptBuilder()
    assert len(builder.configs) == 0
    assert len(builder.messages) == 0
    assert len(builder.prompts) == 0
    assert builder.image_registry.num_images() == 0


def test_init_custom(custom_config):
    """Test initialization with custom config"""
    builder = PromptBuilder()
    builder.add_config(custom_config)
    assert len(builder.configs) == 1
    assert "openai" in builder.configs
    assert builder.configs["openai"] == custom_config
    assert builder.configs["openai"].model == "foobar"
    assert len(builder.messages) == 0
    assert len(builder.prompts) == 0
    assert builder.image_registry.num_images() == 0


def test_add_system_message(builder):
    """Test adding system message"""
    message = "You are a helpful assistant"
    builder.add_system_message(message)
    assert len(builder.messages) == 1
    assert builder.messages[0].role == MessageRole.SYSTEM
    assert builder.messages[0].content[0].type == MessageType.TEXT
    assert builder.messages[0].content[0].data == message


def test_add_user_message(builder):
    """Test adding user message"""
    message = "Hello!"
    builder.add_user_message(message)
    assert len(builder.messages) == 1
    assert builder.messages[0].role == MessageRole.USER
    assert builder.messages[0].content[0].type == MessageType.TEXT
    assert builder.messages[0].content[0].data == message


def test_add_image_message(builder):
    """Test adding image message"""
    image_path = "path/to/image.jpg"
    builder.add_image_message(image_path)
    assert len(builder.messages) == 1
    assert builder.messages[0].role == MessageRole.USER
    assert builder.messages[0].content[0].type == MessageType.IMAGE
    assert builder.messages[0].content[0].data == image_path


def test_add_image_messages(builder):
    """Test adding multiple image messages"""
    image_paths = ["path/to/image1.jpg", "path/to/image2.jpg", "path/to/image3.jpg"]
    builder.add_image_messages(image_paths)
    assert len(builder.messages) == len(image_paths)
    registry = builder.image_registry
    for i, image_data in enumerate(registry.get_all_image_data()):
        assert builder.messages[i].role == MessageRole.USER
        assert builder.messages[i].content[0].type == MessageType.IMAGE
        assert builder.messages[i].content[0].data == image_data.image_path


def test_add_assistant_message(builder):
    """Test adding assistant message"""
    message = "How can I help?"
    builder.add_assistant_message(message)
    assert len(builder.messages) == 1
    assert builder.messages[0].role == MessageRole.ASSISTANT
    assert builder.messages[0].content[0].type == MessageType.TEXT
    assert builder.messages[0].content[0].data == message


def test_add_config(builder, custom_config):
    """Test adding new config"""
    builder.add_config(custom_config)
    assert "openai" in builder.configs
    assert builder.configs["openai"] == custom_config


def test_get_config(builder):
    """Test getting config"""
    config = builder.get_config("openai")
    assert isinstance(config, PromptConfig)


def test_remove_config(builder):
    """Test removing config"""
    builder.remove_config("openai")
    assert "openai" not in builder.configs


def test_has_config(builder):
    """Test checking config existence"""
    assert builder.has_config("openai") is True
    assert builder.has_config("invalid") is False


def test_clear(builder):
    """Test clearing messages"""
    builder.add_user_message("Hello")
    builder.add_assistant_message("Hi")
    assert len(builder.messages) == 2

    builder.clear()
    assert len(builder.messages) == 0


def test_add_invalid_provider(builder, invalid_config):
    """Test adding config with invalid provider"""
    with pytest.raises(ValueError):
        builder.add_config(invalid_config)


def test_repr(builder):
    """Test string representation"""
    builder.add_user_message("Hello")
    assert repr(builder).startswith("<PromptBuilder messages=")


def test_should_download_images(builder):
    """Test checking if images need to be downloaded"""
    # Initially no configs require image download
    assert builder._should_download_images() is False

    # Add config that requires image download
    config = PromptConfig.default()
    config.provider_name = "gemini"  # Gemini requires image download
    builder.add_config(config)
    assert builder._should_download_images() is True

    # Remove config that requires download
    builder.remove_config("gemini")
    assert builder._should_download_images() is False


def test_download_image_data(builder, mocker):
    """Test downloading image data"""
    # Mock the ImageDownloader instance
    mock_downloader = mocker.Mock()
    mock_image_data = mocker.Mock(
        image_path="test.jpg",
        binary_data=b"test",
        get_provider_encoded_image=lambda x: None,
    )
    mock_downloader.download.return_value = mock_image_data

    # Mock provider and its image config
    mock_provider = mocker.Mock()
    mock_provider.get_image_config.return_value = mocker.Mock(needs_download=True)
    mocker.patch.object(
        builder, "get_providers", return_value={"gemini": mock_provider}
    )

    # Add image message and config requiring download
    builder.add_image_message("test.jpg")
    config = PromptConfig.default()
    config.provider_name = "gemini"  # Gemini requires image download
    builder.add_config(config)

    # Verify initial state - empty ImageData object exists but has no binary data
    assert builder.image_registry.has_image("test.jpg")
    initial_data = builder.image_registry.get_image_data("test.jpg")
    assert initial_data.binary_data is None

    # Download images
    registry = builder.download_image_data(downloader=mock_downloader)

    # Verify download was called
    mock_downloader.download.assert_called_once()

    # Verify image data was updated in registry with downloaded content
    downloaded_data = registry.get_image_data("test.jpg")
    assert downloaded_data.binary_data == b"test"

    # Calling again should not re-download since images already have binary data
    mock_downloader.download.reset_mock()
    builder.download_image_data(downloader=mock_downloader)
    mock_downloader.download.assert_not_called()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable.",
)
def test_download_real_image(builder):
    """Test downloading a real image from Wikipedia"""
    # Use a stable Wikimedia Commons image URL
    wiki_image = "https://upload.wikimedia.org/wikipedia/commons/d/d3/Boulevard_du_Temple_by_Daguerre.jpg"

    # Add image message and config requiring download
    builder.add_image_message(wiki_image)
    config = PromptConfig.default()
    config.provider_name = "anthropic"  # Anthropic requires image download
    builder.add_config(config)

    # Download image
    registry = builder.download_image_data()

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
def test_download_real_image_with_403_error_integration(builder):
    """Integration test: Verify behavior when downloading an image returns a 403 error"""
    # Use a stable Wikimedia Commons image URL
    wiki_image = "https://upload.wikimedia.org/wikipedia/commons/d/d3/Boulevard_du_Teple_by_Daguerre.jpg"

    # Add image message and config requiring download
    builder.add_image_message(wiki_image)
    config = PromptConfig.default()
    config.provider_name = "anthropic"  # Anthropic requires image download
    builder.add_config(config)

    # Download image
    registry = builder.download_image_data(raise_on_error=False)

    # Verify image was not downloaded
    assert registry.get_binary_data(wiki_image) is None


def test_encode_image_data(builder, mocker):
    """Test encoding image data for providers"""
    # Mock image download and provider processing
    mock_image_data = mocker.Mock(image_path="test.jpg", binary_data=b"test")
    mock_image_data.get_provider_encoded_image.return_value = "encoded_test_data"
    mock_download = mocker.patch("prompt_any.images.ImageDownloader.download")
    mock_download.return_value = mock_image_data

    # Add image and config
    builder.add_image_message("test.jpg")
    config = PromptConfig.default()
    config.provider_name = "gemini"
    builder.add_config(config)

    # Download images first
    builder.download_image_data()

    # Mock provider image processing
    mock_provider = mocker.Mock()
    mock_provider.provider_name = "gemini"
    mock_provider.process_image.return_value = "encoded_test_data"
    mock_provider.get_image_config.return_value = mocker.Mock(needs_download=True)

    mocker.patch.object(
        builder, "get_providers", return_value={"gemini": mock_provider}
    )

    # Encode images
    registry = builder.encode_image_data()

    # Verify provider processed image
    mock_provider.process_image.assert_called_once_with(mock_image_data)

    # Verify encoded data was added to registry
    image_data = registry.get_image_data("test.jpg")
    assert image_data is not None
    assert image_data.get_provider_encoded_image("gemini") == "encoded_test_data"


def test_get_prompt_for(builder, mocker):
    """Test getting formatted prompt for a specific provider"""
    # Mock provider and config
    mock_provider = mocker.Mock()
    mock_provider.provider_name = "gemini"
    mock_provider.get_provider_name.return_value = "gemini"
    mock_provider.format_prompt.return_value = "formatted prompt"
    mock_provider.get_image_config.return_value = mocker.Mock(needs_download=False)

    mocker.patch.object(
        builder, "get_providers", return_value={"gemini": mock_provider}
    )

    # Add config
    config = PromptConfig.default()
    config.provider_name = "gemini"
    builder.add_config(config)

    # Add some messages
    builder.add_system_message("system message")
    builder.add_user_message("user message")

    # Get prompt
    prompt = builder.get_prompt_for("gemini")

    # Verify prompt was formatted
    assert prompt == "formatted prompt"
    mock_provider.format_prompt.assert_called_once_with(
        builder.messages, config, builder.image_registry
    )

    # Getting prompt again should use cached version
    mock_provider.format_prompt.reset_mock()
    prompt = builder.get_prompt_for("gemini")
    assert prompt == "formatted prompt"
    mock_provider.format_prompt.assert_not_called()


def test_get_content_for(builder, mocker):
    """Test getting formatted content for a specific provider"""
    # Mock provider and config
    mock_provider = mocker.Mock()
    mock_provider.provider_name = "gemini"
    mock_provider.get_provider_name.return_value = "gemini"
    mock_provider.format_messages.return_value = "formatted content"
    mock_provider.get_image_config.return_value = mocker.Mock(needs_download=False)

    mocker.patch.object(
        builder, "get_providers", return_value={"gemini": mock_provider}
    )

    # Add config
    config = PromptConfig.default()
    config.provider_name = "gemini"
    builder.add_config(config)

    # Add some messages
    builder.add_system_message("system message")
    builder.add_user_message("user message")

    # Get content
    content = builder.get_content_for("gemini")

    # Verify content was formatted
    assert content == "formatted content"
    mock_provider.format_messages.assert_called_once_with(
        builder.messages, builder.image_registry
    )


def test_download_image_data_handles_errors(builder, mocker):
    """Test that download_image_data properly handles and reports download errors"""
    # Mock downloader that always fails
    mock_downloader = mocker.Mock()
    mock_downloader.download.side_effect = ImageSourceError("Download failed")

    # Mock provider that requires downloads
    mock_provider = mocker.Mock()
    mock_provider.get_image_config.return_value = mocker.Mock(needs_download=True)
    mocker.patch.object(
        builder, "get_providers", return_value={"gemini": mock_provider}
    )

    # Add test images and config
    builder.add_image_message("test1.jpg")
    builder.add_image_message("test2.jpg")
    config = PromptConfig.default()
    config.provider_name = "gemini"
    builder.add_config(config)

    # Verify error is raised with details about failed downloads
    with pytest.raises(ImageDownloadError) as exc_info:
        builder.download_image_data(downloader=mock_downloader)

    error_msg = str(exc_info.value)
    assert "test1.jpg" in error_msg
    assert "test2.jpg" in error_msg
    assert "Download failed" in error_msg
