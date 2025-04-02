import pytest
import json
from pic_prompt.providers.provider_openai import ProviderOpenAI
from pic_prompt.core.prompt_config import PromptConfig
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry
from unittest.mock import Mock


@pytest.fixture
def provider():
    return ProviderOpenAI()


@pytest.fixture
def basic_config():
    return PromptConfig(
        provider_name="openai",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=100,
        top_p=1.0,
    )


def test_image_config(provider):
    config = provider.get_image_config()
    assert config.requires_base64 is True
    assert config.max_size == 20_000_000
    assert config.supported_formats == ["png", "jpeg", "jpg"]
    assert config.needs_download is True


def test_format_content_text(provider):
    from pic_prompt.core.prompt_content import PromptContent

    content = PromptContent(type="text", content="Hello world")
    result = provider._format_content_text(content)

    assert result["type"] == "text"
    assert result["text"] == "Hello world"


def test_format_content_image(provider):
    from pic_prompt.core.prompt_content import PromptContent

    content = PromptContent(type="image", content="http://example.com/image.jpg")
    registry = ImageRegistry()

    # Create mock image data
    mock_image_data = Mock()
    mock_image_data.is_local_image.return_value = False
    mock_image_data.get_encoded_data_for.return_value = "base64encodeddata"
    registry.image_data = {"http://example.com/image.jpg": mock_image_data}

    result = provider._format_content_image(content, registry)

    assert result["type"] == "image_url"
    assert result["image_url"]["url"] == "data:image/jpeg;base64,base64encodeddata"
