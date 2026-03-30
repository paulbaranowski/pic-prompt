# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pic-prompt is a Python library for building image-based prompts for LLMs. It handles downloading images from multiple sources (URLs, local files, S3), encoding them, resizing oversized images, and inserting them into OpenAI-formatted prompts. Designed for use with LiteLLM, which translates between provider formats.

## Commands

### Install dependencies
```bash
uv sync
uv pip install -e ".[test]"
```

### Run all tests (with coverage)
```bash
pytest
```

### Run a single test file
```bash
pytest tests/test_pic_prompt.py
```

### Run a single test
```bash
pytest tests/test_pic_prompt.py::TestPicPrompt::test_add_system_message -v
```

### Run only integration tests
```bash
pytest -m integration
```

### Run without integration tests
```bash
pytest -m "not integration"
```

### Format code
```bash
black src/ tests/
```

### Build package
```bash
uv build
```

### Build and publish (bumps version, runs tests, publishes to PyPI)
```bash
./build.sh <version>
```

### Run examples
```bash
python -m examples.example1
```

## Architecture

### Core Pattern: Builder + Strategy

`PicPrompt` is the main entry point — a builder that assembles messages (system, user, assistant, image) and produces a formatted prompt. The flow is:

1. Add messages/images via `PicPrompt` methods
2. Call `get_prompt()` which triggers `build()`
3. `build()` downloads images via `ImageRegistry`, then encodes them per provider config
4. Provider's `format_messages()` produces the final message list

### Key Layers

- **`core/`** — Data models: `PromptMessage`, `PromptContent`, `PromptConfig`, `ImageConfig`, error types
- **`images/`** — Image handling: `ImageRegistry` (manages collection), `ImageLoader` (download orchestrator), `ImageData` (binary data + encoding), `ImageResizer` (JPEG quality reduction to fit size limits)
- **`images/sources/`** — Strategy pattern for image sources: `ImageSource` base class with `LocalFileSource`, `HttpSource`, `S3Source`
- **`providers/`** — Strategy pattern for LLM providers: `Provider` base class with `ProviderOpenAI`, `ProviderAnthropic`, `ProviderGemini`. `ProviderFactory` creates instances. Currently only OpenAI is active since LiteLLM handles provider translation.

### Image Processing Pipeline

Images flow through: source detection (URL/local/S3) -> download (`ImageLoader`) -> store (`ImageRegistry`) -> resize if needed (`ImageResizer` via `ImageData.resize_and_encode()`) -> base64 encode -> embed in prompt

### Public API (exported from `__init__.py`)

`PicPrompt`, `ImageRegistry`, `ImageData`, `ImageLoader`, `ImageResizer`, `PromptMessage`, `PromptConfig`, `ImageConfig`, error classes

## Testing

- pytest with pytest-asyncio (async mode: auto)
- Coverage tracked via `--cov=pic_prompt`
- `PYTHONPATH=src` is set automatically in pytest.ini
- Integration tests require `RUN_INTEGRATION_TESTS=1` (set in pytest.ini by default)
- Test image fixture: `in_memory_image` in `conftest.py` creates a test JPEG

## Publishing

- **PyPI**: via GitHub Actions on `v*` tags (OIDC auth), or manually via `./build.sh`
- **Gemfury**: via GitHub Actions on `v*` tags
- Build backend: hatchling
- Package version lives in `pyproject.toml`
