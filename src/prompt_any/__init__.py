"""
Prompt-Any Package

This package provides core functionality for building prompts and handling images.
"""

from importlib.metadata import version

__version__ = version("prompt-any")


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
from prompt_any.images import ImageRegistry, ImageData, ImageDownloader


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
    "ImageRegistry",
    "ImageData",
    "ImageDownloader",
]
