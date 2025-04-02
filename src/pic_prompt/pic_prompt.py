from typing import List, Dict
from pic_prompt.core import PromptMessage, PromptConfig
from pic_prompt.providers import ProviderFactory, Provider
from pic_prompt.images import ImageData
from pic_prompt.images.image_registry import ImageRegistry
from pic_prompt.providers.provider_names import ProviderNames
from pic_prompt.utils.logger import setup_logger

logger = setup_logger(__name__)


class PicPrompt:
    """
      Main Builder Class for constructing prompts for various LLM providers.

      Given this JSON structure:
      {
      "model": "gpt-4o",
      "messages": [
        {
          "role": "developer",
          "content": "You are a helpful assistant."
        },
        {
          "role": "user",
          "content": "Hello!"
        }
      ]
    }

    This class represents the whole block.
    """

    def __init__(self):
        self.configs: Dict[str, PromptConfig] = {}

        # These are the messages that will be used to build the prompt
        self.messages: List[PromptMessage] = []
        self.user_messages: List[PromptMessage] = []
        self.image_messages: List[PromptMessage] = []

        # This is the factory that will be used to get the provider helper
        self.provider_factory = ProviderFactory()

        self.providers: Dict[str, Provider] = {}
        self.init_all_providers()

        # This is the registry of all the downloaded image data
        self.image_registry = ImageRegistry()

        # This is the cache of all the prompts
        self.prompts: Dict[str, str] = {}

    def init_all_providers(self) -> None:
        prompt_config_openai = PromptConfig(
            provider_name="openai",
            model="gpt-4o",
            max_tokens=3000,
            temperature=0.0,
        )
        # prompt_config_anthropic = PromptConfig(
        #     provider_name="anthropic",
        #     model="claude-3-opus-20240229",
        #     max_tokens=3000,
        #     temperature=0.5,
        # )
        # prompt_config_gemini = PromptConfig(
        #     provider_name="gemini",
        #     model="gemini-2.0-flash",
        #     max_tokens=3000,
        #     temperature=0.0,
        # )
        self.add_config(prompt_config_openai)
        # self.add_config(prompt_config_anthropic)
        # self.add_config(prompt_config_gemini)

    # Message Methods
    def add_system_message(self, message: str) -> None:
        pm = PromptMessage(role="system")
        pm.add_text(message)
        self.messages.append(pm)

    def add_user_message(self, message: str) -> None:
        pm = PromptMessage(role="user")
        pm.add_text(message)
        self.user_messages.append(pm)

    def set_user_message(self, message: str) -> None:
        self.user_messages = []
        self.add_user_message(message)

    def add_assistant_message(self, message: str) -> None:
        pm = PromptMessage(role="assistant")
        pm.add_text(message)
        self.messages.append(pm)

    def add_image_message(self, image_path: str) -> None:
        # Initially store the raw image path. Image processing will occur in get_prompt_for.
        pm = PromptMessage(role="user")
        pm.add_image(image_path)
        self.image_registry.add_image_path(image_path)
        self.image_messages.append(pm)

    def add_image_data(self, image_data: ImageData) -> None:
        """For the case where you have already downloaded the image data."""
        self.image_registry.add_image_data(image_data)
        pm = PromptMessage(role="user")
        pm.add_image(image_data.image_path)
        self.image_messages.append(pm)

    def add_image_messages(self, image_paths: List[str]) -> None:
        for path in image_paths:
            self.add_image_message(path)

    # Config Methods
    def add_config(self, config: PromptConfig) -> None:
        if config.provider_name not in ProviderNames.get_all_names():
            raise ValueError(f"Provider {config.provider_name} is not supported")
        self.configs[config.provider_name] = config
        # Reset providers list to force re-initialization with new config
        self.providers = {}

    def get_config(self, provider: str) -> PromptConfig:
        return self.configs.get(provider, PromptConfig.default())

    def remove_config(self, provider: str) -> None:
        if provider in self.configs:
            del self.configs[provider]
            # Reset providers list to force re-initialization
            self.providers = {}

    def has_config(self, provider: str) -> bool:
        return provider in self.configs

    async def download_image_data_async(self) -> ImageRegistry:
        return await self.image_registry.download_image_data_async()

    def encode_image_data(self) -> ImageRegistry:
        for image_data in self.image_registry.get_all_image_data():
            for provider in self.get_providers().values():
                if (
                    provider.get_image_config().requires_base64
                    or image_data.is_local_image()
                ):
                    image_data.resize_and_encode(
                        provider.get_image_config().max_size,
                        provider.get_provider_name(),
                    )
        return self.image_registry

    def get_providers(self) -> Dict[str, Provider]:
        if len(self.providers) == 0:
            for provider_name, config in self.configs.items():
                helper = self.provider_factory.get_provider(config.provider_name)
                self.providers[provider_name] = helper
        return self.providers

    def build(self):
        """
        Builds prompts for all configured providers. If you want to load images asynchronously,
        call the download_image_data_async() method and then the build() method.

        This method:
        1. Downloads any required image data if needed
        2. Encodes the image data according to each provider's requirements

        The formatted prompts can be retrieved using get_content_for().
        """
        self.image_registry.download_image_data()
        self.encode_image_data()

    def get_content_for(self, provider_name: str, preview=False) -> str:
        # if len(self.prompts) == 0:
        self.build()
        provider = self.get_providers().get(provider_name)
        if provider is None:
            raise ValueError(f"Provider {provider_name} not found")
        messages = self.messages + self.user_messages + self.image_messages
        return provider.format_messages(messages, self.image_registry, preview)

    def clear(self) -> None:
        self.messages = []
        self.user_messages = []
        self.image_messages = []

    def __repr__(self) -> str:
        return f"<PromptBuilder messages={self.messages}>"
