"""
Configuration classes for prompt building and image handling
"""

from typing import Optional, Dict, Any, List


class PromptConfig:
    """
    Configuration for prompt generation.
    For content generation (pic_prompt.get_content_for()), only the provider_name is required.

    Args:
        provider_name: The name of the provider to use.
        model: The model to use.
        temperature: The temperature to use.
        max_tokens: The maximum number of tokens to use.
        top_p: The top p value to use.
        json_response: Whether to return a JSON response.
        is_batch: Whether to use batch processing.
        method: The HTTP method to use.
        url: The URL to use.
    """

    def __init__(
        self,
        provider_name: str = "openai",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        json_response: bool = False,
        is_batch: bool = False,
        method: str = "POST",
        url: str = "",
    ):
        self._provider_name = provider_name.lower()
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._json_response = json_response  # Not implemented
        self._is_batch = is_batch  # Not implemented
        self._method = method
        self._url = url

    # Provider properties
    @property
    def provider_name(self) -> str:
        """Get the provider name"""
        return self._provider_name

    @provider_name.setter
    def provider_name(self, value: str) -> None:
        self._provider_name = value

    # Model properties
    @property
    def model(self) -> str:
        """Get the model name"""
        return self._model

    @model.setter
    def model(self, value: str) -> None:
        self._model = value

    # Temperature properties
    @property
    def temperature(self) -> float:
        """Get the temperature value"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._temperature = value

    # Max tokens properties
    @property
    def max_tokens(self) -> Optional[int]:
        """Get the max tokens value"""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: Optional[int]) -> None:
        self._max_tokens = value

    # Top p properties
    @property
    def top_p(self) -> Optional[float]:
        """Get the top p value"""
        return self._top_p

    @top_p.setter
    def top_p(self, value: Optional[float]) -> None:
        self._top_p = value

    # JSON response properties
    @property
    def json_response(self) -> bool:
        """Get the JSON response flag"""
        return self._json_response

    @json_response.setter
    def json_response(self, value: bool) -> None:
        self._json_response = value

    # Batch properties
    @property
    def is_batch(self) -> bool:
        """Get the batch processing flag"""
        return self._is_batch

    @is_batch.setter
    def is_batch(self, value: bool) -> None:
        self._is_batch = value

    # HTTP method properties
    @property
    def method(self) -> str:
        """Get the HTTP method"""
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        self._method = value

    # URL properties
    @property
    def url(self) -> str:
        """Get the custom URL"""
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        self._url = value

    @classmethod
    def default(cls) -> "PromptConfig":
        """Create a default configuration"""
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "provider_name": self._provider_name,
            "model": self._model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "top_p": self._top_p,
            "json_response": self._json_response,
            "is_batch": self._is_batch,
            "method": self._method,
            "url": self._url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptConfig":
        """Create config from dictionary"""
        return cls(**data)
