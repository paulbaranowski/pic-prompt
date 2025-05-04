"""
Pic-Prompt Package

This package provides core functionality for building prompts and handling images.
"""

from importlib.metadata import version

__version__ = version("pic-prompt")


from pic_prompt.core import (
    PromptMessage,
    MessageType,
    PromptConfig,
    ImageConfig,
    PromptBuilderError,
    ConfigurationError,
    ProviderError,
    ImageProcessingError,
)
from .pic_prompt import PicPrompt
from pic_prompt.images import ImageRegistry, ImageData, ImageLoader


__all__ = [
    "PromptMessage",
    "MessageType",
    "PromptConfig",
    "ImageConfig",
    "PromptBuilderError",
    "ConfigurationError",
    "ProviderError",
    "ImageProcessingError",
    "PicPrompt",
    "ImageRegistry",
    "ImageData",
    "ImageLoader",
]
