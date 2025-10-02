"""
Pic-Prompt Package

This package provides core functionality for building prompts and handling images.
"""

try:
    from importlib.metadata import version

    __version__ = version("pic-prompt")
except Exception:
    # Fallback for development/uninstalled package
    __version__ = "dev"


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
from pic_prompt.images import ImageRegistry, ImageData, ImageLoader, ImageResizer


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
    "ImageResizer",
]
