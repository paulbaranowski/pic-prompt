import pytest
import requests
from prompt_any.images.sources.http_source import HttpSource
from prompt_any.images.errors import ImageSourceError
import os
import mimetypes

REAL_IMAGE_URL = "https://hstwhmjryocigvbffybk.supabase.co/storage/v1/object/public/promptfoo_images/all-pro-dadfs.PNG"


class DummyResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


def dummy_requests_get_success(url, timeout=30, headers=None):
    return DummyResponse(200, b"imagedata")


def dummy_requests_get_failure(url, timeout=30, headers=None):
    return DummyResponse(404, b"")


def dummy_requests_get_exception(url, timeout=30, headers=None):
    raise Exception("Network error")


# Dummy aiohttp client session for synchronous tests to avoid real ClientSession creation
class DummyAiohttpClientSessionForTest:
    pass


@pytest.fixture
def http_source():
    return HttpSource(async_http_client=DummyAiohttpClientSessionForTest())


def test_get_image_success(monkeypatch, http_source):
    monkeypatch.setattr(requests, "get", dummy_requests_get_success)
    data = http_source.get_image("http://example.com/image.jpg")
    assert data == b"imagedata"


def test_get_image_http_error(monkeypatch, http_source):
    monkeypatch.setattr(requests, "get", dummy_requests_get_failure)
    with pytest.raises(ImageSourceError) as err:
        http_source.get_image("http://example.com/image.jpg")
    assert "HTTP 404" in str(err.value)


def test_get_image_exception(monkeypatch, http_source):
    monkeypatch.setattr(requests, "get", dummy_requests_get_exception)
    with pytest.raises(ImageSourceError) as err:
        http_source.get_image("http://example.com/image.jpg")
    assert "Failed to download" in str(err.value)


def test_can_handle(http_source):
    assert http_source.can_handle("http://example.com") is True
    assert http_source.can_handle("https://example.com") is True
    assert http_source.can_handle("ftp://example.com") is False


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable.",
)
def test_get_real_image_sync():
    http_source = HttpSource()
    data = http_source.get_image(REAL_IMAGE_URL)
    assert len(data) == 2516965
    assert isinstance(data, bytes)


# Async tests


class DummyAiohttpResponse:
    def __init__(self, status, content):
        self.status = status
        self._content = content

    async def read(self):
        return self._content

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class DummyAiohttpClientSession:
    def get(self, url, timeout=30):
        if "error" in url:
            return DummyAiohttpResponse(404, b"")
        return DummyAiohttpResponse(200, b"async data")


@pytest.mark.asyncio
async def test_get_image_async_success():
    dummy_session = DummyAiohttpClientSession()
    http_source = HttpSource(async_http_client=dummy_session)
    data = await http_source.get_image_async("http://example.com/image.jpg")
    assert data == b"async data"


@pytest.mark.asyncio
async def test_get_image_async_http_error():
    dummy_session = DummyAiohttpClientSession()
    http_source = HttpSource(async_http_client=dummy_session)
    with pytest.raises(ImageSourceError) as err:
        await http_source.get_image_async("http://example.com/error")
    assert "HTTP 404" in str(err.value)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are disabled. Set RUN_INTEGRATION_TESTS=1 to enable.",
)
async def test_get_real_image_async():
    http_source = HttpSource()
    data = await http_source.get_image_async(REAL_IMAGE_URL)
    assert len(data) == 2516965
    assert isinstance(data, bytes)


def test_get_source_type():
    http = HttpSource()
    assert http.get_source_type() == "http"


def test_get_media_type_known():
    http = HttpSource()
    # Using a known extension, e.g., jpg should return image/jpeg
    media_type = http.get_media_type("http://example.com/image.jpg")
    expected = mimetypes.guess_type("image.jpg")[0]
    assert media_type == expected


def test_get_media_type_unknown():
    http = HttpSource()
    media_type = http.get_media_type("http://example.com/image.unknown")
    assert media_type is None
