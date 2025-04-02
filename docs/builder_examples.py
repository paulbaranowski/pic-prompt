from pic_prompt.builder import PicPrompt
from pic_prompt.core.prompt_config import PromptConfig


# Synchronous usage
config = PromptConfig(
    provider_name="openai",
    model="gpt-4o",
    temperature=0.5,
    max_tokens=3000,
    url="https://api.openai.com/v1/chat/completions",
)
builder = PicPrompt(configs=[config])
builder.add_system_message("You are an image analysis AI.")
builder.add_user_message("Return the text on the image.")
builder.add_image_message("/path/to/local/image.jpg")

# If you want to asynchronously download the image data, use the following at this point:
# await builder.download_image_data_async()

openai_prompt = builder.get_prompt_for("openai")
anthropic_prompt = builder.get_prompt_for("anthropic")
gemini_prompt = builder.get_prompt_for("gemini")

# Or just get the content for a specific provider:
openai_content = builder.get_content_for("openai")
anthropic_content = builder.get_content_for("anthropic")
gemini_content = builder.get_content_for("gemini")
