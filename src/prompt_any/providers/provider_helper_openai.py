"""
Provider helper implementation for OpenAI.
"""

import json
from typing import List, Dict

from prompt_any.providers.provider_helper import ProviderHelper
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.prompt_content import PromptContent


class ProviderHelperOpenAI(ProviderHelper):
    """
    ProviderHelper implementation for OpenAI.

    Default image configuration:
      - requires_base64: True
      - max_size: 20,000,000 (20MB)
      - supported_formats: ["png", "jpeg", "gif"]
    """

    def __init__(self) -> None:
        super().__init__()

        self.needs_images_downloaded = False

    def get_image_config(self) -> ImageConfig:
        """
        Return OpenAI's default image configuration.
        """
        return ImageConfig(
            requires_base64=False,
            max_size=5_000_000,
            supported_formats=["png", "jpeg", "jpg"],
            needs_download=False,
        )

    def format_prompt(
        self,
        messages: List[PromptMessage],
        prompt_config: PromptConfig,
        all_image_data: Dict[str, bytes],
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

    def format_messages(
        self, messages: List[PromptMessage], all_image_data: Dict[str, bytes]
    ) -> str:
        prompt_messages = []
        for message in messages:
            msg_dict = {
                "role": message.role,
                "content": self.format_content(message, all_image_data),
            }
            prompt_messages.append(msg_dict)
        return prompt_messages

    def format_content_image(
        self, content: PromptContent, all_image_data: Dict[str, bytes]
    ) -> str:
        """
        Format an image content based on the provider's requirements.

        Returns a dictionary containing the image URL formatted according to OpenAI's API requirements.
        """
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{content.data}"},
        }

    def format_content_text(self, content: PromptContent) -> str:
        """
        Format a text content based on the provider's requirements.
        """
        return {"type": "text", "text": content.data}
