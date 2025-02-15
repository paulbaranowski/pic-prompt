"""
Factory class for creating ProviderHelper instances.
"""

from typing import Dict, List, Type

from prompt_any.providers.base import ProviderHelper
from prompt_any.providers.openai import ProviderHelperOpenAI
from prompt_any.providers.anthropic import ProviderHelperAnthropic
from prompt_any.providers.gemini import ProviderHelperGemini
from prompt_any.core.errors import ProviderError


class ProviderHelperFactory:
    MODEL_OPENAI = "openai"
    MODEL_ANTHROPIC = "anthropic"
    MODEL_GEMINI = "gemini"

    # Default mapping of provider names to their helper classes
    _default_helpers: Dict[str, Type[ProviderHelper]] = {
        MODEL_OPENAI: ProviderHelperOpenAI,
        MODEL_ANTHROPIC: ProviderHelperAnthropic,
        MODEL_GEMINI: ProviderHelperGemini,
    }

    def __init__(self) -> None:
        """Initialize the factory with default helper classes."""
        self._helpers: Dict[str, Type[ProviderHelper]] = self._default_helpers.copy()

    def register_helper(self, name: str, helper: Type[ProviderHelper]) -> None:
        """
        Register a new provider helper.

        Args:
            name (str): The provider's name.
            helper (Type[ProviderHelper]): The helper class for the provider.
        """
        self._helpers[name] = helper

    def get_helper(self, model: str = MODEL_OPENAI) -> ProviderHelper:
        """
        Retrieve a ProviderHelper instance for the given model/provider.

        Args:
            model (str, optional): The provider's name. Defaults to "openai".

        Returns:
            ProviderHelper: An instance of the provider helper.

        Raises:
            ProviderError: If no helper is registered for the given model.
        """
        helper_class = self._helpers.get(model)
        if helper_class is None:
            raise ProviderError(f"No provider helper registered for model '{model}'")
        return helper_class()

    def list_supported_models(self) -> List[str]:
        """Return a list of supported provider names."""
        return list(self._helpers.keys())

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported providers based on default helpers."""
        return list(cls._default_helpers.keys()) 