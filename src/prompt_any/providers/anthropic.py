"""
Provider helper implementation for Anthropic.
"""

import base64
from typing import List, Union

from prompt_any.providers.base import ProviderHelper
from prompt_any.core.config import ImageConfig, PromptConfig
from prompt_any.core.messages import PromptMessage


class ProviderHelperAnthropic(ProviderHelper):
    """
    ProviderHelper implementation for Anthropic.
    
    Default image configuration:
        - requires_base64: True
        - max_size: 40,000,000 (40MB)
        - supported_formats: ["png", "jpeg"]
    """

    def _default_image_config(self) -> ImageConfig:
        """
        Return Anthropic's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=40_000_000,
            supported_formats=["png", "jpeg"]
        )

    def format_prompt(self, messages: List[PromptMessage], config: PromptConfig) -> str:
        """
        Format the prompt for the Anthropic provider as a plain text conversation.
        
        Each message is prefixed based on its role:
            - "Human:" for system and user messages,
            - "Assistant:" for assistant messages,
            - "Function:" for function messages.
            
        Messages are separated by a blank line.
        
        Args:
            messages (List[PromptMessage]): The list of prompt messages.
            config (PromptConfig): The configuration settings (not explicitly used here).
        
        Returns:
            str: The formatted prompt string.
        """
        lines = []
        for message in messages:
            role_lower = message.role.lower().strip()
            if role_lower == "assistant":
                prefix = "Assistant:"
            elif role_lower == "function":
                prefix = "Function:"
            else:
                prefix = "Human:"
            lines.append(f"{prefix} {message.content}")
        return "\n\n".join(lines)

    def encode_image(self, image_bytes: bytes) -> Union[str, bytes]:
        """
        Encode image bytes according to Anthropic's requirements.
        
        Since Anthropic requires base64 encoding, this method returns
        a base64-encoded string of the image bytes.
        
        Args:
            image_bytes (bytes): The raw image data.
        
        Returns:
            Union[str, bytes]: The base64-encoded image data (string).
        """
        if self.get_image_config().requires_base64:
            return base64.b64encode(image_bytes).decode("utf-8")
        return image_bytes 