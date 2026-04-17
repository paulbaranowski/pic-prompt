from typing import List


class ProviderNames:
    """Central registry mapping Provider subclass names to their canonical string
    identifiers (e.g., "ProviderOpenAI" -> "openai").

    Every new Provider subclass MUST be added to class_name_to_provider_name,
    or get_provider_name() will raise a ValueError at runtime.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    MOCK = "mock"

    class_name_to_provider_name = {
        "ProviderOpenAI": OPENAI,
        "ProviderAnthropic": ANTHROPIC,
        "ProviderGemini": GEMINI,
        "MockProvider": MOCK,
    }

    @classmethod
    def get_provider_name(cls, class_name: str) -> str:
        if class_name not in cls.class_name_to_provider_name:
            known = ", ".join(sorted(cls.class_name_to_provider_name.keys()))
            raise ValueError(
                f"Unknown provider class '{class_name}'. "
                f"Known provider classes: {known}. "
                f"Register new providers in ProviderNames.class_name_to_provider_name."
            )
        return cls.class_name_to_provider_name[class_name]

    @classmethod
    def get_all_names(cls) -> List[str]:
        return list(cls.class_name_to_provider_name.values())
