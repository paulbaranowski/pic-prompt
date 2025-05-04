# This example demonstrates how to use PicPrompt to generate image descriptions using GPT-4V
# It shows two use cases:
# 1. Getting a description of a local image file
# 2. Getting a description of an image from a URL
# The script uses litellm to make API calls and formats the output with textwrap
# Run this script with the command:
# cd pic-prompt
# python -m examples.example1

from pic_prompt import PicPrompt
import litellm
import textwrap
import logging

logging.getLogger("pic_prompt").setLevel(logging.WARNING)


image_file = "examples/sweetgum.jpg"
builder = PicPrompt()
builder.add_user_message("Describe this image")
builder.add_image_message(image_file)
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
builder = PicPrompt()
builder.add_user_message("Describe this image")
url = "https://the-public-domain-review.imgix.net/essays/pajamas-from-spirit-land/b31359620_0002_0188-edit.jpeg?fit=clip&w=1063&h=800&auto=format,compress"
builder.add_image_message(url)
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
