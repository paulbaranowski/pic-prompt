"""
Provider helper implementation for Anthropic.
"""

import json
from typing import List, Dict

from prompt_any.providers.provider_helper import ProviderHelper
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images.image_data import ImageData


class ProviderHelperAnthropic(ProviderHelper):
    """
    ProviderHelper implementation for Anthropic.
    """

    def __init__(self) -> None:
        super().__init__()

    def default_image_config(self) -> ImageConfig:
        """
        Return Anthropic's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=5_000_000,
            supported_formats=["png", "jpeg", "gif", "webp"],
            needs_download=True,
        )

    def format_prompt(
        self,
        messages: List[PromptMessage],
        prompt_config: PromptConfig,
        all_image_data: Dict[str, bytes],
    ) -> str:
        self._prompt_config = prompt_config
        self._all_image_data = all_image_data
        prompt_messages = self.format_messages(messages)
        prompt = {
            "messages": prompt_messages,
            "model": prompt_config.model,
            "temperature": prompt_config.temperature,
            "max_tokens": prompt_config.max_tokens,
            "top_p": prompt_config.top_p,
        }

        if prompt_config.json_response and prompt_config.json_schema is not None:
            prompt["json_schema"] = prompt_config.json_schema

        return json.dumps(prompt)

    def format_content_text(self, content: PromptContent) -> str:
        """
        Format a text content based on Anthropic's requirements.
        """
        return {"type": "text", "text": content.data}

    def format_content_image(
        self, content: PromptContent, all_image_data: Dict[str, ImageData]
    ) -> str:
        """
        Format an image content based on Anthropic's requirements.

        Returns a dictionary containing the image data formatted according to Anthropic's API requirements.
        """
        # look up the image data in all_image_data
        image_data = all_image_data[content.data]
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_data.media_type,
                "data": image_data.encoded_data,
            },
        }
