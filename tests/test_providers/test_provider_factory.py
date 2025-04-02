import pytest

from pic_prompt.providers.provider_factory import ProviderFactory
from pic_prompt.providers.provider_openai import ProviderOpenAI
from pic_prompt.providers.provider_anthropic import ProviderAnthropic
from pic_prompt.providers.provider_gemini import ProviderGemini
from pic_prompt.core.errors import ProviderError


def test_get_provider_default():
    """Test getting default (OpenAI) provider"""
    factory = ProviderFactory()
    provider = factory.get_provider()
    assert isinstance(provider, ProviderOpenAI)


def test_get_provider_openai():
    """Test getting OpenAI provider explicitly"""
    factory = ProviderFactory()
    provider = factory.get_provider(ProviderFactory.MODEL_OPENAI)
    assert isinstance(provider, ProviderOpenAI)


def test_get_provider_anthropic():
    """Test getting Anthropic provider"""
    factory = ProviderFactory()
    provider = factory.get_provider(ProviderFactory.MODEL_ANTHROPIC)
    assert isinstance(provider, ProviderAnthropic)


def test_get_provider_gemini():
    """Test getting Gemini provider"""
    factory = ProviderFactory()
    provider = factory.get_provider(ProviderFactory.MODEL_GEMINI)
    assert isinstance(provider, ProviderGemini)


def test_get_provider_invalid():
    """Test getting invalid provider raises error"""
    factory = ProviderFactory()
    with pytest.raises(ProviderError) as exc_info:
        factory.get_provider("invalid_provider")
    assert "No provider registered for model 'invalid_provider'" in str(exc_info.value)
