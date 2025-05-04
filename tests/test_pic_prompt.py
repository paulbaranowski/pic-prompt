import pytest
from pic_prompt.pic_prompt import PicPrompt
from pic_prompt.core import PromptConfig
from pic_prompt.core.message_role import MessageRole
from pic_prompt.core.message_type import MessageType


@pytest.fixture
def builder():
    """Basic prompt builder fixture"""
    config = PromptConfig(provider_name="openai")
    builder = PicPrompt()
    builder._add_config(config)
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
    builder = PicPrompt()
    assert len(builder.configs) == 1
    assert len(builder.messages) == 0
    assert len(builder.prompts) == 0
    assert builder.image_registry.num_images() == 0


def test_init_custom(custom_config):
    """Test initialization with custom config"""
    builder = PicPrompt()
    builder._add_config(custom_config)
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
    assert len(builder.user_messages) == 1
    assert builder.user_messages[0].role == MessageRole.USER
    assert builder.user_messages[0].content[0].type == MessageType.TEXT
    assert builder.user_messages[0].content[0].data == message


def test_add_image_message(builder):
    """Test adding image message"""
    image_path = "path/to/image.jpg"
    builder.add_image_message(image_path)
    assert len(builder.image_messages) == 1
    assert builder.image_messages[0].role == MessageRole.USER
    assert builder.image_messages[0].content[0].type == MessageType.IMAGE
    assert builder.image_messages[0].content[0].data == image_path


def test_add_image_messages(builder):
    """Test adding multiple image messages"""
    image_paths = ["path/to/image1.jpg", "path/to/image2.jpg", "path/to/image3.jpg"]
    builder.add_image_messages(image_paths)
    assert len(builder.image_messages) == len(image_paths)
    registry = builder.image_registry
    for i, image_data in enumerate(registry.get_all_image_data()):
        assert builder.image_messages[i].role == MessageRole.USER
        assert builder.image_messages[i].content[0].type == MessageType.IMAGE
        assert builder.image_messages[i].content[0].data == image_data.image_path


def test_add_assistant_message(builder):
    """Test adding assistant message"""
    message = "How can I help?"
    builder.add_assistant_message(message)
    assert len(builder.messages) == 1
    assert builder.messages[0].role == MessageRole.ASSISTANT
    assert builder.messages[0].content[0].type == MessageType.TEXT
    assert builder.messages[0].content[0].data == message


def test_clear(builder):
    """Test clearing messages"""
    builder.add_user_message("Hello")
    builder.add_assistant_message("Hi")
    builder.add_image_message("path/to/image.jpg")
    assert len(builder.user_messages) == 1
    assert len(builder.messages) == 1
    assert len(builder.image_messages) == 1
    builder.clear()
    assert len(builder.user_messages) == 0
    assert len(builder.messages) == 0
    assert len(builder.image_messages) == 0


def test_repr(builder):
    """Test string representation"""
    builder.add_user_message("Hello")
    assert repr(builder).startswith("<PromptBuilder messages=")


def test_encode_image_data(builder, mocker):
    """Test encoding image data for providers"""
    # Mock image data and registry
    mock_image_data = mocker.Mock(image_path="test.jpg", binary_data=b"test")
    mock_image_data.is_local_image.return_value = False
    mock_image_data.resize_and_encode.return_value = mock_image_data

    # Mock provider
    mock_provider = mocker.Mock()
    mock_provider.get_image_config.return_value = mocker.Mock(
        requires_base64=True, max_size=1000
    )
    mock_provider.get_provider_name.return_value = "openai"

    # Add image and config
    builder.add_image_message("test.jpg")
    # config = PromptConfig(
    #     provider_name="openai",
    #     model="gpt-4o",
    #     max_tokens=3000,
    #     temperature=0.0,
    # )
    # builder.add_config(config)

    # Mock image registry to return our mock image data
    mocker.patch.object(
        builder.image_registry, "get_all_image_data", return_value=[mock_image_data]
    )

    # Mock get_providers to return our mock provider
    mocker.patch.object(
        builder, "_get_providers", return_value={"openai": mock_provider}
    )

    # Encode images
    registry = builder._encode_image_data()

    # Verify image was resized and encoded
    mock_image_data.resize_and_encode.assert_called_once_with(
        mock_provider.get_image_config().max_size, mock_provider.get_provider_name()
    )

    assert registry is builder.image_registry


# def test_get_content_for(builder, mocker):
#     """Test getting formatted content for a specific provider"""
#     # Mock provider and config
#     mock_provider = mocker.Mock()
#     mock_provider.provider_name = "gemini"
#     mock_provider.get_provider_name.return_value = "gemini"
#     mock_provider.format_messages.return_value = "formatted content"
#     mock_provider.get_image_config.return_value = mocker.Mock(needs_download=True)

#     mocker.patch.object(
#         builder, "get_providers", return_value={"gemini": mock_provider}
#     )

#     # Add config
#     config = PromptConfig.default()
#     config.provider_name = "gemini"
#     builder.add_config(config)

#     # Add some messages
#     builder.add_system_message("system message")
#     builder.add_user_message("user message")

#     # Get content
#     content = builder.get_content()

#     # Verify content was formatted
#     assert content == "formatted content"

#     # Get expected messages in correct order
#     expected_messages = (
#         builder.messages + builder.user_messages + builder.image_messages
#     )

#     mock_provider.format_messages.assert_called_once_with(
#         expected_messages, builder.image_registry, False
#     )


def test_get_prompt(builder, mocker):
    """Test getting formatted content for openai provider"""
    # Mock provider and config
    mock_provider = mocker.Mock()
    mock_provider.provider_name = "openai"
    mock_provider.get_provider_name.return_value = "openai"
    mock_provider.format_messages.return_value = "formatted content"
    mock_provider.get_image_config.return_value = mocker.Mock(requires_base64=True)

    mocker.patch.object(
        builder, "_get_providers", return_value={"openai": mock_provider}
    )

    # Add some messages
    builder.add_system_message("system message")
    builder.add_user_message("user message")

    # Get content
    content = builder.get_prompt()

    # Verify content was formatted
    assert content == "formatted content"

    # Get expected messages in correct order
    expected_messages = (
        builder.messages + builder.user_messages + builder.image_messages
    )

    mock_provider.format_messages.assert_called_once_with(
        expected_messages, builder.image_registry, False
    )
