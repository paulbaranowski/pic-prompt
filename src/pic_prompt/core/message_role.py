from enum import Enum


class MessageRole(str, Enum):
    """Defines the sender roles for a prompt message (system, user, assistant,
    image, function). The image role is a pic-prompt internal role used during
    prompt building."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    IMAGE = "image"
    FUNCTION = "function"

    def __str__(self) -> str:
        return self.value
