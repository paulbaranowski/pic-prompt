from enum import Enum


class MessageType(Enum):
    """Types of messages that can be included in a prompt"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    IMAGE = "image"
    FUNCTION = "function"