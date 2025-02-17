import os
import pytest
from prompt_any.images.sources.local_file_source import LocalFileSource
from prompt_any.images.errors import ImageSourceError


@pytest.fixture
def local_source():
    return LocalFileSource()


def test_get_image_success(tmp_path, local_source):
    data = b"imagedata"
    file_path = tmp_path / "image.jpg"
    file_path.write_bytes(data)
    result = local_source.get_image(str(file_path))
    assert result == data


def test_get_image_failure(local_source):
    with pytest.raises(ImageSourceError) as exc_info:
        local_source.get_image("nonexistent.jpg")
    assert "Failed to read" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_image_async_success(tmp_path, local_source):
    data = b"async_imagedata"
    file_path = tmp_path / "async_image.png"
    file_path.write_bytes(data)
    result = await local_source.get_image_async(str(file_path))
    assert result == data


@pytest.mark.asyncio
async def test_get_image_async_failure(local_source):
    with pytest.raises(ImageSourceError) as exc_info:
        await local_source.get_image_async("nonexistent_async.png")
    assert "Failed to read" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_image_async_ioerror(local_source):
    # Monkeypatch get_image to raise IOError directly to simulate an unexpected IOError
    def broken_get_image(path: str) -> bytes:
        raise IOError("Simulated IOError in get_image")
    local_source.get_image = broken_get_image
    with pytest.raises(ImageSourceError) as exc_info:
        await local_source.get_image_async("dummy_path")
    assert "Failed to read" in str(exc_info.value)
    assert "Simulated IOError" in str(exc_info.value)


def test_can_handle(local_source):
    # local paths should be handled
    assert local_source.can_handle("image.jpg") is True
    assert local_source.can_handle("/1/2/3/image.jpg") is True
    # remote URIs should not be handled
    assert local_source.can_handle("http://example.com/image.jpg") is False
    assert local_source.can_handle("https://example.com/image.jpg") is False
    assert local_source.can_handle("s3://bucket/image.jpg") is False
