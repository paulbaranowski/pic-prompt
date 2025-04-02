import pytest
import json
from pic_prompt.providers.provider_anthropic import ProviderAnthropic
from pic_prompt.core.prompt_config import PromptConfig
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.images.image_data import ImageData
from conftest import create_test_image


@pytest.fixture
def provider():
    return ProviderAnthropic()


@pytest.fixture
def basic_config():
    return PromptConfig(
        provider_name="anthropic",
        model="claude-2",
        temperature=0.7,
        max_tokens=100,
        top_p=1.0,
    )


def test_image_config(provider):
    config = provider.get_image_config()
    assert config.requires_base64 is True
    assert config.max_size == 5_000_000
    assert config.supported_formats == ["png", "jpeg", "gif", "webp"]
    assert config.needs_download is True


def test_format_content_text(provider):
    content = PromptContent(type="text", content="Hello world")
    result = provider._format_content_text(content)

    assert result["type"] == "text"
    assert result["text"] == "Hello world"


def test_format_content_image(provider):
    content = PromptContent(type="image", content="test_image")
    registry = ImageRegistry()
    image_data = ImageData(
        image_path="test_image",
        media_type="image/jpeg",
        binary_data=create_test_image(),
    )
    image_data.add_provider_encoded_image(provider.get_provider_name(), "encoded_data")
    registry.add_image_data(image_data)

    result = provider._format_content_image(content, registry)

    assert result["type"] == "image"
    assert result["source"]["type"] == "base64"
    assert result["source"]["media_type"] == "image/jpeg"
    assert result["source"]["data"] == "encoded_data"


def test_format_content_image_not_found(provider):
    content = PromptContent(type="image", content="missing_image")
    registry = ImageRegistry()

    with pytest.raises(ValueError, match="Image data not found for missing_image"):
        provider._format_content_image(content, registry)
