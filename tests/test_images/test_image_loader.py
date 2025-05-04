import unittest
import asyncio
import pytest
import boto3
from pic_prompt.images.image_loader import ImageLoader
from pic_prompt.images.image_data import ImageData
from pic_prompt.core.errors import ImageProcessingError
from pic_prompt.images.sources.s3_source import S3Source
from PIL import Image
from io import BytesIO
from conftest import create_test_image


# Dummy image source for testing successful download
class DummyImageSource:
    def can_handle(self, path: str) -> bool:
        return path.startswith("dummy://")

    def get_image(self, path: str) -> bytes:
        return create_test_image()

    def get_media_type(self, path: str) -> str:
        return "image/dummy"

    async def get_image_async(self, path: str) -> bytes:
        return create_test_image()


# Dummy image source for testing failure in download
class FailingImageSource:
    def can_handle(self, path: str) -> bool:
        return path.startswith("fail://")

    def get_image(self, path: str) -> bytes:
        raise Exception("Simulated download failure")

    def get_media_type(self, path: str) -> str:
        return "image/fail"

    async def get_image_async(self, path: str) -> bytes:
        raise Exception("Simulated async download failure")


@pytest.fixture
def downloader():
    # Create an instance and override sources for controlled testing
    downloader = ImageLoader()
    # Clear default sources
    downloader.sources = {}
    return downloader


def test_in_memory_image_can_be_read():
    # Verify the bytes can be read back as an image
    img = Image.open(BytesIO(create_test_image()))
    assert img.size == (100, 100)
    assert img.mode == "RGB"
    # Get color of center pixel
    center_color = img.getpixel((50, 50))
    assert center_color[0] > 250  # Should be mostly red


def test_download_success(downloader):
    downloader.register_source("dummy", DummyImageSource())
    image_data = downloader.download("dummy://image.jpg")
    assert isinstance(image_data, ImageData)
    assert image_data.binary_data == create_test_image()
    assert image_data.media_type == "image/dummy"


def test_download_no_source(downloader):
    # Test when no registered source can handle the path
    with pytest.raises(ImageProcessingError) as exc_info:
        downloader.download("nosource://image")
    assert "No registered image source can handle path" in str(exc_info.value)


def test_download_async_success(downloader):
    downloader.register_source("dummy", DummyImageSource())

    async def run_test():
        image_data = await downloader.download_async("dummy://image")
        assert isinstance(image_data, ImageData)
        assert image_data.binary_data == create_test_image()
        assert image_data.media_type == "image/dummy"

    asyncio.run(run_test())


def test_init_with_s3_client():
    # Create a mock S3 client
    s3_client = boto3.client("s3")

    # Create downloader with S3 client
    downloader = ImageLoader(s3_client=s3_client)

    # Verify default sources are registered
    assert "file" in downloader.sources
    assert "http" in downloader.sources
    assert "https" in downloader.sources
    assert "s3" in downloader.sources

    # Verify S3 source is registered with correct client
    assert isinstance(downloader.get_source("s3"), S3Source)
    assert downloader.get_source("s3").get_source_type() == "s3"


def test_init_without_s3_client():
    # Create downloader without S3 client
    downloader = ImageLoader()

    # Verify default sources except S3 are registered
    assert "file" in downloader.sources
    assert "http" in downloader.sources
    assert "https" in downloader.sources
    assert "s3" not in downloader.sources


if __name__ == "__main__":
    unittest.main()
