# Basic usage example
builder = PromptBuilder()

# Add some messages
builder.add_system_message("You are a helpful AI assistant.")
builder.add_user_message("What is the capital of France?")
builder.add_assistant_message("The capital of France is Paris.")
builder.add_user_message("What's the population?")

# Get formatted prompt for different providers
openai_prompt = builder.get_prompt_for("openai")
# Returns JSON like:
# {
#   "messages": [
#     {"role": "system", "content": "You are a helpful AI assistant."},
#     {"role": "user", "content": "What is the capital of France?"},
#     {"role": "assistant", "content": "The capital of France is Paris."},
#     {"role": "user", "content": "What's the population?"}
#   ]
# }

# Example with image
builder = PromptBuilder()
builder.add_system_message("You are an image analysis AI.")
builder.add_image_message("https://example.com/paris.jpg")
builder.add_user_message("What landmarks do you see in this image?")

# Configure provider settings
config = PromptConfig(
    provider="openai",
    model="gpt-4-vision-preview",
    temperature=0.7,
    max_tokens=150
)
builder.add_config("openai", config)

openai_image_prompt = builder.get_prompt_for("openai")
# Returns JSON like:
# {
#   "messages": [
#     {"role": "system", "content": "You are an image analysis AI."},
#     {"role": "user", "content": [
#       {"type": "image", "image_url": "https://example.com/paris.jpg"},
#       {"type": "text", "text": "What landmarks do you see in this image?"}
#     ]}
#   ],
#   "model": "gpt-4-vision-preview",
#   "temperature": 0.7,
#   "max_tokens": 150
# }

# Example with function calling
builder = PromptBuilder()
builder.add_system_message("You can search for weather information.")
builder.add_user_message("What's the weather in Paris?")
builder.add_function_message(
    name="get_weather",
    arguments={"location": "Paris", "units": "celsius"}
)

openai_function_prompt = builder.get_prompt_for("openai")
# Returns JSON like:
# {
#   "messages": [
#     {"role": "system", "content": "You can search for weather information."},
#     {"role": "user", "content": "What's the weather in Paris?"},
#     {"role": "function", "name": "get_weather", "content": {"location": "Paris", "units": "celsius"}}
#   ]
# }

# Example with async image processing
async_builder = AsyncPromptBuilder()
async_builder.add_system_message("You are an image analysis AI.")
await async_builder.add_image_message("https://example.com/paris.jpg")

# Process multiple images in parallel
await async_builder.add_image_messages([
    "https://example.com/eiffel.jpg",
    "https://example.com/louvre.jpg"
])

prompt = await async_builder.get_prompt_for("openai")
