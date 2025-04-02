from enum import Enum


class MessageType:
    """Types of messages that can be included in a prompt"""

    IMAGE = "image"
    TEXT = "text"

    ALLOWED_TYPES = [IMAGE, TEXT]
