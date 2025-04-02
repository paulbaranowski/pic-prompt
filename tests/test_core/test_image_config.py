import pytest
from pic_prompt.core.image_config import ImageConfig


@pytest.fixture
def default_config():
    return ImageConfig()


@pytest.fixture
def custom_config():
    return ImageConfig(
        requires_base64=True,
        max_size=1_000_000,
        supported_formats=["png"],
        needs_download=True,
    )


def test_init_default(default_config):
    """Test initialization with default values"""
    assert default_config.requires_base64 is False
    assert default_config.max_size == 5_000_000
    assert default_config.supported_formats == ["png", "jpeg"]
    assert default_config.needs_download is False


def test_init_custom(custom_config):
    """Test initialization with custom values"""
    assert custom_config.requires_base64 is True
    assert custom_config.max_size == 1_000_000
    assert custom_config.supported_formats == ["png"]
    assert custom_config.needs_download is True


def test_to_dict(custom_config):
    """Test converting config to dictionary"""
    config_dict = custom_config.to_dict()
    assert config_dict == {
        "requires_base64": True,
        "max_size": 1_000_000,
        "supported_formats": ["png"],
        "needs_download": True,
    }


def test_from_dict():
    """Test creating config from dictionary"""
    data = {
        "requires_base64": True,
        "max_size": 2_000_000,
        "supported_formats": ["jpeg"],
        "needs_download": True,
    }
    config = ImageConfig.from_dict(data)
    assert config.requires_base64 is True
    assert config.max_size == 2_000_000
    assert config.supported_formats == ["jpeg"]
    assert config.needs_download is True


def test_from_dict_defaults():
    """Test creating config from partial dictionary uses defaults"""
    data = {"requires_base64": True}
    config = ImageConfig.from_dict(data)
    assert config.requires_base64 is True
    assert config.max_size == 5_000_000
    assert config.supported_formats is None
    assert config.needs_download is False


def test_property_getters(default_config):
    """Test property getter methods"""
    assert isinstance(default_config.requires_base64, bool)
    assert isinstance(default_config.max_size, int)
    assert isinstance(default_config.supported_formats, list)
    assert isinstance(default_config.needs_download, bool)


def test_property_setters(default_config):
    """Test property setter methods"""
    default_config.requires_base64 = True
    assert default_config.requires_base64 is True

    default_config.max_size = 2_000_000
    assert default_config.max_size == 2_000_000

    default_config.supported_formats = ["jpg", "gif"]
    assert default_config.supported_formats == ["jpg", "gif"]

    default_config.needs_download = True
    assert default_config.needs_download is True
