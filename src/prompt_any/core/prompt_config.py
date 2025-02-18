"""
Configuration classes for prompt building and image handling
"""

from typing import Optional, Dict, Any, List


class PromptConfig:
    """Configuration for prompt generation"""

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        json_response: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
        is_batch: bool = False,
        method: str = "POST",
        url: str = "",
    ):
        self._provider = provider
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._top_p = top_p
        self._json_response = json_response
        self._json_schema = json_schema
        self._is_batch = is_batch
        self._method = method
        self._url = url

    # Provider properties
    @property
    def provider(self) -> str:
        """Get the provider name"""
        return self._provider

    @provider.setter
    def provider(self, value: str) -> None:
        self._provider = value

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

    # JSON schema properties
    @property
    def json_schema(self) -> Optional[Dict[str, Any]]:
        """Get the JSON schema"""
        return self._json_schema

    @json_schema.setter
    def json_schema(self, value: Optional[Dict[str, Any]]) -> None:
        self._json_schema = value

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
            "provider": self._provider,
            "model": self._model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "top_p": self._top_p,
            "json_response": self._json_response,
            "json_schema": self._json_schema,
            "is_batch": self._is_batch,
            "method": self._method,
            "url": self._url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptConfig":
        """Create config from dictionary"""
        return cls(**data)
