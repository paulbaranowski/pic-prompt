"""
Base provider helper interface for handling prompt formatting and provider-specific image processing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import base64

from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage, MessageType
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images import ImageTransformer
from prompt_any.images.image_data import ImageData
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.providers.provider_names import ProviderNames


class ProviderHelper(ABC):
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
        self._image_registry: Union[ImageRegistry, None] = None

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

    @abstractmethod
    def format_prompt(
        self,
        messages: List[PromptMessage],
        prompt_config: PromptConfig,
        all_image_data: ImageRegistry,
    ) -> str:
        """
        Format the prompt based on the list of messages and the provided configuration.

        Args:
            messages (List[PromptMessage]): The list of messages to include in the prompt.
            config (PromptConfig): The configuration settings for prompt generation.

        Returns:
            str: The formatted prompt string.
        """
        pass

    def format_messages(
        self, messages: List[PromptMessage], all_image_data: ImageRegistry
    ) -> str:
        """
        Format a list of messages based on the provider's requirements.
        """
        prompt_messages = []
        for message in messages:
            msg_dict = {
                "role": message.role,
                "content": self.format_content(message, all_image_data),
            }
            prompt_messages.append(msg_dict)
        return prompt_messages

    def format_content(
        self, message: PromptMessage, all_image_data: ImageRegistry
    ) -> str:
        """
        Format all content based on the provider's requirements.
        """
        formatted_content = []
        for content in message.content:
            if content.type == MessageType.IMAGE:
                formatted_content.append(
                    self.format_content_image(content, all_image_data)
                )
            elif content.type == MessageType.TEXT:
                formatted_content.append(self.format_content_text(content))
        return formatted_content

    @abstractmethod
    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry
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

    def process_image(self, binary_data: bytes) -> str:
        """
        Process an image based on the provider's requirements.
        """
        if self.get_image_config().requires_base64:
            encoded_data = self.encode_image(binary_data)
            if len(encoded_data) > self.get_image_config().max_size:
                resized_image = ImageTransformer.resize(binary_data)
                encoded_data = self.encode_image(resized_image)
            return encoded_data
        else:
            # should never happen
            return binary_data

    def encode_image(self, binary_data: bytes) -> str:
        """
        Encode an image.
        """
        return base64.b64encode(binary_data).decode("utf-8")
