from concurrent.futures import (
    ThreadPoolExecutor,
    TimeoutError as FutureTimeoutError,
)

from google import genai

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_TIMEOUT_SECONDS,
)


# Gemini Client

client = genai.Client(
    api_key=GEMINI_API_KEY,
)

# Worker threads for Gemini calls, so a slow call can be abandoned
_executor = ThreadPoolExecutor(max_workers=4)


def _call_gemini(
    prompt,
):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    if not response.text:
        raise Exception(
            "Gemini returned an empty response."
        )

    return response.text


# Generate Recipe

def generate_recipe(
    prompt,
):
    """
    Send the prompt to Gemini and return the generated recipe.

    Raises an exception if Gemini fails or does not answer within
    GEMINI_TIMEOUT_SECONDS, so the caller can use the dataset fallback.
    """

    future = _executor.submit(
        _call_gemini,
        prompt,
    )

    try:
        return future.result(
            timeout=GEMINI_TIMEOUT_SECONDS,
        )

    except FutureTimeoutError:
        future.cancel()

        raise Exception(
            f"Gemini did not respond within "
            f"{GEMINI_TIMEOUT_SECONDS:g} seconds."
        )


# Fallback testing

# def generate_recipe(prompt):
#     raise Exception("Forced Gemini failure for testing fallback")