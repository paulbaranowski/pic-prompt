from pic_prompt import PromptBuilder
import litellm
import textwrap
import logging

logging.getLogger("pic_prompt").setLevel(logging.WARNING)


image_file = "examples/sweetgum.jpg"
builder = PromptBuilder()
builder.add_user_message("Describe this image")
builder.add_image_message(image_file)
content = builder.get_content_for("openai")
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
builder = PromptBuilder()
builder.add_user_message("Describe this image")
url = "https://the-public-domain-review.imgix.net/essays/pajamas-from-spirit-land/b31359620_0002_0188-edit.jpeg?fit=clip&w=1063&h=800&auto=format,compress"
builder.add_image_message(url)
content = builder.get_content_for("openai")
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
