import pytest
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.core.message_type import MessageType


@pytest.fixture
def text_content():
    return PromptContent("Hello world", MessageType.TEXT)


@pytest.fixture
def image_content():
    return PromptContent("image.jpg", MessageType.IMAGE)


def test_init_text_content(text_content):
    """Test initializing text content"""
    assert text_content.data == "Hello world"
    assert text_content.type == MessageType.TEXT


def test_init_image_content(image_content):
    """Test initializing image content"""
    assert image_content.data == "image.jpg"
    assert image_content.type == MessageType.IMAGE


def test_add_text():
    """Test adding text content"""
    content = PromptContent("", MessageType.TEXT)
    content.add_text("New text")
    assert content.data == "New text"


def test_add_image():
    """Test adding image content"""
    content = PromptContent("", MessageType.IMAGE)
    content.add_image("new_image.jpg")
    assert content.data == "new_image.jpg"


def test_type_setter():
    """Test setting content type"""
    content = PromptContent("test", MessageType.TEXT)
    content.type = MessageType.IMAGE
    assert content.type == MessageType.IMAGE


def test_invalid_type():
    """Test setting invalid content type"""
    content = PromptContent("test", MessageType.TEXT)
    with pytest.raises(ValueError, match="Invalid message type: invalid_type"):
        content.type = "invalid_type"


def test_repr(text_content):
    """Test string representation"""
    expected = "PromptContent(type=text, content='Hello world')"
    assert repr(text_content) == expected


def test_data_property(text_content):
    """Test data property getter"""
    assert text_content.data == "Hello world"
