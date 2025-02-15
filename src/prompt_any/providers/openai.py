"""
Provider helper implementation for OpenAI.
"""

import json
import base64
from typing import List, Union

from prompt_any.providers.base import ProviderHelper
from prompt_any.core.config import ImageConfig, PromptConfig
from prompt_any.core.messages import PromptMessage


class ProviderHelperOpenAI(ProviderHelper):
    """
    ProviderHelper implementation for OpenAI.
    
    Default image configuration:
      - requires_base64: True
      - max_size: 20,000,000 (20MB)
      - supported_formats: ["png", "jpeg", "gif"]
    """
    
    def _default_image_config(self) -> ImageConfig:
        """
        Return OpenAI's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=20_000_000,
            supported_formats=["png", "jpeg", "gif"]
        )
    
    def format_prompt(self, messages: List[PromptMessage], config: PromptConfig) -> str:
        """
        Format the prompt for the OpenAI provider.
        
        This implementation converts the list of PromptMessages into a JSON-formatted string.
        
        Args:
            messages (List[PromptMessage]): The list of prompt messages.
            config (PromptConfig): The configuration settings (including model parameters).
        
        Returns:
            str: A JSON string representing the prompt, e.g.:
                 {"messages": [{"role": "system", "content": "You are ..."}, ...],
                  "model": "gpt-3.5-turbo", "temperature": 0.7, ... }
        """
        prompt_messages = []
        for message in messages:
            msg_dict = {
                "role": message.role,
                "content": message.content
            }
            # Merge any additional data into the message dict
            if message.additional_data:
                msg_dict.update(message.additional_data)
            prompt_messages.append(msg_dict)
        
        prompt = {
            "messages": prompt_messages,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }
        
        if config.json_response and config.json_schema is not None:
            prompt["json_schema"] = config.json_schema
        
        return json.dumps(prompt)
    
    def encode_image(self, image_bytes: bytes) -> Union[str, bytes]:
        """
        Encode image bytes according to OpenAI's requirements.
        
        If base64 encoding is required, the raw image bytes are encoded as a base64 string;
        otherwise, raw bytes are returned.
        
        Args:
            image_bytes (bytes): The raw image data.
        
        Returns:
            Union[str, bytes]: The encoded image data.
        """
        if self._image_config.requires_base64:
            return base64.b64encode(image_bytes).decode("utf-8")
        return image_bytes 