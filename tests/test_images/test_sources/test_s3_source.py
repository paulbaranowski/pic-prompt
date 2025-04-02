import pytest
from pic_prompt.images.sources.s3_source import S3Source
from pic_prompt.images.errors import ImageSourceError
import pytest


# Dummy synchronous S3 client which returns a successful response
class DummyS3ClientSuccess:
    def get_object(self, Bucket, Key):
        class DummyBody:
            def read(self):
                return b"test image data"

        return {"Body": DummyBody()}


# Dummy synchronous S3 client that raises an exception
class DummyS3ClientFailure:
    def get_object(self, Bucket, Key):
        raise Exception("S3 error")


# Dummy asynchronous response for S3 client
class DummyAsyncS3Response:
    def __init__(self, content):
        self._content = content

    async def read(self):
        return self._content


# Dummy asynchronous S3 client for successful response
class DummyAsyncS3ClientSuccess:
    async def get_object(self, Bucket, Key):
        return {"Body": DummyAsyncS3Response(b"async test image data")}


# Dummy asynchronous S3 client that raises an exception
class DummyAsyncS3ClientFailure:
    async def get_object(self, Bucket, Key):
        raise Exception("Async S3 error")


@pytest.fixture
def s3_source_success():
    return S3Source(DummyS3ClientSuccess())


@pytest.fixture
def s3_source_failure():
    return S3Source(DummyS3ClientFailure())


@pytest.fixture
def s3_source_async_success():
    return S3Source(DummyAsyncS3ClientSuccess())


@pytest.fixture
def s3_source_async_failure():
    return S3Source(DummyAsyncS3ClientFailure())


def test_get_image_success(s3_source_success):
    data = s3_source_success.get_image("s3://mybucket/mykey")
    assert data == b"test image data"


def test_get_image_invalid_uri(s3_source_success):
    with pytest.raises(ImageSourceError) as excinfo:
        s3_source_success.get_image("s3://invalid")
    assert "Invalid S3 URI" in str(excinfo.value)


def test_get_image_failure(s3_source_failure):
    with pytest.raises(ImageSourceError) as excinfo:
        s3_source_failure.get_image("s3://mybucket/mykey")
    assert "S3 error" in str(excinfo.value)


def test_can_handle_positive(s3_source_success):
    assert s3_source_success.can_handle("s3://bucket/key") is True


def test_can_handle_negative(s3_source_success):
    assert s3_source_success.can_handle("http://example.com") is False


@pytest.mark.asyncio
async def test_get_image_async_success(s3_source_async_success):
    data = await s3_source_async_success.get_image_async("s3://mybucket/mykey")
    assert data == b"async test image data"


@pytest.mark.asyncio
async def test_get_image_async_invalid_uri(s3_source_async_success):
    with pytest.raises(ImageSourceError) as excinfo:
        await s3_source_async_success.get_image_async("s3://invalid")
    assert "Invalid S3 URI" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_image_async_failure(s3_source_async_failure):
    with pytest.raises(ImageSourceError) as excinfo:
        await s3_source_async_failure.get_image_async("s3://mybucket/mykey")
    assert "Async S3 error" in str(excinfo.value)


def test_get_media_type(s3_source_success):
    """Test that get_media_type returns correct MIME types"""
    # Test common image types
    assert s3_source_success.get_media_type("s3://bucket/image.jpg") == "image/jpeg"
    assert s3_source_success.get_media_type("s3://bucket/image.png") == "image/png"
    assert s3_source_success.get_media_type("s3://bucket/image.gif") == "image/gif"

    # Test with nested path
    assert (
        s3_source_success.get_media_type("s3://bucket/path/to/image.jpg")
        == "image/jpeg"
    )

    # Test unknown extension
    assert s3_source_success.get_media_type("s3://bucket/image.unknown") is None
