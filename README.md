# prompt-any

A Python library that provides a simple and flexible way to build image-based prompts for various LLM providers. This turns out to be a surprisingly complex problem, so I created this library to handle it.

It focuses on the following problems:
- Downloading images from different sources, either synchronously or asynchronously
- Encoding images for different providers
- Handling media types (e.g. image/jpeg, image/png, etc.)
- Handling oversized images by resizing them
- Inserting image data into prompts

It supports adding images from (Image Sources):
- URLs
- Local files
- S3 files

Current provider support:
- OpenAI
- Anthropic
- Gemini

It is easy to add support for other providers and other image sources.

## Installation

```bash
pip install prompt-any
```
or:

```bash
uv add prompt-any
```

## Usage

See the [docs](https://prompt-any.readthedocs.io/en/latest/) for more information.

## Development

See the [development docs](https://prompt-any.readthedocs.io/en/latest/development.html) for more information.

