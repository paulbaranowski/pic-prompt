import litellm
import textwrap
import logging
from pic_prompt import PicPrompt
from pic_prompt.images.image_data import ImageData
from pic_prompt.images.image_downloader import ImageLoader

logging.getLogger("pic_prompt").setLevel(logging.WARNING)

image_file = "examples/sweetgum.jpg"
image_data = ImageLoader.fetch(image_file)
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
