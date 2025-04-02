import pytest
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.core.message_role import MessageRole
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.core.message_type import MessageType


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


def test_init_empty():
    """Test initializing empty message"""
    message = PromptMessage(role=MessageRole.USER)
    assert message.content == []
    assert message.role == MessageRole.USER


def test_init_with_content():
    """Test initializing with content"""
    content = [PromptContent("test", MessageType.TEXT)]
    message = PromptMessage(role=MessageRole.ASSISTANT, content=content)
    assert message.content == content
    assert message.role == MessageRole.ASSISTANT


def test_add_text(text_message):
    """Test adding text content"""
    assert len(text_message.content) == 1
    assert text_message.content[0].type == MessageType.TEXT
    assert text_message.content[0].data == "Hello world"


def test_add_image(image_message):
    """Test adding image content"""
    assert len(image_message.content) == 1
    assert image_message.content[0].type == MessageType.IMAGE
    assert image_message.content[0].data == "image.jpg"


def test_add_multiple_content():
    """Test adding multiple content pieces"""
    message = PromptMessage(role=MessageRole.USER)
    message.add_text("First text")
    message.add_image("image1.jpg")
    message.add_text("Second text")

    assert len(message.content) == 3
    assert message.content[0].type == MessageType.TEXT
    assert message.content[1].type == MessageType.IMAGE
    assert message.content[2].type == MessageType.TEXT


def test_content_setter():
    """Test setting content list"""
    message = PromptMessage(role=MessageRole.USER)
    new_content = [
        PromptContent("test1", MessageType.TEXT),
        PromptContent("test2", MessageType.TEXT),
    ]
    message.content = new_content
    assert message.content == new_content


def test_role_setter():
    """Test setting message role"""
    message = PromptMessage(role=MessageRole.USER)
    message.role = MessageRole.ASSISTANT
    assert message.role == MessageRole.ASSISTANT


def test_invalid_role():
    """Test setting invalid message role"""
    message = PromptMessage(role=MessageRole.USER)
    with pytest.raises(ValueError, match="Invalid message role: invalid_role"):
        message.role = "invalid_role"


def test_repr(text_message):
    """Test string representation"""
    expected = f"PromptMessage(role='user', content={text_message.content!r})"
    assert repr(text_message) == expected


def test_init_invalid_content():
    """Test initialization with invalid content type"""
    with pytest.raises(
        TypeError, match="All content items must be PromptContent objects"
    ):
        PromptMessage(
            role=MessageRole.USER, content=[{"type": "text", "content": "test"}]
        )
