from typing import List, Dict
from prompt_any.core import PromptMessage, PromptConfig
from prompt_any.providers import ProviderFactory, Provider
from prompt_any.images import ImageDownloader
from prompt_any.images.image_registry import ImageRegistry
from prompt_any.providers.provider_names import ProviderNames


class PromptBuilder:
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

        # These are the images that will be downloaded and processed
        self.image_list = []

        # This is the factory that will be used to get the provider helper
        self.provider_factory = ProviderFactory()

        self.providers: Dict[str, Provider] = {}

        # This is the cache of all the downloadedimage data
        # self.all_image_data: Dict[str, ImageData] = {}

        # This is the registry of all the downloaded image data
        self.image_registry = ImageRegistry()

        # This is the cache of all the prompts
        self.prompts: Dict[str, str] = {}

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

    def _should_download_images(self) -> bool:
        for provider in self.get_providers().values():
            if provider.get_image_config().needs_download:
                return True
        return False

    def download_image_data(self) -> ImageRegistry:
        """
        Downloads images if needed and stores them in the image registry.

        Only downloads images if they haven't already been downloaded and if at least one provider
        requires downloaded images. The downloaded images are stored in the image registry for reuse.

        Returns:
            ImageRegistry: The registry containing all downloaded image data
        """
        if self.image_registry.num_images() == 0:
            if self._should_download_images():
                for image in self.image_list:
                    image_data = ImageDownloader.download(image)
                    self.image_registry.add_image_data(image_data)
        return self.image_registry

    async def download_image_data_async(self) -> ImageRegistry:
        """
        Asynchronously downloads images if needed and stores them in the image registry.

        Only downloads images if they haven't already been downloaded and if at least one provider
        requires downloaded images. The downloaded images are stored in the image registry for reuse.

        Returns:
            ImageRegistry: The registry containing all downloaded image data
        """
        if self.image_registry.num_images() == 0:
            if self._should_download_images():
                for image in self.image_list:
                    image_data = await ImageDownloader.download_async(image)
                    self.image_registry.add_image_data(image_data)
        return self.image_registry

    def encode_image_data(self) -> ImageRegistry:
        for image_data in self.image_registry.get_all_image_data():
            for provider in self.get_providers().values():
                encoded_image_data = provider.process_image(image_data.binary_data)
                self.image_registry.add_provider_encoded_image(
                    image_data.image_path,
                    provider.provider_name,
                    encoded_image_data,
                )
        return self.image_registry

    def get_providers(self) -> Dict[str, Provider]:
        if len(self.providers) == 0:
            for provider_name, config in self.configs.items():
                helper = self.provider_factory.get_helper(config.provider_name)
                self.providers[provider_name] = helper
        return self.providers

    def build(self):
        """
        Builds prompts for all configured providers. If you want to load images asynchronously,
        call the download_image_data_async() method and then the build() method.

        This method:
        1. Downloads any required image data if needed
        2. Encodes the image data according to each provider's requirements
        3. Formats the prompt for each provider using their specific helper

        The formatted prompts are stored internally and can be retrieved using get_prompt_for().
        """
        self.download_image_data()
        self.encode_image_data()
        for provider in self.get_providers().values():
            self.prompts[provider.get_provider_name()] = provider.format_prompt(
                self.messages,
                self.configs[provider.get_provider_name()],
                self.image_registry,
            )

    def get_prompt_for(self, provider_name: str) -> str:
        if len(self.prompts) == 0:
            self.build()
        return self.prompts[provider_name]

    def get_content_for(self, provider_name: str) -> str:
        if len(self.prompts) == 0:
            self.build()
        provider = self.get_providers()[provider_name]
        return provider.format_messages(self.messages, self.image_registry)

    def clear(self) -> None:
        self.messages = []

    def __repr__(self) -> str:
        return f"<PromptBuilder messages={self.messages}>"
