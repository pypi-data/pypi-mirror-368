# openai_is_even

A Python package that uses OpenAI to check if numbers are even ✨

## Description

Instead of using boring traditional math to check if a number is even, this package asks OpenAI's GPT model to determine the evenness of numbers with AI-powered vibes.

## Installation

```bash
pip install openai-is-even
```

Or with uv:

```bash
uv add openai-is-even
```

## Requirements

- Python >= 3.10
- OpenAI API key set in the `OPENAI_API_KEY` environment variable

## Usage

```sh
export OPENAI_API_KEY=your_key_here
```

```python
from openai_is_even import openai_is_even

# Check if numbers are even
result = openai_is_even(4)  # Returns True
result = openai_is_even(3)  # Returns False
```

## Development

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Setup

```bash
# Clone the repository
git clone https://github.com/d-costa/openai_is_even.git
cd openai_is_even

# Install dependencies
uv sync

# Set up your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

### Running Tests

```bash
uv run pytest -v
```

## Disclaimer

This package is for entertainment and educational purposes. Please use traditional mathematical operations to check if numbers are even. 😄

Inspired by <https://github.com/abyesilyurt/vibesort>
