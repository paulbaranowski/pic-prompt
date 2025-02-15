# Synchronous usage
builder = PromptBuilder()
builder.add_system_message("You are an image analysis AI.")
builder.add_image_message("/path/to/local/image.jpg")  # Blocks until complete
prompt = builder.get_prompt_for("openai")

# Asynchronous usage
async_builder = AsyncPromptBuilder()
async_builder.add_system_message("You are an image analysis AI.")
await async_builder.add_image_message("https://example.com/image.jpg")
# Process multiple images in parallel
await async_builder.add_image_messages([
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
])
prompt = await async_builder.get_prompt_for("openai") 