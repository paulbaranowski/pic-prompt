"""
Factory class for creating ProviderHelper instances.
"""

from typing import Dict, List, Type

from pic_prompt.providers.provider import Provider
from pic_prompt.providers.provider_openai import ProviderOpenAI
from pic_prompt.providers.provider_anthropic import ProviderAnthropic
from pic_prompt.providers.provider_gemini import ProviderGemini
from pic_prompt.core.errors import ProviderError


class ProviderFactory:
    MODEL_OPENAI = "openai"
    MODEL_ANTHROPIC = "anthropic"
    MODEL_GEMINI = "gemini"

    # Class-level shared default. Instance __init__ copies this to self._providers,
    # so mutating the instance dict is safe. Do NOT mutate this class-level dict directly.
    _default_helpers: Dict[str, Type[Provider]] = {
        MODEL_OPENAI: ProviderOpenAI,
        MODEL_ANTHROPIC: ProviderAnthropic,
        MODEL_GEMINI: ProviderGemini,
    }

    def __init__(self) -> None:
        """Initialize the factory with default provider classes."""
        self._providers: Dict[str, Type[Provider]] = self._default_helpers.copy()

    def get_provider(self, model: str = MODEL_OPENAI) -> Provider:
        """
        Retrieve a Provider instance for the given model/provider.

        Args:
            model (str, optional): The provider's name. Defaults to "openai".

        Returns:
            Provider: An instance of the provider.

        Raises:
            ProviderError: If no provider is registered for the given model.
        """
        provider_class = self._providers.get(model)
        if provider_class is None:
            raise ProviderError(f"No provider registered for model '{model}'")
        return provider_class()
