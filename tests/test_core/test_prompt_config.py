import pytest
from pic_prompt.core.prompt_config import PromptConfig


@pytest.fixture
def default_config():
    return PromptConfig.default()


@pytest.fixture
def custom_config():
    return PromptConfig(
        provider_name="anthropic",
        model="claude-2",
        temperature=0.5,
        max_tokens=1000,
        top_p=0.9,
        json_response=True,
        is_batch=True,
        method="GET",
        url="https://api.example.com",
    )


def test_default_config(default_config):
    """Test default configuration values"""
    assert default_config.provider_name == "openai"
    assert default_config.model == "gpt-3.5-turbo"
    assert default_config.temperature == 0.7
    assert default_config.max_tokens is None
    assert default_config.top_p is None
    assert default_config.json_response is False
    assert default_config.is_batch is False
    assert default_config.method == "POST"
    assert default_config.url == ""


def test_custom_config(custom_config):
    """Test custom configuration values"""
    assert custom_config.provider_name == "anthropic"
    assert custom_config.model == "claude-2"
    assert custom_config.temperature == 0.5
    assert custom_config.max_tokens == 1000
    assert custom_config.top_p == 0.9
    assert custom_config.json_response is True
    assert custom_config.is_batch is True
    assert custom_config.method == "GET"
    assert custom_config.url == "https://api.example.com"


def test_config_setters(default_config):
    """Test setting configuration values"""
    default_config.provider_name = "gemini"
    default_config.model = "gemini-pro"
    default_config.temperature = 0.3
    default_config.max_tokens = 500
    default_config.top_p = 0.8
    default_config.json_response = True
    default_config.is_batch = True
    default_config.method = "PUT"
    default_config.url = "https://custom.api.com"

    assert default_config.provider_name == "gemini"
    assert default_config.model == "gemini-pro"
    assert default_config.temperature == 0.3
    assert default_config.max_tokens == 500
    assert default_config.top_p == 0.8
    assert default_config.json_response is True
    assert default_config.is_batch is True
    assert default_config.method == "PUT"
    assert default_config.url == "https://custom.api.com"


def test_to_dict(custom_config):
    """Test converting config to dictionary"""
    config_dict = custom_config.to_dict()
    expected = {
        "provider_name": "anthropic",
        "model": "claude-2",
        "temperature": 0.5,
        "max_tokens": 1000,
        "top_p": 0.9,
        "json_response": True,
        "is_batch": True,
        "method": "GET",
        "url": "https://api.example.com",
    }
    assert config_dict == expected


def test_from_dict():
    """Test creating config from dictionary"""
    config_data = {
        "provider_name": "anthropic",
        "model": "claude-2",
        "temperature": 0.5,
        "max_tokens": 1000,
        "top_p": 0.9,
        "json_response": True,
        "is_batch": True,
        "method": "GET",
        "url": "https://api.example.com",
    }
    config = PromptConfig.from_dict(config_data)

    assert config.provider_name == "anthropic"
    assert config.model == "claude-2"
    assert config.temperature == 0.5
    assert config.max_tokens == 1000
    assert config.top_p == 0.9
    assert config.json_response is True
    assert config.is_batch is True
    assert config.method == "GET"
    assert config.url == "https://api.example.com"
