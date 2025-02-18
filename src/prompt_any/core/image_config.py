from typing import List, Dict, Any, Union


class ImageConfig:
    """Configuration for model-specific image requirements"""

    def __init__(
        self,
        requires_base64: bool = False,
        max_size: int = 5_000_000,  # 5MB default
        supported_formats: List[str] = ["png", "jpeg"],
        needs_download: bool = False,
    ):
        """Initialize image configuration

        Args:
            requires_base64: Whether images need base64 encoding
            max_size: Maximum allowed image size in bytes
            supported_formats: List of supported image formats
        """
        self._requires_base64 = requires_base64
        self._max_size = max_size
        self._supported_formats = supported_formats
        self._needs_download = needs_download

    @property
    def requires_base64(self) -> bool:
        """Whether images need to be base64 encoded"""
        return self._requires_base64

    @property
    def max_size(self) -> int:
        """Maximum allowed image size in bytes"""
        return self._max_size

    @property
    def supported_formats(self) -> List[str]:
        """List of supported image formats"""
        return self._supported_formats

    @property
    def needs_download(self) -> bool:
        """Whether images need to be downloaded"""
        return self._needs_download

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "requires_base64": self._requires_base64,
            "max_size": self._max_size,
            "supported_formats": self._supported_formats,
            "needs_download": self._needs_download,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageConfig":
        """Create config from dictionary"""
        return cls(
            requires_base64=data.get("requires_base64", False),
            max_size=data.get("max_size", 5_000_000),
            supported_formats=data.get("supported_formats", None),
            needs_download=data.get("needs_download", False),
        )
