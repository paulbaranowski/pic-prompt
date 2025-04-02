import pytest
from pic_prompt.core.message_type import MessageType


def test_message_type_values():
    """Test that message type values are correct"""
    values = MessageType.ALLOWED_TYPES
    assert "image" in values
    assert "text" in values
    assert len(values) == 2


def test_message_type_image():
    """Test image message type"""
    assert MessageType.IMAGE == "image"


def test_message_type_text():
    """Test text message type"""
    assert MessageType.TEXT == "text"


def test_message_type_allowed_types():
    """Test that allowed types contains expected values"""
    assert MessageType.ALLOWED_TYPES == ["image", "text"]
