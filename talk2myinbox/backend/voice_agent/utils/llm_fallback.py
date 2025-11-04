"""
LLM Fallback Chain - Multi-Provider AI with Automatic Failover
Tries providers in order: Euron → DeepSeek → Google Gemini → OpenAI
"""

import os
import requests
from typing import Optional


def call_llm_with_fallback(prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
    """
    Call LLM providers with automatic fallback.

    Fallback chain:
    1. Euron API (primary - cost-effective)
    2. DeepSeek (fallback 1 - affordable)
    3. Google Gemini (fallback 2 - reliable)
    4. OpenAI (fallback 3 - high quality)

    Args:
        prompt: The prompt to send to the AI
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)

    Returns:
        The AI's response text

    Raises:
        Exception: If all providers fail
    """

    providers = [
        ("Euron", _call_euron_api),
        ("DeepSeek", _call_deepseek_api),
        ("Google Gemini", _call_gemini_api),
        ("OpenAI", _call_openai_api)
    ]

    errors = []

    for provider_name, provider_func in providers:
        try:
            print(f"[LLM Fallback] Trying {provider_name}...")
            response = provider_func(prompt, max_tokens, temperature)
            if response:
                print(f"[LLM Fallback] [OK] SUCCESS with {provider_name}")
                return response
        except Exception as e:
            error_msg = f"{provider_name} failed: {str(e)}"
            print(f"[LLM Fallback] [ERROR] {error_msg}")
            errors.append(error_msg)
            continue

    # All providers failed
    error_summary = "; ".join(errors)
    raise Exception(f"All LLM providers failed: {error_summary}")


def _call_euron_api(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Call Euron API"""
    api_key = os.getenv("EURON_API_KEY")
    api_base = os.getenv("EURON_API_BASE", "https://api.euron.one/api/v1/euri")
    model = os.getenv("EURON_MODEL", "gpt-4.1-nano")

    if not api_key or api_key == "your_euron_api_key_here":
        raise ValueError("EURON_API_KEY not configured")

    response = requests.post(
        f"{api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_deepseek_api(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Call DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

    if not api_key or api_key == "your_deepseek_api_key_here":
        raise ValueError("DEEPSEEK_API_KEY not configured")

    response = requests.post(
        f"{api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_gemini_api(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Call Google Gemini API"""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key or api_key == "your_google_api_key_here":
        raise ValueError("GOOGLE_API_KEY not configured")

    # Gemini uses a different API format
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    # Extract text from Gemini's response format
    if "candidates" in data and len(data["candidates"]) > 0:
        candidate = data["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            parts = candidate["content"]["parts"]
            if len(parts) > 0 and "text" in parts[0]:
                return parts[0]["text"]

    raise ValueError("Invalid Gemini response format")


def _call_openai_api(prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
    """Call OpenAI API"""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY not configured")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",  # Cost-effective OpenAI model
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        timeout=30
    )

    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


# Quick test function
def test_llm_fallback():
    """Test the LLM fallback chain"""
    try:
        result = call_llm_with_fallback("Say 'Hello from AI!' in one sentence.")
        print(f"\n✓ LLM Test Result: {result}\n")
        return True
    except Exception as e:
        print(f"\n✗ LLM Test Failed: {e}\n")
        return False
