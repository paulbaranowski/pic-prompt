from typing import List


class ProviderNames:
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"

    class_name_to_provider_name = {
        "ProviderHelperOpenAI": OPENAI,
        "ProviderHelperAnthropic": ANTHROPIC,
        "ProviderHelperGemini": GEMINI,
    }

    @classmethod
    def get_provider_name(cls, class_name: str) -> str:
        return cls.class_name_to_provider_name[class_name]

    @classmethod
    def get_all_names(cls) -> List[str]:
        return list(cls.class_name_to_provider_name.values())
