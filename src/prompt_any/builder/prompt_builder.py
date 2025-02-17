from typing import List, Dict, Optional, Any
from prompt_any.core import PromptMessage, MessageType, PromptConfig
from prompt_any.providers import ProviderHelperFactory
from prompt_any.images import ImageDownloader


class PromptBuilder:
    """Main Builder Class for constructing prompts for various LLM providers."""
    def __init__(self, configs: Optional[Dict[str, PromptConfig]] = None):
        # Use provided configs or default to openai default configuration
        self.configs: Dict[str, PromptConfig] = configs if configs is not None else {"openai": PromptConfig.default()}
        self.default_provider: str = list(self.configs.keys())[0]
        self.messages: List[PromptMessage] = []
        self.provider_helper_factory = ProviderHelperFactory()

    # Message Methods
    def add_system_message(self, message: str) -> None:
        self.messages.append(PromptMessage(content=message, type=MessageType.SYSTEM, role="system"))

    def add_user_message(self, message: str) -> None:
        self.messages.append(PromptMessage(content=message, type=MessageType.USER, role="user"))

    def add_assistant_message(self, message: str) -> None:
        self.messages.append(PromptMessage(content=message, type=MessageType.ASSISTANT, role="assistant"))

    def add_image_message(self, image_path: str) -> None:
        # Initially store the raw image path. Image processing will occur in get_prompt_for.
        self.messages.append(PromptMessage(content=image_path, type=MessageType.IMAGE, role="user"))

    def add_image_messages(self, image_paths: List[str]) -> None:
        for path in image_paths:
            self.add_image_message(path)

    def add_function_message(self, name: str, arguments: Dict[str, Any]) -> None:
        # Create a function message. The function name is stored as content and arguments as additional data.
        self.messages.append(PromptMessage(content=name, type=MessageType.FUNCTION, role="function", arguments=arguments))

    # Config Methods
    def add_config(self, provider: str, config: PromptConfig) -> None:
        self.configs[provider] = config

    def get_config(self, provider: str) -> PromptConfig:
        return self.configs.get(provider, PromptConfig.default())

    def remove_config(self, provider: str) -> None:
        if provider in self.configs:
            del self.configs[provider]

    def has_config(self, provider: str) -> bool:
        return provider in self.configs

    # Utility Methods
    def get_prompt_for(self, provider: str) -> str:
        # Retrieve the configuration; if not found, use default
        config = self.configs.get(provider, PromptConfig.default())
        helper = self.provider_helper_factory.get_helper(provider)

        # Format and return the prompt using the provider's helper
        return helper.format_prompt(self.messages, config)

    def clear(self) -> None:
        self.messages = []

    def __repr__(self) -> str:
        return f"<PromptBuilder messages={self.messages}>" 