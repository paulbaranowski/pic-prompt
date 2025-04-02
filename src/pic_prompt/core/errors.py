"""
Core error classes for the pic_prompt library.
"""


class PromptBuilderError(Exception):
    """Base exception for errors in the prompt builder."""

    pass


class ConfigurationError(PromptBuilderError):
    """Raised when there is an error in the configuration of the prompt builder."""

    pass


class ProviderError(PromptBuilderError):
    """Raised when there is an error with provider operations."""

    pass


class ImageProcessingError(PromptBuilderError):
    """Raised when there is an error during image processing."""

    pass
