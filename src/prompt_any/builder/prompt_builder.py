from typing import List, Dict, Optional
from prompt_any.core import PromptMessage, PromptConfig
from prompt_any.providers import ProviderHelperFactory, ProviderHelper
from prompt_any.images import ImageDownloader, ImageTransformer


class PromptBuilder:
    """Main Builder Class for constructing prompts for various LLM providers."""

    def __init__(self, configs: Optional[Dict[str, PromptConfig]] = None):
        # Use provided configs or default to openai default configuration
        self.configs: Dict[str, PromptConfig] = (
            configs if configs is not None else {"openai": PromptConfig.default()}
        )
        self.default_provider: str = list(self.configs.keys())[0]
        self.messages: List[PromptMessage] = []
        self.provider_helper_factory = ProviderHelperFactory()
        self.image_list = []

    # Message Methods
    def add_system_message(self, message: str) -> None:
        pm = PromptMessage(role="system")
        pm.add_text(message)
        self.messages.append(pm)

    def add_user_message(self, message: str) -> None:
        pm = PromptMessage(role="user")
        pm.add_text(message)
        self.messages.append(pm)

    def add_assistant_message(self, message: str) -> None:
        pm = PromptMessage(role="assistant")
        pm.add_text(message)
        self.messages.append(pm)

    def add_image_message(self, image_path: str) -> None:
        # Initially store the raw image path. Image processing will occur in get_prompt_for.
        pm = PromptMessage(role="user")
        pm.add_image(image_path)
        self.image_list.append(image_path)
        self.messages.append(pm)

    def add_image_messages(self, image_paths: List[str]) -> None:
        for path in image_paths:
            self.add_image_message(path)

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

    def get_image_data(self, provider_helper: ProviderHelper) -> Dict[str, bytes]:
        """
        Downloads and processes images based on provider requirements.

        Downloads images if the provider requires it, and encodes them in base64 if needed.
        Caches the processed image data to avoid downloading the same image multiple times.

        Args:
            provider_helper (ProviderHelper): The provider helper containing image requirements

        Returns:
            Dict[str, bytes]: Dictionary mapping image paths to their processed binary data
        """
        all_image_data = {}
        if provider_helper.get_image_config().needs_download:
            for image in self.image_list:
                image_data = ImageDownloader.download(image)
                all_image_data[image] = provider_helper.process_image(image_data)
        return all_image_data

    # Utility Methods
    def get_prompt_for(self, provider: str) -> str:
        # Retrieve the configuration; if not found, use default
        config = self.configs.get(provider, PromptConfig.default())
        helper = self.provider_helper_factory.get_helper(provider)

        # We download all the image data here to avoid downloading the same image multiple times
        # and to avoid making a lot of sync vs async functions.
        all_image_data = self.get_image_data(helper)

        # Format and return the prompt using the provider's helper
        return helper.format_prompt(self.messages, config, all_image_data)

    def clear(self) -> None:
        self.messages = []

    def __repr__(self) -> str:
        return f"<PromptBuilder messages={self.messages}>"
