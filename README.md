# pic-prompt

A Python library that provides a simple and flexible way to build image-based prompts for 
OpenAI. Initially it was developed to generate the prompt for different providers, but
then we discovered LiteLLM (https://www.litellm.ai/) which will translate between OpenAI
and other providers. 

It focuses on the following problems:
- Downloading images from different sources, either synchronously or asynchronously
- Encoding images 
- Handling media types (e.g. image/jpeg, image/png, etc.)
- Handling oversized images by resizing them to lower quality
- Inserting image data into prompts

It supports adding images from (Image Sources):
- URLs
- Local files
- S3 files

It is easy to add support for other providers and other image sources.

## Installation

```bash
pip install pic-prompt
```
or:

```bash
uv add pic-prompt
```

## Usage
To use the example scripts, set the OPENAI_API_KEY in your environment, typically in a `.env` file. These examples will do two queries each.

You do not need to set the OPENAI_API_KEY to actually use this library.

Example: `examples/example1.py`
This example fetches a local image and runs a LLM query on it,
and the fetches a URL and runs an LLM query on it.

Run it using: 

```
python -m examples.example1
```

/Users/paul/dev/pic-prompt/examples/example2-image-cache.pyExample: `examples/example2-image-cache.py`
This example illustrates how to pre-fetch the images before creating the prompt.
Run it using: 

```
python -m examples.example2-image-cache
```
