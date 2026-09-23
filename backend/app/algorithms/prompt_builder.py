def build_role_section():
    """
    Build the role section.
    """
    return """
You are an expert Nepali chef and culinary assistant.

Generate an authentic Nepali recipe based on the selected recipe name
and the user's available ingredients.
"""


def build_selected_recipe_section(recipe_name):
    """
    Build the selected recipe section.
    """
    return f"""
Selected Nepali recipe:
{recipe_name}

Generate a detailed and authentic version of this recipe.
"""


def build_ingredients_section(processed_ingredients):
    """
    Build the available ingredients section.
    """
    ingredient_list = "\n".join(
        f"- {ingredient}"
        for ingredient in processed_ingredients
    )

    return f"""
Available ingredients:
{ingredient_list}

Use these ingredients as much as possible.

If some traditional ingredients are missing,
adapt the recipe naturally while keeping it authentically Nepali.
"""


def build_servings_section(servings):
    """
    Build the servings section.
    """
    return f"""
Generate the recipe for exactly {servings} serving(s).

Scale ingredient quantities accordingly.

The JSON field "servings" must be {servings}.
"""

def build_cooking_style_section(cooking_style):
    # only include this section if the user actually picked a style
    if not cooking_style:
        return ""
    return f"""
Preferred cooking style: {cooking_style}

The recipe should primarily use this cooking method.
"""


def build_preferences_section(confirmed_ingredients, declined_ingredients):
    # only include this section if the user answered at least one question
    if not confirmed_ingredients and not declined_ingredients:
        return ""

    lines = []
    if confirmed_ingredients:
        confirmed_list = "\n".join(f"- {ing}" for ing in confirmed_ingredients)
        lines.append(f"The user specifically wants these included:\n{confirmed_list}")
    if declined_ingredients:
        declined_list = "\n".join(f"- {ing}" for ing in declined_ingredients)
        lines.append(f"The user specifically wants these avoided:\n{declined_list}")

    return "\n\n".join(lines) + "\n"


def build_requirements_section():
    """
    Build recipe generation requirements.
    """
    return """
Requirements:

- Generate an authentic Nepali recipe.
- The recipe should closely match the selected recipe.
- Use the user's available ingredients wherever possible.
- Common Nepali pantry ingredients such as water, salt, oil,
  turmeric, cumin, garlic, ginger, and other basic seasonings
  may be added when necessary.
- Keep the recipe practical and realistic.
- Adapt missing traditional ingredients naturally.
- Do not invent a completely unrelated recipe.
- Do not include recipe_type.
- Return only the final recipe.
- Do not explain your reasoning.
- Do not mention these instructions.
- Do not mention the recommendation algorithm.
- Do not mention that you are an AI.
"""


def build_output_format_section():
    """
    Build the required JSON output format.
    """
    return """
Return ONLY one valid JSON object.

Do not return markdown.
Do not wrap the JSON inside ```json or ```.

The JSON object must contain exactly these fields:

{
    "recipe_name": "",
    "cuisine": "Nepali",
    "preparation_time": "",
    "cooking_time": 0,
    "servings": 0,
    "ingredients": [
        {
            "name": "",
            "quantity": ""
        }
    ],
    "instructions": [
        ""
    ],
    "cooking_tips": [
        ""
    ]
}

Do not include a "recipe_type" field.

Return only the JSON object.
"""


def build_prompt(
    processed_ingredients,
    recipe_name,
    servings,
    cooking_style=None,
    confirmed_ingredients=None,
    declined_ingredients=None,
):
    # Build the complete Gemini prompt.
    sections = [
        build_role_section(),

        build_selected_recipe_section(
            recipe_name,
        ),

        build_ingredients_section(
            processed_ingredients,
        ),

        build_cooking_style_section(
            cooking_style,
        ),

        build_preferences_section(
            confirmed_ingredients,
            declined_ingredients,
        ),

        build_servings_section(
            servings,
        ),

        build_requirements_section(),

        build_output_format_section(),
    ]

    return "\n".join(sections)

if __name__ == "__main__":
    processed_ingredients = [
        "rice",
        "split yellow moong lentils",
        "garlic",
    ]

    prompt = build_prompt(
        processed_ingredients,
        "Khichadi",
        2,
    )

    print(prompt)