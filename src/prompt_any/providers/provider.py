"""
Base provider helper interface for handling prompt formatting and provider-specific image processing.
"""

from abc import ABC, abstractmethod
from typing import List, Union
import base64

from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage, MessageType
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.providers.provider_names import ProviderNames
from prompt_any.images.image_data import ImageData
from prompt_any.utils.logger import setup_logger

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
    ) -> str:
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

    def process_image(self, image_data: ImageData) -> str:
        """
        Process an image based on the provider's requirements.

        If the provider requires base64 encoding, this will:
        1. Encode the original image
        2. If too large, try resampling the image and re-encode
        3. If still too large, resize the image and re-encode

        The encoded image data is stored in the ImageData object for later use.

        Args:
            image_data (ImageData): The image data to process

        Returns:
            ImageData: The processed image data with encoded versions stored
        """
        if self.get_image_config().requires_base64:
            logger.info(f"Encoding image data for {image_data.image_path}")
            encoded_data = self.encode_image(image_data.binary_data)
            if len(encoded_data) > self.get_image_config().max_size:
                logger.info(
                    f"Encoded data is too large({len(encoded_data)} bytes) for {image_data.image_path}. Resampling..."
                )
                resampled_image = image_data.resample_image()
                encoded_data = self.encode_image(resampled_image)
                logger.info(f"Encoded data after resampling: {len(encoded_data)} bytes")
                # if that didn't work, try resizing
                if len(encoded_data) > self.get_image_config().max_size:
                    logger.info(
                        f"Encoded data is still too large for {image_data.image_path}. Resizing..."
                    )
                    resized_image = image_data.resize(self.get_image_config().max_size)
                    encoded_data = self.encode_image(resized_image)
                    logger.info(
                        f"Encoded data after resizing: {len(encoded_data)} bytes"
                    )
            image_data.add_provider_encoded_image(
                self.get_provider_name(), encoded_data
            )
        else:
            logger.info(
                f"Not encoding image data for {image_data} due to provider image config."
            )
        return image_data

    def encode_image(self, binary_data: bytes) -> str:
        """
        Encode an image.
        """
        return base64.b64encode(binary_data).decode("utf-8")
