"""
Base provider helper interface for handling prompt formatting and provider-specific image processing.
"""

from abc import ABC, abstractmethod
from typing import List, Union

from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_config import PromptConfig
from pic_prompt.core.prompt_message import PromptMessage, MessageType
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.providers.provider_names import ProviderNames
from pic_prompt.utils.logger import setup_logger

logger = setup_logger(__name__)


class Provider(ABC):
    """
    Abstract base class that handles both prompt formatting and image requirements for a specific provider.

    Subclasses must implement:
      - _default_image_config()
      - format_prompt()
      - encode_image()

    The provider's image configuration can be accessed via `get_image_config()`.
    """

    def __init__(self) -> None:
        self._image_config: ImageConfig = self.get_image_config()
        self._prompt_config: Union[PromptConfig, None] = None

    def get_provider_name(self) -> str:
        """
        Return the name of the provider.
        """
        return ProviderNames.get_provider_name(self.__class__.__name__)

    @abstractmethod
    def get_image_config(self) -> ImageConfig:
        """
        Return the default image configuration for the provider.

        This should be specific to the provider's API requirements.
        """
        pass

    def format_messages(
        self,
        messages: List[PromptMessage],
        all_image_data: ImageRegistry,
        preview=False,
    ) -> str:
        """
        Format a list of messages based on the provider's requirements.
        """
        prompt_messages = []
        for message in messages:
            msg_dict = {
                "role": message.role,
                "content": self.format_content(message, all_image_data, preview),
            }
            prompt_messages.append(msg_dict)
        return prompt_messages

    def format_content(
        self, message: PromptMessage, all_image_data: ImageRegistry, preview=False
    ) -> list:
        """
        Format all content based on the provider's requirements.
        """
        formatted_content = []
        for content in message.content:
            if content.type == MessageType.IMAGE:
                formatted_content.append(
                    self._format_content_image(content, all_image_data, preview)
                )
            elif content.type == MessageType.TEXT:
                formatted_content.append(self._format_content_text(content))
        return formatted_content

    @abstractmethod
    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format an image message based on the provider's requirements.
        """
        pass

    @abstractmethod
    def _format_content_text(self, content: PromptContent) -> str:
        """
        Format a text message based on the provider's requirements.
        """
        pass
