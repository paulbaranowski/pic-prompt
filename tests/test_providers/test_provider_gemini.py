import json
import pytest
from prompt_any.providers.provider_gemini import ProviderGemini
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent, MessageType
from prompt_any.images.image_registry import ImageRegistry


@pytest.fixture
def provider():
    return ProviderGemini()


@pytest.fixture
def image_registry():
    return ImageRegistry()


def test_get_image_config(provider):
    config = provider.get_image_config()
    assert isinstance(config, ImageConfig)
    assert config.requires_base64 is False
    assert config.max_size == 10_000_000
    assert config.supported_formats == [
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/heic",
        "image/heif",
    ]
    assert config.needs_download is True


def test_format_prompt(provider, image_registry):
    messages = [PromptMessage([PromptContent(MessageType.TEXT, "Hello")])]
    prompt_config = PromptConfig(max_tokens=100, temperature=0.7, top_p=0.9)

    formatted = provider.format_prompt(messages, prompt_config, image_registry)
    parsed = json.loads(formatted)

    assert "contents" in parsed
    assert "generationConfig" in parsed
    assert parsed["generationConfig"]["maxOutputTokens"] == 100
    assert parsed["generationConfig"]["temperature"] == 0.7
    assert parsed["generationConfig"]["topP"] == 0.9
    assert parsed["generationConfig"]["topK"] == 10


def test_format_messages(provider, image_registry):
    messages = [PromptMessage([PromptContent(MessageType.TEXT, "Hello")])]

    formatted = provider.format_messages(messages, image_registry)
    assert "contents" in formatted
    assert isinstance(formatted["contents"], list)
    assert "parts" in formatted["contents"][0]
    assert formatted["contents"][0]["parts"][0]["text"] == "Hello"


def test_format_content_text_only(provider, image_registry):
    message = PromptMessage([PromptContent(MessageType.TEXT, "Hello")])

    formatted = provider.format_content(message, image_registry)
    assert "parts" in formatted
    assert len(formatted["parts"]) == 1
    assert formatted["parts"][0]["text"] == "Hello"


def test_format_content_text_formatting(provider, image_registry):
    message = PromptMessage([PromptContent(MessageType.TEXT, "Test\nWith\nNewlines")])

    formatted = provider.format_content(message, image_registry)
    assert formatted["parts"][0]["text"] == "Test\nWith\nNewlines"


def test_format_content_raises_on_missing_image(provider, image_registry):
    message = PromptMessage([PromptContent(MessageType.IMAGE, "nonexistent_image")])

    with pytest.raises(ValueError, match="Image data not found"):
        provider.format_content(message, image_registry)
