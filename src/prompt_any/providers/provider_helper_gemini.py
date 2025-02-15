"""
Provider helper implementation for Gemini.
"""

import json
from typing import List, Union

from prompt_any.providers.provider_helper import ProviderHelper
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage


class ProviderHelperGemini(ProviderHelper):
    """
    ProviderHelper implementation for Gemini.
    
    Default image configuration:
        - requires_base64: False
        - max_size: 10,000,000 (10MB)
        - supported_formats: ["png", "jpeg", "webp", "heic"]
    """

    def _default_image_config(self) -> ImageConfig:
        """
        Return Gemini's default image configuration.
        """
        return ImageConfig(
            requires_base64=False,
            max_size=10_000_000,
            supported_formats=["png", "jpeg", "webp", "heic"]
        )

    def format_prompt(self, messages: List[PromptMessage], config: PromptConfig) -> str:
        """
        Format the prompt for the Gemini provider.
        
        This method formats the prompt as a JSON object with a key "contents" which is a list of message entries.
        Each entry is a dictionary with:
            - "role": for the sender role; the "assistant" role is mapped to "model"
            - "parts": a list containing one dictionary with the message text.
        
        Example JSON:
        {
            "contents": [
                {"role": "user", "parts": [{"text": "You are a helpful AI assistant."}]},
                {"role": "user", "parts": [{"text": "What is the capital of France?"}]},
                {"role": "model", "parts": [{"text": "The capital of France is Paris."}]},
                {"role": "user", "parts": [{"text": "What's the population?"}]}
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150,
            "top_p": 1.0
        }
        
        Args:
            messages (List[PromptMessage]): The list of prompt messages.
            config (PromptConfig): The configuration settings, including model parameters.
        
        Returns:
            str: A JSON string representing the formatted prompt.
        """
        contents = []
        for message in messages:
            # Map "assistant" role to "model" for Gemini, other roles remain the same.
            role = message.role.lower().strip()
            formatted_role = "model" if role == "assistant" else role
            entry = {
                "role": formatted_role,
                "parts": [{"text": str(message.content)}]
            }
            # If there are any additional data fields, merge them into the entry.
            if message.additional_data:
                entry.update(message.additional_data)
            contents.append(entry)
        
        prompt = {
            "contents": contents,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p
        }
        
        if config.json_response and config.json_schema is not None:
            prompt["json_schema"] = config.json_schema
        
        return json.dumps(prompt)

    def encode_image(self, image_bytes: bytes) -> Union[str, bytes]:
        """
        Encode image bytes according to Gemini's requirements.
        
        Since Gemini's default configuration does not require base64 encoding, this method simply returns the raw bytes.
        However, if the configuration is updated to require base64, it will return a base64-encoded string.
        
        Args:
            image_bytes (bytes): The raw image data.
        
        Returns:
            Union[str, bytes]: The encoded image data.
        """
        if self.get_image_config().requires_base64:
            import base64
            return base64.b64encode(image_bytes).decode("utf-8")
        return image_bytes 