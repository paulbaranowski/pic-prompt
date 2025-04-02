"""
Provider helper implementation for Anthropic.
"""

from typing import List

from pic_prompt.providers.provider import Provider
from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry


class ProviderAnthropic(Provider):
    """
    ProviderHelper implementation for Anthropic.
    """

    def __init__(self) -> None:
        super().__init__()

    def get_image_config(self) -> ImageConfig:
        """
        Return Anthropic's default image configuration.
        """
        return ImageConfig(
            requires_base64=True,
            max_size=5_000_000,
            supported_formats=["png", "jpeg", "gif", "webp"],
            needs_download=True,
        )

    def _format_content_text(self, content: PromptContent) -> str:
        """
        Format a text content based on Anthropic's requirements.
        """
        return {"type": "text", "text": content.data}

    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format an image content based on Anthropic's requirements.

        Returns a dictionary containing the image data formatted according to Anthropic's API requirements.
        """
        # look up the image data in all_image_data
        image_data = all_image_data.get_image_data(content.data)
        if image_data is None:
            raise ValueError(f"Image data not found for {content.data}")
        encoded_data = image_data.get_encoded_data_for(self.get_provider_name())
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": image_data.media_type,
                "data": f"{len(encoded_data)} bytes" if preview else encoded_data,
            },
        }
