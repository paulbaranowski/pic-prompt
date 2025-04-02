from pic_prompt.core.message_type import MessageType


class PromptContent:
    """
    A content piece in the prompt.

      Given the following JSON structure:
      {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            }
        ]
    }

    This class represents a single "content" block, like so:
    {
        "type": "text",
        "text": "What's in this image?"
    }

    or

    {
        "type": "image_url",
        "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
        },
    }
    """

    def __init__(self, content: str, type: str):
        self._data = content
        self._type: str = type

    def __repr__(self) -> str:
        """String representation of the content"""
        return f"PromptContent(type={self._type}, content={self._data!r})"

    def add_text(self, text: str) -> None:
        """Add a text content piece to the message."""
        self._data = text
        self._type = MessageType.TEXT

    def add_image(self, image_url: str) -> None:
        """Add an image content piece to the message."""
        self._data = image_url
        self._type = MessageType.IMAGE

    @property
    def data(self) -> str:
        """Get the content"""
        return self._data

    @property
    def type(self) -> str:
        """Get the type"""
        return self._type

    @type.setter
    def type(self, message_type: str) -> None:
        """Set the type"""
        if message_type not in MessageType.ALLOWED_TYPES:
            raise ValueError(f"Invalid message type: {message_type}")
        self._type = message_type
