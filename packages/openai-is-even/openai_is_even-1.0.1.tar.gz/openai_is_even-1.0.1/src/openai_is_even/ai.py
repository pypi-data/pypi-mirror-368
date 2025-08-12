import os
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel


class IsEvenResponse(BaseModel):
    is_even: bool


class IsEvenRequest(BaseModel):
    number: int


def openai_is_even(number: int) -> bool:
    """
    Check if a number is even using OpenAI.

    Args:
        number: The integer to check for evenness

    Returns:
        True if the number is even, False otherwise

    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set or invalid response
        Exception: If OpenAI API call fails
    """

    return structured_output(
        content=IsEvenRequest(number=number).model_dump_json(),
        response_format=IsEvenResponse,
    ).is_even


T = TypeVar("T", bound=BaseModel)


def structured_output(
    content: str,
    response_format: Type[T],
    model: str = "gpt-4o-mini",
) -> T:
    api_key = os.environ["OPENAI_API_KEY"]

    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable must be set")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": content,
            },
        ],
        response_format=response_format,
        max_tokens=10,
        temperature=0,
    )

    response_model = response.choices[0].message.parsed

    if not response_model:
        raise ValueError("Invalid response from OpenAI")

    return response_model
