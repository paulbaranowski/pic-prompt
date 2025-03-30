"""
Provider helper implementation for OpenAI.
"""

import json
from typing import List

from prompt_any.providers.provider import Provider
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.utils.logger import setup_logger

logger = setup_logger(__name__)


class ProviderOpenAI(Provider):
    """
    ProviderHelper implementation for OpenAI.

    Default image configuration:
      - requires_base64: True
      - max_size: 20,000,000 (20MB)
      - supported_formats: ["png", "jpeg", "gif"]
    """

    def __init__(self) -> None:
        super().__init__()

    def get_image_config(self) -> ImageConfig:
        """
        Return OpenAI's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=20_000_000,
            supported_formats=["png", "jpeg", "jpg"],
            needs_download=True,
        )

    def format_prompt(
        self,
        messages: List[PromptMessage],
        prompt_config: PromptConfig,
        all_image_data: ImageRegistry,
    ) -> str:
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
        self._prompt_config = prompt_config
        self._all_image_data = all_image_data
        prompt_messages = self.format_messages(messages, all_image_data)
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

    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format an image content based on the provider's requirements.

        Returns a dictionary containing the image URL formatted according to OpenAI's API requirements.
        """
        image_data = all_image_data.get_image_data(content.data)
        logger.info(f"image_data: {image_data}")
        if self._image_config.requires_base64 or image_data.is_local_image():
            encoded_data = image_data.get_encoded_data_for(self.get_provider_name())
            encoded_data = f"{len(encoded_data)} bytes" if preview else encoded_data
            return {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{encoded_data}"},
            }
        else:
            return {
                "type": "image_url",
                "image_url": {"url": content.data},
            }

    def _format_content_text(self, content: PromptContent) -> str:
        """
        Format a text content based on the provider's requirements.
        """
        return {"type": "text", "text": content.data}
