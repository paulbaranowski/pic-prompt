import pytest
from pic_prompt.core.message_type import MessageType


def test_message_type_values():
    """Test that message type values are correct"""
    values = list(MessageType)
    assert "image" in values
    assert "text" in values
    assert len(values) == 2


def test_message_type_image():
    """Test image message type"""
    assert MessageType.IMAGE == "image"


def test_message_type_text():
    """Test text message type"""
    assert MessageType.TEXT == "text"


def test_message_type_is_str_enum():
    """Test that MessageType is a str Enum"""
    assert issubclass(MessageType, str)
    for mt in MessageType:
        assert isinstance(mt, str)


def test_message_type_membership():
    """Test Enum membership checks"""
    assert "image" in MessageType._value2member_map_
    assert "invalid" not in MessageType._value2member_map_
