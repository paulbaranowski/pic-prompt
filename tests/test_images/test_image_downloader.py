import unittest
import asyncio
import pytest
import boto3
from prompt_any.images.image_downloader import ImageDownloader
from prompt_any.images.image_data import ImageData
from prompt_any.core.errors import ImageProcessingError
from prompt_any.images.sources.s3_source import S3Source


# Dummy image source for testing successful download
class DummyImageSource:
    def can_handle(self, path: str) -> bool:
        return path.startswith("dummy://")

    def get_image(self, path: str) -> bytes:
        return b"dummy_image_data"

    def get_media_type(self, path: str) -> str:
        return "image/dummy"

    async def get_image_async(self, path: str) -> bytes:
        return b"dummy_image_data_async"


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
    # Create an ImageDownloader instance and override sources for controlled testing
    downloader = ImageDownloader()
    # Clear default sources
    downloader.sources = {}
    return downloader


def test_download_success(downloader):
    downloader.register_source("dummy", DummyImageSource())
    image_data = downloader.download("dummy://image")
    assert isinstance(image_data, ImageData)
    assert image_data.binary_data == b"dummy_image_data"
    assert image_data.media_type == "image/dummy"


def test_download_failure(downloader):
    downloader.register_source("fail", FailingImageSource())
    with pytest.raises(ImageProcessingError) as exc_info:
        downloader.download("fail://image")
    assert "Simulated download failure" in str(exc_info.value)


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
        assert image_data.binary_data == b"dummy_image_data_async"
        assert image_data.media_type == "image/dummy"

    asyncio.run(run_test())


def test_download_async_failure(downloader):
    downloader.register_source("fail", FailingImageSource())

    async def run_test():
        with pytest.raises(ImageProcessingError) as exc_info:
            await downloader.download_async("fail://image")
        assert "Simulated async download failure" in str(exc_info.value)

    asyncio.run(run_test())


def test_init_with_s3_client():
    # Create a mock S3 client
    s3_client = boto3.client("s3")

    # Create downloader with S3 client
    downloader = ImageDownloader(s3_client=s3_client)

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
    downloader = ImageDownloader()

    # Verify default sources except S3 are registered
    assert "file" in downloader.sources
    assert "http" in downloader.sources
    assert "https" in downloader.sources
    assert "s3" not in downloader.sources


if __name__ == "__main__":
    unittest.main()
