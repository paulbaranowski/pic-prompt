import pytest
from pic_prompt.providers.provider_names import ProviderNames


def test_get_provider_name_unknown_provider_raises():
    """Test that get_provider_name raises ValueError for an unknown provider class."""
    with pytest.raises(ValueError, match="Unknown provider class") as exc_info:
        ProviderNames.get_provider_name("NonExistentProvider")

    assert "Known provider classes" in str(exc_info.value)
