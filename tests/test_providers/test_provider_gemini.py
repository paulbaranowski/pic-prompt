import json
import pytest
from prompt_any.providers.provider_gemini import ProviderGemini
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.images.image_data import ImageData
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
    messages = [
        PromptMessage(
            role="system",
            content=[
                PromptContent(type="text", content="You are a helpful assistant.")
            ],
        ),
        PromptMessage(
            role="user", content=[PromptContent(type="text", content="Hello")]
        ),
    ]
    prompt_config = PromptConfig(
        provider_name="gemini",
        model="gemini-pro",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
    )

    formatted = provider.format_prompt(messages, prompt_config, image_registry)
    parsed = json.loads(formatted)

    assert "contents" in parsed
    assert "generationConfig" in parsed
    assert len(parsed["contents"]) == 2
    assert parsed["contents"][0]["parts"][0]["text"] == "You are a helpful assistant."
    assert parsed["contents"][1]["parts"][0]["text"] == "Hello"
    assert parsed["generationConfig"]["maxOutputTokens"] == 100
    assert parsed["generationConfig"]["temperature"] == 0.7
    assert parsed["generationConfig"]["topP"] == 0.9
    assert parsed["generationConfig"]["topK"] == 10


def test_format_prompt_with_image(provider, image_registry):
    messages = [
        PromptMessage(
            role="user",
            content=[
                PromptContent(type="text", content="What's in this image?"),
                PromptContent(type="image", content="test_image"),
            ],
        ),
    ]
    prompt_config = PromptConfig(
        provider_name="gemini",
        model="gemini-pro-vision",
        max_tokens=100,
        temperature=0.7,
        top_p=0.9,
    )

    # Add test image to registry
    image_data = ImageData(
        image_path="test_image",
        media_type="image/jpeg",
        binary_data=create_test_image(),
    )
    image_data.add_provider_encoded_image(provider.get_provider_name(), "encoded_data")
    image_registry.add_image_data(image_data)

    formatted = provider.format_prompt(messages, prompt_config, image_registry)
    parsed = json.loads(formatted)

    assert "contents" in parsed
    assert "generationConfig" in parsed
    assert len(parsed["contents"]) == 1

    # Check parts ordering - image should come before text
    parts = parsed["contents"][0]["parts"]
    assert len(parts) == 2

    # Verify image part
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["mime_type"] == "image/jpeg"
    assert parts[0]["inline_data"]["data"] == "encoded_data"

    # Verify text part
    assert parts[1]["text"] == "What's in this image?"

    # Verify generation config
    assert parsed["generationConfig"]["maxOutputTokens"] == 100
    assert parsed["generationConfig"]["temperature"] == 0.7
    assert parsed["generationConfig"]["topP"] == 0.9
    assert parsed["generationConfig"]["topK"] == 10


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
    assert "contents" in formatted
    assert isinstance(formatted["contents"], list)
    assert len(formatted["contents"]) == 2

    # Check first message
    assert "parts" in formatted["contents"][0]
    assert formatted["contents"][0]["parts"][0]["text"] == "Hello"

    # Check second message
    assert "parts" in formatted["contents"][1]
    assert formatted["contents"][1]["parts"][0]["text"] == "Hi there"


def test_format_content_text_only(provider, image_registry):
    message = PromptMessage(
        role="user", content=[PromptContent(type="text", content="Hello")]
    )

    formatted = provider.format_content(message, image_registry)
    assert "parts" in formatted
    assert len(formatted["parts"]) == 1
    assert formatted["parts"][0]["text"] == "Hello"


def test_format_content_text_formatting(provider, image_registry):
    message = PromptMessage(
        role="user",
        content=[PromptContent(type="text", content="Test\nWith\nNewlines")],
    )

    formatted = provider.format_content(message, image_registry)
    assert "parts" in formatted
    assert len(formatted["parts"]) == 1
    assert formatted["parts"][0]["text"] == "Test\nWith\nNewlines"


def test_format_content_raises_on_missing_image(provider, image_registry):
    message = PromptMessage(
        role="user", content=[PromptContent(type="image", content="nonexistent_image")]
    )

    with pytest.raises(ValueError, match="Image data not found"):
        provider.format_content(message, image_registry)
