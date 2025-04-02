"""
Provider helper implementation for OpenAI.
"""

from typing import List

from pic_prompt.providers.provider import Provider
from pic_prompt.core.image_config import ImageConfig
from pic_prompt.core.prompt_content import PromptContent
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.utils.logger import setup_logger

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

    def _format_content_image(
        self, content: PromptContent, all_image_data: ImageRegistry, preview=False
    ) -> str:
        """
        Format an image content based on the provider's requirements.

        Returns a dictionary containing the image URL formatted according to OpenAI's API requirements.
        """
        image_data = all_image_data.get_image_data(content.data)
        if image_data is None:
            raise ValueError(f"Image data not found for {content.data}")

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
