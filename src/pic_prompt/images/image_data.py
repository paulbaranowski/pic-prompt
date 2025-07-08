import base64
from typing import Dict, Optional
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from math import sqrt
from pic_prompt.core.errors import ImageProcessingError
from pic_prompt.utils.logger import setup_logger
from pic_prompt.images.sources.local_file_source import LocalFileSource
from pic_prompt.images.image_resizer import ImageResizer

logger = setup_logger(__name__)


class ImageData:
    """A class for handling image data, including loading, encoding, and resizing operations.

    This class manages image data from various sources, providing functionality to:
    - Load images from local files or binary data
    - Convert images to different formats and encodings
    - Resize images while maintaining quality
    - Store provider-specific encoded versions
    - Access image metadata like dimensions and media type

    Attributes:
        image_obj (Image.Image): PIL Image object for image manipulation
        image_path (str): Path or URL to the image source
        binary_data (bytes): Raw binary data of the image
        media_type (str): Media/MIME type of the image
        provider_encoded_images (Dict[str, str]): Dictionary storing encoded versions for different providers
        local_file_source (LocalFileSource): Handler for local file operations
    """

    def __init__(
        self, image_path: str = None, binary_data: bytes = None, media_type: str = None
    ):
        """Initialize an ImageData instance.

        Args:
            image_path (str): Path or URL to the image
            binary_data (bytes, optional): Raw binary image data. Defaults to None.
            media_type (str, optional): Media/MIME type of the image. Defaults to None.
        """
        self.image_obj: Image.Image = None
        self.image_path: str = image_path
        self.binary_data: bytes = binary_data
        self.media_type: str = media_type
        self.provider_encoded_images: Dict[str, str] = {}
        self.local_file_source = LocalFileSource()

    def __repr__(self) -> str:
        """Return a string representation of the ImageData instance.

        Returns:
            str: A string showing the image path, binary data size, media type,
                 whether it's a local image, and any provider-encoded image sizes.
        """
        if len(self.provider_encoded_images) == 0:
            encoded_images = "none"
        else:
            encoded_images = ", ".join(
                [
                    f"{k}: {len(v)} bytes"
                    for k, v in self.provider_encoded_images.items()
                ]
            )
        return f"ImageData(image_path={self.image_path}, binary_data={len(self.binary_data) if self.binary_data else 'none'}, media_type={self.media_type}, is_local={self.is_local_image()}, encoded_images={encoded_images})"

    @property
    def image_path(self) -> str:
        """Get the image path.

        Returns:
            str: The path or URL to the image
        """
        return self._image_path

    @image_path.setter
    def image_path(self, value: str):
        """Set the image path.

        Args:
            value (str): The path or URL to the image
        """
        self._image_path = value

    def is_local_image(self) -> bool:
        """Check if the image path refers to a local file.

        Returns:
            bool: True if the image path is a local file path, False if it's a URL or other type
        """
        return self.local_file_source.can_handle(self.image_path)

    @property
    def binary_data(self) -> bytes:
        """Get the binary data of the image.

        Returns:
            bytes: The raw binary data of the image
        """
        return self._binary_data

    @binary_data.setter
    def binary_data(self, value: bytes):
        """Set the binary data of the image.

        This method also attempts to create an Image object from the binary data
        if the value is not None. If the image data is invalid or cannot be opened,
        it raises an ImageProcessingError.

        Args:
            value (bytes): The raw binary data of the image

        Raises:
            ImageProcessingError: If the image data cannot be opened or is invalid
        """
        if value is not None:
            try:
                bytes_io = BytesIO(value)
                self.image_obj = Image.open(bytes_io)
            except UnidentifiedImageError as e:
                raise ImageProcessingError(
                    f"UnidentifiedImageError opening image: {e}"
                ) from e
            except Exception as e:
                raise ImageProcessingError(
                    f"Unknown exception opening image: {e}"
                ) from e
        self._binary_data = value

    @property
    def media_type(self) -> str:
        """Get the media type of the image.

        Returns:
            str: The media type (MIME type) of the image
        """
        return self._media_type

    @media_type.setter
    def media_type(self, value: str):
        """Set the media type of the image.

        Args:
            value (str): The media type (MIME type) to set for the image
        """
        self._media_type = value

    def get_dimensions(self) -> tuple[int, int]:
        """Get the dimensions of the image.

        Returns:
            tuple[int, int]: A tuple containing the width and height of the image in pixels
        """
        return self.image_obj.size

    def add_provider_encoded_image(self, provider_name: str, encoded_image: str):
        """Store an encoded version of the image for a specific provider.

        Args:
            provider_name (str): Name of the provider (e.g. 'openai') to store the encoded image for
            encoded_image (str): The encoded image data as a string
        """
        self.provider_encoded_images[provider_name] = encoded_image

    def get_encoded_data_for(self, provider_name: str = "openai") -> Optional[str]:
        """Get the encoded image data for a specific provider.

        Args:
            provider_name (str, optional): Name of the provider to get encoded data for. Defaults to "openai".

        Returns:
            Optional[str]: The encoded image data for the specified provider if it exists

        Raises:
            ValueError: If no encoded data exists for the specified provider
        """
        if provider_name not in self.provider_encoded_images:
            raise ValueError(
                f"Encoded data not found for provider {provider_name} in ImageData for {self.image_path}"
            )
        return self.provider_encoded_images.get(provider_name)

    def encode_as_base64(self, provider_name: str = "openai") -> bytes:
        """Encode the binary image data as base64 and store it for a provider.

        Args:
            provider_name (str, optional): Name of the provider to store encoded data for. Defaults to "openai".

        Returns:
            bytes: The base64 encoded image data if binary data exists, None otherwise
        """
        if self.binary_data is not None:
            encoded_data = base64.b64encode(self.binary_data).decode("utf-8")
            self.add_provider_encoded_image(provider_name, encoded_data)
            return encoded_data
        return None

    def resize_and_encode(
        self, max_size: int, provider_name: str = "openai", resizer: ImageResizer = None
    ) -> str:
        """
        Resize and encode an image to meet provider size requirements.

        This method will resize the image if needed to meet the maximum size requirement,
        then encode it as base64. The resizing is handled by an ImageResizer instance
        which will attempt various strategies to reduce the file size while maintaining
        image quality.

        Args:
            max_size (int): Maximum allowed size in bytes for the binary image data
            provider_name (str): Name of the provider to store encoded data for. Defaults to "openai".
            resizer (ImageResizer, optional): ImageResizer instance for testing. Creates new one if None.

        Returns:
            ImageData: Self reference with the resized binary data and encoded version stored
        """
        logger.info(f"Processing image data for {self.image_path}")

        resizer = resizer or ImageResizer(target_size=max_size)
        self.binary_data = resizer.resize(self.binary_data)

        # Encode the final binary data
        self.encode_as_base64(provider_name)
        return self
