from prompt_any.core.message_type import MessageType


class PromptContent:
    """A content piece in the prompt"""

    def __init__(self, content: str, type: MessageType):
        self._data = content
        self._type = type

    def __repr__(self) -> str:
        """String representation of the content"""
        return f"PromptContent(type={self.type.value}, content={self.content!r})"

    def add_text(self, text: str) -> None:
        """Add a text content piece to the message."""
        self._data = text

    def add_image(self, image_url: str) -> None:
        """Add an image content piece to the message."""
        self._data = image_url

    @property
    def data(self) -> str:
        """Get the content"""
        return self._data

    @property
    def type(self) -> MessageType:
        """Get the type"""
        return self._type

    @type.setter
    def type(self, value: MessageType) -> None:
        """Set the type"""
        self._type = value
