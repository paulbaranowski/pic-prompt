"""
Provider helper implementation for Gemini.
"""

from typing import List

from pic_prompt.providers.provider import Provider
from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_message import PromptMessage
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.core.prompt_content import PromptContent, MessageType


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
            for content in message.content:
                formatted_content = self._format_content_image(
                    content, all_image_data, preview
                )
                formatted_contents.append(formatted_content)

        # Then format text messages
        for message in text_messages:
            # formatted_content = self.format_content(message, all_image_data, preview)
            for content in message.content:
                formatted_content = self._format_content_text(content)
                formatted_contents.append(formatted_content)

        return formatted_contents

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
