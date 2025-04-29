import pytest
import requests
from pic_prompt.images.sources.http_source import HttpSource
from pic_prompt.images.errors import ImageSourceError
import os
import mimetypes
import aiohttp

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
    def __init__(self, response_code=200, side_effect=None):
        self.response_code = response_code
        self.side_effect = side_effect

    def get(self, url, timeout=30):
        if self.side_effect:
            raise self.side_effect
        if "error" in url:
            return DummyAiohttpResponse(self.response_code, b"")
        return DummyAiohttpResponse(self.response_code, b"async data")


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


@pytest.mark.asyncio
async def test_get_image_async_success():
    dummy_session = DummyAiohttpClientSession()
    http_source = HttpSource(async_http_client=dummy_session)
    data = await http_source.get_image_async("http://example.com/image.jpg")
    assert data == b"async data"


@pytest.mark.asyncio
async def test_get_image_async_http_error():
    dummy_session = DummyAiohttpClientSession(response_code=404)
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


def test_get_image_403_error(mocker):
    """Test that get_image raises appropriate error on 403 response"""
    mock_response = mocker.Mock()
    mock_response.status_code = 403
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    http_source = HttpSource()
    with pytest.raises(ImageSourceError) as err:
        http_source.get_image("http://example.com/forbidden")

    mock_get.assert_called_once_with(
        "http://example.com/forbidden",
        timeout=30,
        headers={"User-Agent": "pic-prompt/1.0"},
    )
    assert "Access forbidden (HTTP 403)" in str(err.value)
    assert "authentication or have rate limiting" in str(err.value)


def test_get_image_500_error(mocker):
    """Test that get_image raises appropriate error on 500 response"""
    mock_response = mocker.Mock()
    mock_response.status_code = 500
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    http_source = HttpSource()
    with pytest.raises(ImageSourceError) as err:
        http_source.get_image("http://example.com/server-error")

    mock_get.assert_called_once_with(
        "http://example.com/server-error",
        timeout=30,
        headers={"User-Agent": "pic-prompt/1.0"},
    )
    assert "HTTP 500" in str(err.value)


def test_get_image_request_exception(mocker):
    """Test that get_image raises appropriate error on RequestException"""
    mock_get = mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    http_source = HttpSource()
    with pytest.raises(ImageSourceError) as err:
        http_source.get_image("http://example.com/error")

    mock_get.assert_called_once_with(
        "http://example.com/error",
        timeout=30,
        headers={"User-Agent": "pic-prompt/1.0"},
    )
    assert "Network error downloading" in str(err.value)
    assert "Connection error" in str(err.value)


@pytest.mark.asyncio
async def test_get_image_async_403_error():
    """Test that get_image_async raises appropriate error on 403 response"""

    session = DummyAiohttpClientSession(response_code=403)

    http_source = HttpSource(async_http_client=session)
    with pytest.raises(ImageSourceError) as err:
        await http_source.get_image_async("http://example.com/forbidden")

    assert "Access forbidden (HTTP 403)" in str(err.value)
    assert "authentication or have rate limiting" in str(err.value)


@pytest.mark.asyncio
async def test_get_image_async_500_error():
    """Test that get_image_async raises appropriate error on 500 response"""

    session = DummyAiohttpClientSession(response_code=500)

    http_source = HttpSource(async_http_client=session)
    with pytest.raises(ImageSourceError) as err:
        await http_source.get_image_async("http://example.com/server-error")

    assert "HTTP 500" in str(err.value)


@pytest.mark.asyncio
async def test_get_image_async_client_error(mocker):
    """Test that get_image_async raises appropriate error on ClientError"""
    session = DummyAiohttpClientSession(
        side_effect=aiohttp.ClientError("Connection error")
    )

    http_source = HttpSource(async_http_client=session)
    with pytest.raises(ImageSourceError) as err:
        await http_source.get_image_async("http://example.com/error")

    assert "Network error downloading" in str(err.value)
    assert "Connection error" in str(err.value)
