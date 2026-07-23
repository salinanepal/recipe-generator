from google import genai

from app.core.config import GEMINI_API_KEY


# -------------------------------------------------------
# Gemini Client
# -------------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY,
)


# -------------------------------------------------------
# Generate Recipe
# -------------------------------------------------------

def generate_recipe(
    prompt,
):
    """
    Send the prompt to Gemini
    and return the generated recipe.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )

    if not response.text:
        raise Exception("Gemini returned an empty response.")

    return response.text