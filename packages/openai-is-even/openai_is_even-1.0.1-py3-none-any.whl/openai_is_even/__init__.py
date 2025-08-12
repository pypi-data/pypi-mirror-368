"""A Python package that uses OpenAI to check if numbers are even with vibe."""

from . import ai

def openai_is_even(number: int) -> bool:
    return ai.openai_is_even(number)
