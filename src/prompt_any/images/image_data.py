from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ImageData:
    image_path: str
    binary_data: bytes
    media_type: str
    provider_encoded_images: Dict[str, str]

    def __init__(self, image_path: str, binary_data: bytes, media_type: str):
        self.image_path = image_path
        self.binary_data = binary_data
        self.media_type = media_type
        self.provider_encoded_images = {}

    def add_provider_encoded_image(self, provider_name: str, encoded_image: str):
        self.provider_encoded_images[provider_name] = encoded_image

    def get_encoded_data_for(self, provider_name: str) -> Optional[str]:
        if provider_name not in self.provider_encoded_images:
            raise ValueError(
                f"Encoded data not found for provider {provider_name} in ImageData for {self.image_path}"
            )
        return self.provider_encoded_images.get(provider_name)
