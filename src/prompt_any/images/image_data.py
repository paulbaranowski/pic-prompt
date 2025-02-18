from dataclasses import dataclass


@dataclass
class ImageData:
    binary_data: bytes
    encoded_data: str
    media_type: str
