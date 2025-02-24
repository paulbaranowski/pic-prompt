import pytest
import json
from prompt_any.providers.provider_openai import ProviderOpenAI
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images.image_registry import ImageRegistry


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
    assert config.requires_base64 is False
    assert config.max_size == 5_000_000
    assert config.supported_formats == ["png", "jpeg", "jpg"]
    assert config.needs_download is False


def test_format_prompt_basic(provider, basic_config):
    messages = [
        PromptMessage(
            role="system",
            content=[
                PromptContent(type="text", content="You are a helpful assistant.")
            ],
        ),
        PromptMessage(
            role="user",
            content=[PromptContent(type="text", content="Hello!")],
        ),
    ]

    result = provider.format_prompt(messages, basic_config, ImageRegistry())
    parsed = json.loads(result)

    assert parsed["model"] == "gpt-3.5-turbo"
    assert parsed["temperature"] == 0.7
    assert parsed["max_tokens"] == 100
    assert parsed["top_p"] == 1.0
    assert len(parsed["messages"]) == 2
    assert parsed["messages"][0]["role"] == "system"
    assert parsed["messages"][1]["role"] == "user"


def test_format_prompt_with_images(provider, basic_config):
    messages = [
        PromptMessage(
            role="user",
            content=[
                PromptContent(type="text", content="What's in this image?"),
                PromptContent(type="image", content="http://example.com/image1.jpg"),
                PromptContent(type="image", content="http://example.com/image2.jpg"),
            ],
        ),
        PromptMessage(
            role="assistant",
            content=[PromptContent(type="text", content="I see two images")],
        ),
    ]

    result = provider.format_prompt(messages, basic_config, ImageRegistry())
    parsed = json.loads(result)

    assert len(parsed["messages"]) == 2

    # Check user message with images
    user_message = parsed["messages"][0]
    assert user_message["role"] == "user"
    assert len(user_message["content"]) == 3

    # Check text content
    assert user_message["content"][0]["type"] == "text"
    assert user_message["content"][0]["text"] == "What's in this image?"

    # Check image contents
    assert user_message["content"][1]["type"] == "image_url"
    assert (
        user_message["content"][1]["image_url"]["url"]
        == "http://example.com/image1.jpg"
    )
    assert user_message["content"][2]["type"] == "image_url"
    assert (
        user_message["content"][2]["image_url"]["url"]
        == "http://example.com/image2.jpg"
    )

    # Check assistant message
    assistant_message = parsed["messages"][1]
    assert assistant_message["role"] == "assistant"
    assert len(assistant_message["content"]) == 1
    assert assistant_message["content"][0]["type"] == "text"
    assert assistant_message["content"][0]["text"] == "I see two images"


def test_format_prompt_with_json_schema(provider, basic_config):
    messages = [
        PromptMessage(
            role="user",
            content=[PromptContent(type="text", content="List three colors")],
        )
    ]
    basic_config.json_response = True
    basic_config.json_schema = {
        "type": "object",
        "properties": {"colors": {"type": "array", "items": {"type": "string"}}},
    }

    result = provider.format_prompt(messages, basic_config, ImageRegistry())
    parsed = json.loads(result)

    assert "json_schema" in parsed
    assert parsed["json_schema"]["type"] == "object"
    assert "colors" in parsed["json_schema"]["properties"]


def test_format_content_text(provider):
    from prompt_any.core.prompt_content import PromptContent

    content = PromptContent(type="text", content="Hello world")
    result = provider._format_content_text(content)

    assert result["type"] == "text"
    assert result["text"] == "Hello world"


def test_format_content_image(provider):
    from prompt_any.core.prompt_content import PromptContent

    content = PromptContent(type="image", content="http://example.com/image.jpg")
    registry = ImageRegistry()

    result = provider._format_content_image(content, registry)

    assert result["type"] == "image_url"
    assert result["image_url"]["url"] == "http://example.com/image.jpg"


def test_format_content_image_base64(provider):
    from prompt_any.core.prompt_content import PromptContent

    # Set requires_base64 to True
    provider._image_config.requires_base64 = True

    content = PromptContent(
        type="image", content="SGVsbG8gd29ybGQ="
    )  # Example base64 data
    registry = ImageRegistry()

    result = provider._format_content_image(content, registry)

    assert result["type"] == "image_url"
    assert result["image_url"]["url"] == "data:image/jpeg;base64,SGVsbG8gd29ybGQ="
