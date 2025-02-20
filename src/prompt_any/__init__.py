"""
Prompt-Any Package

This package provides core functionality for building prompts and handling images.
"""

from prompt_any.core import (
    PromptMessage,
    MessageType,
    PromptConfig,
    ImageConfig,
    PromptBuilderError,
    ConfigurationError,
    ProviderError,
    ImageProcessingError,
)
from prompt_any.builder import PromptBuilder

__version__ = "0.1.0"

__all__ = [
    "PromptMessage",
    "MessageType",
    "PromptConfig",
    "ImageConfig",
    "PromptBuilderError",
    "ConfigurationError",
    "ProviderError",
    "ImageProcessingError",
    "PromptBuilder",
]
