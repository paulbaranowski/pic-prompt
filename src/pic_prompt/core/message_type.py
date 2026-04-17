from enum import Enum


class MessageType(str, Enum):
    """Classifies the content format within a PromptContent block: TEXT for
    plain strings, IMAGE for image paths or URLs. Used by
    Provider.format_content() to dispatch formatting."""

    IMAGE = "image"
    TEXT = "text"

    def __str__(self) -> str:
        return self.value
