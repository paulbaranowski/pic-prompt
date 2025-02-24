from typing import Dict, List, Optional
from prompt_any.images.image_data import ImageData


class ImageRegistry:
    def __init__(self):
        self.image_data: Dict[str, ImageData] = {}

    def add_image_path(self, image_path: str):
        self.image_data[image_path] = ImageData(image_path)

    def add_image_data(self, image_data: ImageData):
        self.image_data[image_data.image_path] = image_data

    def add_provider_encoded_image(
        self, image_path: str, provider_name: str, encoded_image: str
    ):
        self.image_data[image_path].add_provider_encoded_image(
            provider_name, encoded_image
        )

    def num_images(self) -> int:
        return len(self.image_data)

    def get_binary_data(self, image_path: str) -> ImageData:
        return self.image_data[image_path].binary_data

    def get_all_image_data(self) -> List[ImageData]:
        return list(self.image_data.values())

    def get_all_image_paths(self) -> List[str]:
        return list(self.image_data.keys())

    def get_image_data(self, image_path: str) -> Optional[ImageData]:
        return self.image_data.get(image_path)

    def has_image(self, image_path: str) -> bool:
        return image_path in self.image_data

    def clear(self):
        self.image_data = {}
