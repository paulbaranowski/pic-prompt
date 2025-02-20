from enum import Enum


class MessageRole:
    """Types of messages that can be included in a prompt"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    IMAGE = "image"
    FUNCTION = "function"

    ALLOWED_ROLES = [SYSTEM, USER, ASSISTANT, IMAGE, FUNCTION]
