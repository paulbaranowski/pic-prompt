# This example demonstrates how to use pic_prompt to generate image descriptions using GPT-4V
# It shows two ways to load images:
# 1. From a local file
# 2. From a URL
#
# The example uses ImageLoader.fetch() to pre-fetch and cache images before sending them
# to the model. This is useful for:
# - Avoiding repeated downloads of the same image
# - Converting images to base64 format required by the API
# - Handling both local files and URLs with the same interface
#
# To run this example:
# 1. Install required packages: pip install litellm pic_prompt
# 2. Set up your OpenAI API key as an environment variable: export OPENAI_API_KEY=<your_key>
# 3. Run:
#  cd pic-prompt
#  python -m examples.example2-image-cache

import litellm
import textwrap
import logging
from pic_prompt import PicPrompt
from pic_prompt.images.image_data import ImageData
from pic_prompt.images.image_loader import ImageLoader

logging.getLogger("pic_prompt").setLevel(logging.WARNING)

image_file = "examples/sweetgum.jpg"

# Load image bytes directly from file
with open(image_file, "rb") as f:
    image_bytes = f.read()


image_data = ImageData()
image_data.binary_data = image_bytes
image_data.media_type = "image/jpeg"

builder = PicPrompt()
builder.add_user_message("Describe this image")
builder.add_image_data(image_data)
content = builder.get_prompt()
print("\nImage file: ", image_file)
response = litellm.completion(
    model="openai/gpt-4o",
    messages=content,
)
print(
    "Image description: \n"
    + "\n".join(textwrap.wrap(response.choices[0].message.content, width=80))
    + "\n\n"
)
print("-" * 80)

# With a URL
url = "https://the-public-domain-review.imgix.net/essays/pajamas-from-spirit-land/b31359620_0002_0188-edit.jpeg?fit=clip&w=1063&h=800&auto=format,compress"
image_data = ImageLoader.fetch(url)
builder = PicPrompt()
builder.add_user_message("Describe this image")
builder.add_image_data(image_data)
content = builder.get_prompt()
response = litellm.completion(
    model="openai/gpt-4o",
    messages=content,
)
print("\nImage URL: ", url)
print(
    "Image description: \n"
    + "\n".join(textwrap.wrap(response.choices[0].message.content, width=80))
    + "\n\n"
)
