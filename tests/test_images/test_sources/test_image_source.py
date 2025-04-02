import pytest
from pic_prompt.images.sources.image_source import ImageSource


class DummyImageSource(ImageSource):
    """A concrete implementation of ImageSource for testing the abstract base class"""

    def get_source_type(self) -> str:
        return "dummy"

    def get_image(self, url: str) -> bytes:
        return b"test_image"

    async def get_image_async(self, url: str) -> bytes:
        return b"test_image_async"

    def can_handle(self, path: str) -> bool:
        return True

    def get_media_type(self, path: str) -> str:
        return "image/jpeg"


@pytest.fixture
def dummy_source():
    return DummyImageSource()


def test_get_source_type(dummy_source):
    """Test that get_source_type returns expected value"""
    assert dummy_source.get_source_type() == "dummy"


def test_get_image(dummy_source):
    """Test that get_image returns expected bytes"""
    result = dummy_source.get_image("test.jpg")
    assert result == b"test_image"


@pytest.mark.asyncio
async def test_get_image_async(dummy_source):
    """Test that get_image_async returns expected bytes"""
    result = await dummy_source.get_image_async("test.jpg")
    assert result == b"test_image_async"


def test_can_handle(dummy_source):
    """Test that can_handle returns expected boolean"""
    assert dummy_source.can_handle("test.jpg") is True


def test_get_media_type(dummy_source):
    """Test that get_media_type returns expected media type"""
    assert dummy_source.get_media_type("test.jpg") == "image/jpeg"


def test_abstract_class():
    """Test that ImageSource cannot be instantiated directly"""
    with pytest.raises(TypeError):
        ImageSource()
