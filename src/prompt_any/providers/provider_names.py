from typing import List


class ProviderNames:
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
        return cls.class_name_to_provider_name[class_name]

    @classmethod
    def get_all_names(cls) -> List[str]:
        return list(cls.class_name_to_provider_name.values())
