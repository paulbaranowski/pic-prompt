import pytest
from pic_prompt.core.message_role import MessageRole


def test_message_role_values():
    """Test that message role values are correct"""
    values = MessageRole.ALLOWED_ROLES
    assert "system" in values
    assert "user" in values
    assert "assistant" in values
    assert "image" in values
    assert "function" in values
    assert len(values) == 5


def test_message_role_system():
    """Test system message role"""
    assert MessageRole.SYSTEM == "system"


def test_message_role_user():
    """Test user message role"""
    assert MessageRole.USER == "user"


def test_message_role_assistant():
    """Test assistant message role"""
    assert MessageRole.ASSISTANT == "assistant"


def test_message_role_image():
    """Test image message role"""
    assert MessageRole.IMAGE == "image"


def test_message_role_function():
    """Test function message role"""
    assert MessageRole.FUNCTION == "function"


def test_message_role_allowed_roles():
    """Test that allowed roles contains expected values"""
    assert MessageRole.ALLOWED_ROLES == [
        "system",
        "user",
        "assistant",
        "image",
        "function",
    ]
