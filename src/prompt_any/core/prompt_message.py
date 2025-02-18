"""
Core message types and classes for prompt building
"""

from typing import List
from prompt_any.core.message_type import MessageType
from prompt_any.core.prompt_content import PromptContent


class PromptMessage:
    """A message in the prompt"""

    def __init__(
        self,
        role: str = "user",
        content: List[PromptContent] = None,
    ):
        """Initialize a prompt message

        Args:
            content: The message content (text or image data)
            type: The type of message (system, user, assistant, etc)
            role: The role of the message sender
        """
        if content is None:
            content = []
        self._content_list = content
        self._role = role

    @property
    def content(self) -> List[PromptContent]:
        """Get the message content, which is a list of content pieces (each as a dict)"""
        return self._content_list

    @content.setter
    def content(self, value: List[PromptContent]) -> None:
        """Set the message content"""
        self._content_list = value

    def add_text(self, text: str) -> None:
        """Add a text content piece to the message"""
        self._content_list.append(PromptContent(content=text, type=MessageType.TEXT))

    def add_image(self, image_url: str) -> None:
        """Add an image content piece to the message"""
        self._content_list.append(
            PromptContent(content=image_url, type=MessageType.IMAGE)
        )

    @property
    def role(self) -> str:
        """Get the message role"""
        return self._role

    @role.setter
    def role(self, value: str) -> None:
        """Set the message role"""
        self._role = value

    def __repr__(self) -> str:
        """String representation of the message"""
        return f"PromptMessage(" f"role={self.role!r}, " f"content={self.content!r})"
