"""
vibeisodd: AI-powered odd number detection using GPT
"""
from typing import List, Union, Optional
import os

try:
    import openai
except ImportError:
    raise ImportError("The 'openai' package is required. Please install it with 'pip install openai'.")

__version__ = "1.0.0"

class VibeIsOddError(Exception):
    """Base exception for vibeisodd package."""
    pass

class APIKeyMissingError(VibeIsOddError):
    """Raised when the OpenAI API key is missing."""
    pass

class OpenAIRequestError(VibeIsOddError):
    """Raised when there is an error with the OpenAI API request."""
    pass

def _get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise APIKeyMissingError("OPENAI_API_KEY environment variable not set.")
    return api_key

def _ask_gpt(prompt: str, model: str = "gpt-3.5-turbo", temperature: float = 0.0) -> str:
    try:
        client = openai.OpenAI(api_key=_get_api_key())
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=5,
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        raise OpenAIRequestError(f"OpenAI API request failed: {e}")

def vibeisodd(number: Union[int, float], model: str = "gpt-3.5-turbo") -> bool:
    """
    Uses AI to determine if a number is odd.
    Returns True if odd, False if even.
    Raises VibeIsOddError for API or input errors.
    """
    if not isinstance(number, (int, float)):
        raise ValueError("Input must be an integer or float.")
    prompt = f"Is the number {number} odd? Reply only 'True' or 'False'."
    answer = _ask_gpt(prompt, model=model)
    if "true" in answer:
        return True
    elif "false" in answer:
        return False
    else:
        raise OpenAIRequestError(f"Unexpected response from OpenAI: {answer}")

def vibeisodd_batch(numbers: List[Union[int, float]], model: str = "gpt-3.5-turbo") -> List[bool]:
    """
    Uses AI to determine if each number in a list is odd.
    Returns a list of booleans.
    Raises VibeIsOddError for API or input errors.
    """
    if not isinstance(numbers, list):
        raise ValueError("Input must be a list of numbers.")
    results = []
    for n in numbers:
        results.append(vibeisodd(n, model=model))
    return results
