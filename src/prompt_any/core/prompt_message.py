"""
Core message types and classes for prompt building
"""

from typing import Union, Dict, Any
from prompt_any.core.message_type import MessageType


class PromptMessage:
    """A message in the prompt"""
    
    def __init__(
        self,
        content: Union[str, bytes],
        type: Union[str, MessageType],
        role: str,
        **kwargs: Any  # For additional fields like function arguments or image data
    ):
        """Initialize a prompt message
        
        Args:
            content: The message content (text or image data)
            type: The type of message (system, user, assistant, etc)
            role: The role of the message sender
            **kwargs: Additional data specific to message type
                     (e.g., function arguments, image metadata)
        """
        self._content = content
        self._type = type
        self._role = role
        self._additional_data = kwargs

    @property
    def content(self) -> Union[str, bytes]:
        """Get the message content"""
        return self._content

    @content.setter
    def content(self, value: Union[str, bytes]) -> None:
        """Set the message content"""
        self._content = value

    @property
    def type(self) -> Union[str, MessageType]:
        """Get the message type"""
        return self._type

    @type.setter
    def type(self, value: Union[str, MessageType]) -> None:
        """Set the message type"""
        self._type = value

    @property
    def role(self) -> str:
        """Get the message role"""
        return self._role

    @role.setter
    def role(self, value: str) -> None:
        """Set the message role"""
        self._role = value

    @property
    def additional_data(self) -> Dict[str, Any]:
        """Get additional message data"""
        return self._additional_data

    @additional_data.setter
    def additional_data(self, value: Dict[str, Any]) -> None:
        """Set additional message data"""
        self._additional_data = value

    def __repr__(self) -> str:
        """String representation of the message"""
        return (
            f"PromptMessage(type={self.type.value}, "
            f"role={self.role}, "
            f"content={self.content!r})"
        ) 