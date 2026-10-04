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


def build_ingredients_section(
    processed_ingredients,
    selected_optional=None,
):
    """
    Build the available ingredients section.
    Optional ingredients the user chose to add are included here.
    """
    available = list(processed_ingredients)

    for ingredient in selected_optional or []:
        if ingredient not in available:
            available.append(ingredient)

    ingredient_list = "\n".join(
        f"- {ingredient}"
        for ingredient in available
    )

    return f"""
Available ingredients:
{ingredient_list}

Use these ingredients as much as possible.

If some traditional ingredients are missing,
adapt the recipe naturally while keeping it authentically Nepali.
"""


def build_exclusions_section(excluded_optional):
    """
    Build the excluded ingredients section.
    Returns an empty string when nothing is excluded.
    """
    if not excluded_optional:
        return ""

    excluded_list = "\n".join(
        f"- {ingredient}"
        for ingredient in excluded_optional
    )

    return f"""
Excluded ingredients (the user chose NOT to use these):
{excluded_list}

Do NOT use any excluded ingredient anywhere in the recipe:
not in the ingredients list, not in the instructions
and not in the cooking tips.

Rewrite the recipe so it still tastes good and stays authentic
without the excluded ingredients.
Do not mention that these ingredients were removed.
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


def build_requirements_section(excluded_optional=None):
    """
    Build recipe generation requirements.
    """
    extra_rule = ""

    if excluded_optional:
        extra_rule = """- Do not introduce any other non-pantry ingredient that is not
  in the available ingredients list.
"""

    return f"""
Requirements:

- Generate an authentic Nepali recipe.
- The recipe should closely match the selected recipe.
- Use the user's available ingredients wherever possible.
- Common Nepali pantry ingredients such as water, salt, oil,
  turmeric, cumin, garlic, ginger, and other basic seasonings
  may be added when necessary, unless they are listed as
  excluded ingredients.
- Never use an ingredient that is listed as excluded.
{extra_rule}- Keep the recipe practical and realistic.
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
    selected_optional=None,
    excluded_optional=None,
):
    """
    Build the complete Gemini prompt.
    """
    sections = [
        build_role_section(),

        build_selected_recipe_section(
            recipe_name,
        ),

        build_ingredients_section(
            processed_ingredients,
            selected_optional,
        ),

        build_exclusions_section(
            excluded_optional,
        ),

        build_servings_section(
            servings,
        ),

        build_requirements_section(
            excluded_optional,
        ),

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
        selected_optional=["green peas"],
        excluded_optional=["ghee", "asafoetida"],
    )

    print(prompt)