"""
Core message types and classes for prompt building
"""

from typing import List
from pic_prompt.core.message_type import MessageType
from pic_prompt.core.message_role import MessageRole
from pic_prompt.core.prompt_content import PromptContent


class PromptMessage:
    """
      A message in the prompt.

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


    This class represents a single "messages" block, like so:
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
    """

    def __init__(
        self,
        role: str,
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
        if not all(isinstance(item, PromptContent) for item in content):
            raise TypeError("All content items must be PromptContent objects")
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
    def role(self, role: str) -> None:
        """Set the message role"""
        if role not in MessageRole.ALLOWED_ROLES:
            raise ValueError(f"Invalid message role: {role}")
        self._role = role

    def __repr__(self) -> str:
        """String representation of the message"""
        return f"PromptMessage(" f"role={self.role!r}, " f"content={self.content!r})"
