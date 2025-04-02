import pytest
from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_config import PromptConfig
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.core.message_role import MessageRole
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.providers.provider import Provider
from PIL import Image
from io import BytesIO
import base64
from pic_prompt.images.image_data import ImageData


class MockProvider(Provider):
    def __init__(self):
        self.image_config = ImageConfig(requires_base64=True, max_size=1000)

    def get_image_config(self) -> ImageConfig:
        return self.image_config

    def format_prompt(self, messages, prompt_config, all_image_data):
        return "mock formatted prompt"

    def _format_content_image(self, content, all_image_data):
        return {"type": "image", "image_url": content.data}

    def _format_content_text(self, content):
        return {"type": "text", "text": content.data}


@pytest.fixture
def provider():
    return MockProvider()


@pytest.fixture
def image_registry():
    return ImageRegistry()


@pytest.fixture
def text_message():
    message = PromptMessage(role=MessageRole.USER)
    message.add_text("Hello world")
    return message


@pytest.fixture
def image_message():
    message = PromptMessage(role=MessageRole.USER)
    message.add_image("image.jpg")
    return message


def test_get_provider_name(provider):
    """Test getting provider name"""
    assert provider.get_provider_name() == "mock"


def test_get_image_config(provider):
    """Test getting image config"""
    config = provider.get_image_config()
    assert isinstance(config, ImageConfig)
    assert config.requires_base64 is True


def test_format_messages(provider, text_message, image_registry):
    """Test formatting messages"""
    messages = [text_message]
    formatted = provider.format_messages(messages, image_registry)
    assert len(formatted) == 1
    assert formatted[0]["role"] == "user"
    assert isinstance(formatted[0]["content"], list)


def test_format_content(provider, text_message, image_registry):
    """Test formatting content"""
    formatted = provider.format_content(text_message, image_registry)
    assert len(formatted) == 1
    assert formatted[0]["type"] == "text"
    assert formatted[0]["text"] == "Hello world"


def test_format_prompt(provider, text_message, image_registry):
    """Test formatting prompt"""
    messages = [text_message]
    config = PromptConfig()
    formatted = provider.format_prompt(messages, config, image_registry)
    assert formatted == "mock formatted prompt"
