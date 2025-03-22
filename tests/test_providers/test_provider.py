import pytest
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.message_role import MessageRole
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.providers.provider import Provider
from PIL import Image
from io import BytesIO
import base64
from prompt_any.images.image_data import ImageData


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


def test_process_image(provider):
    """Test processing image"""
    # Create test image data
    img = Image.new("RGB", (50, 50), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    test_image_data = img_bytes.getvalue()
    test_data = ImageData(
        "test.png", binary_data=test_image_data, media_type="image/png"
    )

    # Process the image
    processed = provider.process_image(test_data)

    # Verify the image was processed and encoded data was stored
    assert isinstance(processed, ImageData)
    assert provider.get_provider_name() in processed.provider_encoded_images
    encoded_data = processed.get_encoded_data_for(provider.get_provider_name())
    assert isinstance(encoded_data, str)
    assert len(encoded_data) > 0


def test_process_image_no_encoding(provider):
    """Test processing image when provider doesn't require base64 encoding"""
    # Create test image data
    img = Image.new("RGB", (50, 50), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    test_image_data = img_bytes.getvalue()
    test_data = ImageData(
        "test.png", binary_data=test_image_data, media_type="image/png"
    )

    # Override provider config to not require encoding
    provider.image_config.requires_base64 = False

    # Process the image
    processed = provider.process_image(test_data)

    # Verify no encoded data was stored since encoding wasn't required
    assert isinstance(processed, ImageData)
    assert provider.get_provider_name() not in processed.provider_encoded_images


def test_process_real_image_greater_than_max_size(provider):
    # Create a small test image in memory
    img = Image.new("RGB", (500, 500), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    test_image_data = img_bytes.getvalue()
    image_data = ImageData(
        "test.png", binary_data=test_image_data, media_type="image/png"
    )
    # Process the actual image data
    provider.process_image(image_data)

    # Verify we get back valid base64 encoded data
    encoded_data = image_data.get_encoded_data_for("mock")
    assert isinstance(encoded_data, str)
    assert len(encoded_data) > 0

    # Verify we can decode it back to an image
    decoded = base64.b64decode(encoded_data)
    img = Image.open(BytesIO(decoded))
    assert img.size == (500, 500)


def test_encode_image(provider):
    """Test encoding image"""
    test_data = b"test image data"
    encoded = provider.encode_image(test_data)
    assert isinstance(encoded, str)
    assert len(encoded) > 0


def test_format_prompt(provider, text_message, image_registry):
    """Test formatting prompt"""
    messages = [text_message]
    config = PromptConfig()
    formatted = provider.format_prompt(messages, config, image_registry)
    assert formatted == "mock formatted prompt"
