import json
import pytest
from pic_prompt.providers.provider_gemini import ProviderGemini
from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_config import PromptConfig
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.images.image_data import ImageData
from conftest import create_test_image


@pytest.fixture
def provider():
    return ProviderGemini()


@pytest.fixture
def image_registry():
    return ImageRegistry()


def test_get_image_config(provider):
    config = provider.get_image_config()
    assert isinstance(config, ImageConfig)
    assert config.requires_base64 is True
    assert config.max_size == 20_000_000
    assert config.supported_formats == [
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/heic",
        "image/heif",
    ]
    assert config.needs_download is True


def test_format_messages(provider, image_registry):
    messages = [
        PromptMessage(
            role="user", content=[PromptContent(type="text", content="Hello")]
        ),
        PromptMessage(
            role="assistant", content=[PromptContent(type="text", content="Hi there")]
        ),
    ]

    formatted = provider.format_messages(messages, image_registry)
    assert isinstance(formatted, list)
    assert len(formatted) == 2

    # Check first message
    assert formatted[0]["text"] == "Hello"

    # Check second message
    assert formatted[1]["text"] == "Hi there"


def test_format_content_text_only(provider, image_registry):
    message = PromptMessage(
        role="user", content=[PromptContent(type="text", content="Hello")]
    )

    formatted = provider.format_messages([message], image_registry)
    assert isinstance(formatted, list)
    assert len(formatted) == 1
    assert formatted[0]["text"] == "Hello"


def test_format_content_text_formatting(provider, image_registry):
    message = PromptMessage(
        role="user",
        content=[PromptContent(type="text", content="Test\nWith\nNewlines")],
    )

    formatted = provider.format_messages([message], image_registry)
    assert isinstance(formatted, list)
    assert len(formatted) == 1
    assert formatted[0]["text"] == "Test\nWith\nNewlines"


def test_format_content_raises_on_missing_image(provider, image_registry):
    message = PromptMessage(
        role="user", content=[PromptContent(type="image", content="nonexistent_image")]
    )

    with pytest.raises(ValueError, match="Image data not found"):
        provider.format_content(message, image_registry)
