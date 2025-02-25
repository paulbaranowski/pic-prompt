"""
Provider helper implementation for Gemini.
"""

import json
from typing import List, Union

from prompt_any.providers.provider import Provider
from prompt_any.core.image_config import ImageConfig
from prompt_any.core.prompt_config import PromptConfig
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.core.prompt_content import PromptContent, MessageType


class ProviderGemini(Provider):
    """
    ProviderHelper implementation for Gemini.

    Default image configuration:
        - requires_base64: False
        - max_size: 10,000,000 (10MB)
        - supported_formats: ["png", "jpeg", "webp", "heic"]
    """

    def __init__(self) -> None:
        super().__init__()

    def get_image_config(self) -> ImageConfig:
        """
        Return Gemini's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=20_000_000,
            supported_formats=[
                "image/png",
                "image/jpeg",
                "image/webp",
                "image/heic",
                "image/heif",
            ],
            needs_download=True,
        )

    def format_prompt(
        self,
        messages: List[PromptMessage],
        prompt_config: PromptConfig,
        all_image_data: ImageRegistry,
    ) -> str:
        """
        Format the prompt based on Gemini's requirements.

        Returns a JSON string containing:
        - contents: List of formatted messages from format_messages()
        - generationConfig: Settings for text generation
        - safetySettings: Default safety thresholds
        """
        formatted_messages = self.format_messages(messages, all_image_data)

        prompt = {
            "contents": formatted_messages["contents"],
            "generationConfig": {
                "maxOutputTokens": prompt_config.max_tokens,
                "temperature": prompt_config.temperature,
                "topP": prompt_config.top_p,
                "topK": 10,
            },
            # "safetySettings": [
            #     {
            #         "category": "HARM_CATEGORY_HARASSMENT",
            #         "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            #     }
            # ]
        }

        return json.dumps(prompt)

    def format_messages(
        self,
        messages: List[PromptMessage],
        all_image_data: ImageRegistry,
        preview=False,
    ) -> str:
        """
        Format a list of messages based on Gemini's requirements.

        Returns a dictionary with a "contents" key containing a list of formatted content from messages.
        The content formatting is handled by format_content().
        Image parts are placed first in the formatted contents.
        """
        formatted_contents = []
        image_messages = []
        text_messages = []

        for message in messages:
            # Check if message contains any images
            has_images = any(
                content.type == MessageType.IMAGE for content in message.content
            )
            if has_images:
                image_messages.append(message)
            else:
                text_messages.append(message)

        # Format image messages first
        for message in image_messages:
            formatted_content = self.format_content(message, all_image_data, preview)
            formatted_contents.append(formatted_content)

        # Then format text messages
        for message in text_messages:
            formatted_content = self.format_content(message, all_image_data, preview)
            formatted_contents.append(formatted_content)

        return {"contents": formatted_contents}

    def format_content(
        self, message: PromptMessage, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format all content based on Gemini's requirements.
        Returns a list containing a single dict with a "parts" key, where parts contains
        the formatted content elements (images and text) in order.
        Always puts image content before text content.
        """
        parts = []
        image_parts = []
        text_parts = []

        for content in message.content:
            if content.type == MessageType.IMAGE:
                image_parts.append(
                    self._format_content_image(content, all_image_data, preview)
                )
            elif content.type == MessageType.TEXT:
                text_parts.append(self._format_content_text(content))

        # If exactly one image and one text, put text after image
        # From the Gemini API docs:
        # "For best results, If using a single image, place the text prompt after the image."
        if len(image_parts) == 1 and len(text_parts) == 1:
            parts = image_parts + text_parts
        else:
            parts = text_parts + image_parts
        return {"role": message.role, "parts": parts}

    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format an image content based on Gemini's requirements.

        Returns a dictionary containing the image data formatted according to Gemini's API requirements.
        """
        # Look up the image data in all_image_data
        image_data = all_image_data.get_image_data(content.data)
        if image_data is None:
            raise ValueError(f"Image data not found for {content.data}")
        encoded_data = image_data.get_encoded_data_for(self.get_provider_name())
        return {
            "inline_data": {
                "mime_type": image_data.media_type,
                "data": f"{len(encoded_data)} bytes" if preview else encoded_data,
            },
        }

    def _format_content_text(self, content: PromptContent) -> str:
        """
        Format a text content based on Gemini's requirements.
        """
        return {"text": content.data}
