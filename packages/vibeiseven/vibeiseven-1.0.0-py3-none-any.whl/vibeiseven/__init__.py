"""
VibeIsEven: AI-powered even number detection using GPT or Gemini.
"""

from typing import List, Optional
import os

__version__ = "1.0.0"

class VibeIsEvenError(Exception):
    """Base exception for VibeIsEven errors."""
    pass

class MissingAPIKeyError(VibeIsEvenError):
    """Raised when the required API key is missing."""
    pass

class APIProviderError(VibeIsEvenError):
    """Raised when there is an error with the LLM provider."""
    pass

def vibeiseven(number: int, provider: str = 'openai', api_key: Optional[str] = None) -> bool:
    """
    Determines if a number is even by asking an LLM provider.

    Args:
        number (int): The number to check.
        provider (str): 'openai' or 'gemini'.
        api_key (Optional[str]): API key for the provider. If None, uses environment variable.

    Returns:
        bool: True if even, False if odd.

    Raises:
        MissingAPIKeyError: If the API key is missing.
        APIProviderError: If the provider fails or is unsupported.
    """
    if provider not in ('openai', 'gemini'):
        raise APIProviderError(f"Unsupported provider: {provider}")

    if provider == 'openai':
        key = api_key or os.getenv('OPENAI_API_KEY')
        if not key:
            raise MissingAPIKeyError("OPENAI_API_KEY is not set.")
        try:
            import openai
            openai.api_key = key
            prompt = f"Is the number {number} even? Answer only 'Yes' or 'No'."
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content.strip().lower()
            return answer.startswith('yes')
        except Exception as e:
            raise APIProviderError(f"OpenAI error: {e}")

    elif provider == 'gemini':
        key = api_key or os.getenv('GEMINI_API_KEY')
        if not key:
            raise MissingAPIKeyError("GEMINI_API_KEY is not set.")
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            prompt = f"Is the number {number} even? Answer only 'Yes' or 'No'."
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            answer = response.text.strip().lower()
            return answer.startswith('yes')
        except Exception as e:
            raise APIProviderError(f"Gemini error: {e}")

    raise APIProviderError("Unknown error.")

def vibeiseven_batch(numbers: List[int], provider: str = 'openai', api_key: Optional[str] = None) -> List[bool]:
    """
    Batch process a list of numbers to determine if each is even using an LLM provider.

    Args:
        numbers (List[int]): List of numbers to check.
        provider (str): 'openai' or 'gemini'.
        api_key (Optional[str]): API key for the provider. If None, uses environment variable.

    Returns:
        List[bool]: List of results (True for even, False for odd).
    """
    return [vibeiseven(n, provider=provider, api_key=api_key) for n in numbers]
