"""
Async version of PromptBuilder that handles asynchronous image operations.
"""

import asyncio
from typing import List

from prompt_any.builder.prompt_builder import PromptBuilder
from prompt_any.core.prompt_message import PromptMessage
from prompt_any.core.message_type import MessageType


class AsyncPromptBuilder(PromptBuilder):
    """
    Async version of PromptBuilder that processes images asynchronously.

    This class overrides methods for adding image messages and generating prompts
    so that image processing (e.g., downloading and encoding) is done asynchronously.
    """

    async def add_image_message(self, image_path: str) -> None:
        """
        Add an image message asynchronously.

        This method processes the image asynchronously using the default provider's configuration,
        then appends a PromptMessage with the processed image data.
        """
        # Use the default provider's configuration for processing the image.
        config = self.get_config(self.default_provider)
        helper = self.provider_helper_factory.get_helper(config.provider)
        processed_image = await self.image_handler.process_image_async(image_path, helper)
        self.messages.append(
            PromptMessage(
                content=processed_image,
                type=MessageType.IMAGE,
                role="user",
                source_path=image_path,
            )
        )

    async def add_image_messages(self, image_paths: List[str]) -> None:
        """
        Add multiple image messages asynchronously in parallel.

        This method launches asynchronous processing for all provided image paths.
        """
        tasks = [self.add_image_message(path) for path in image_paths]
        await asyncio.gather(*tasks)

    async def get_prompt_for(self, provider: str) -> str:
        """
        Asynchronously build and return the formatted prompt for the specified provider.

        This method processes any image messages asynchronously by using the provider's
        helper to encode image data, then returns the formatted prompt.
        """
        config = self.get_config(provider)
        helper = self.provider_helper_factory.get_helper(config.provider)

        async def process_message(message: PromptMessage) -> None:
            if message.type == MessageType.IMAGE:
                processed_image = await self.image_handler.process_image_async(message.content, helper)
                message.content = processed_image

        # Process all image messages concurrently.
        tasks = [process_message(msg) for msg in self.messages if msg.type == MessageType.IMAGE]
        if tasks:
            await asyncio.gather(*tasks)

        # Format and return the prompt.
        return helper.format_prompt(self.messages, config) 