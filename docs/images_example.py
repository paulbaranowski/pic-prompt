from pic_prompt import PicPrompt, ImageSourceError
from pic_prompt.core import PromptConfig


def main():
    # Initialize builder with image sources
    builder = PicPrompt()

    # Set up the conversation
    builder.add_system_message("You are an AI that analyzes images.")
    builder.add_user_message("I'll show you some images to analyze.")

    try:
        # Add a local image
        builder.add_image_message("./images/local_image.jpg")
        builder.add_user_message("What do you see in this image?")

        # Add multiple images from different sources
        images = [
            "https://example.com/image1.jpg",
            "/path/to/local/image2.jpg",
            "s3://my-bucket/image3.jpg",
        ]
        builder.add_image_messages(images)
        builder.add_user_message("Compare these three images.")

    except ImageSourceError as e:
        print(f"Failed to load image: {e}")
        return

    # Configure model settings
    builder.set_model("openai")
    builder.set_temperature(0.7)
    builder.set_max_tokens(500)

    # Get formatted prompts for different models
    try:
        # OpenAI format
        openai_prompt = builder.get_prompt_for("openai")
        print("OpenAI Prompt:", openai_prompt)

        # Anthropic format
        builder.set_model("anthropic")
        anthropic_prompt = builder.get_prompt_for("anthropic")
        print("Anthropic Prompt:", anthropic_prompt)

        # Gemini format
        builder.set_model("gemini")
        gemini_prompt = builder.get_prompt_for("gemini")
        print("Gemini Prompt:", gemini_prompt)

    except Exception as e:
        print(f"Failed to format prompt: {e}")


def example_with_error_handling():
    builder = PromptBuilder()

    try:
        # Try loading an image that might not exist
        builder.add_image_message("nonexistent.jpg")
    except ImageSourceError as e:
        print(f"Failed to load image: {e}")
        # Handle error appropriately

    try:
        # Try loading from URL that might be down
        builder.add_image_message("https://example.com/broken_image.jpg")
    except ImageSourceError as e:
        print(f"Failed to load URL: {e}")
        # Handle error appropriately


def example_with_batch_processing():
    builder = PromptBuilder()
    builder.add_system_message("Analyzing multiple product images.")

    # Process a batch of local images
    product_images = [
        "./products/product1.jpg",
        "./products/product2.jpg",
        "./products/product3.jpg",
    ]

    try:
        builder.add_image_messages(product_images)
        builder.add_user_message("Compare these product images.")

        prompt = builder.get_prompt_for("openai")
        print("Batch Processing Result:", prompt)

    except ImageSourceError as e:
        print(f"Failed to process batch: {e}")


def simple_example():
    # Create config
    config = PromptConfig(
        provider="openai", temperature=0.7, max_tokens=500, json_response=True
    )

    # Create builder with config
    builder = PromptBuilder(config)

    # Add messages
    builder.add_system_message("You are an AI that analyzes images.")
    builder.add_user_message("What's in this image?")
    builder.add_image_message("./cat.jpg")

    # Build the prompt
    prompt = builder.build()
    print(prompt)

    # To use different config, create new config and builder
    anthropic_config = PromptConfig(provider="anthropic", temperature=0.9)
    another_builder = PromptBuilder(anthropic_config)
    # ... add messages and build


def example_with_multiple_images():
    builder = PromptBuilder()

    # Add multiple images at once
    images = [
        "./image1.jpg",  # Local file
        "http://example/2.jpg",  # HTTP URL
        "s3://bucket/3.jpg",  # S3 path
    ]

    builder.add_image_messages(images)
    builder.add_user_message("Compare these images")

    prompt = builder.get_prompt_for("openai")
    print(prompt)


if __name__ == "__main__":
    main()
    # example_with_error_handling()
    # example_with_batch_processing()
    simple_example()
    # example_with_multiple_images()
