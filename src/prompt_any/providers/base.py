"""
Base provider helper interface for handling prompt formatting and provider-specific image processing.
"""

from abc import ABC, abstractmethod
from typing import List, Union

from prompt_any.core.config import PromptConfig, ImageConfig
from prompt_any.core.messages import PromptMessage


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
        self._image_config: ImageConfig = self._default_image_config()

    @abstractmethod
    def _default_image_config(self) -> ImageConfig:
        """
        Return the default image configuration for the provider.
        
        This should be specific to the provider's API requirements.
        """
        pass

    @abstractmethod
    def format_prompt(self, messages: List[PromptMessage], config: PromptConfig) -> str:
        """
        Format the prompt based on the list of messages and the provided configuration.
        
        Args:
            messages (List[PromptMessage]): The list of messages to include in the prompt.
            config (PromptConfig): The configuration settings for prompt generation.
        
        Returns:
            str: The formatted prompt string.
        """
        pass

    def get_image_config(self) -> ImageConfig:
        """
        Retrieve the image configuration for this provider.
        
        Returns:
            ImageConfig: The provider's image configuration.
        """
        return self._image_config

    @abstractmethod
    def encode_image(self, image_bytes: bytes) -> Union[str, bytes]:
        """
        Encode the provided image data according to the provider's requirements.
        
        Args:
            image_bytes (bytes): The raw image data.
        
        Returns:
            Union[str, bytes]: The encoded image data (e.g. base64 string or raw bytes).
        """
        pass 