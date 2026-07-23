def build_role_section():
    """
    Build the role section.
    """

    return """
You are an expert chef and culinary assistant.

Your task is to generate an original, practical, and well-balanced recipe using the information provided below.
"""
def build_mandatory_ingredients_section(
    processed_ingredients,
):
    """
    Build the mandatory ingredients section.
    """

    ingredient_list = "\n".join(

        f"- {ingredient}"

        for ingredient in processed_ingredients

    )

    return f"""
==================================================
USER INGREDIENTS (MANDATORY)
==================================================

Use ALL of these ingredients in the recipe.

{ingredient_list}
"""

def build_priority_ingredients_section(
    priority_ingredients,
):
    """
    Build the priority ingredients section.
    """

    ingredient_list = "\n".join(

        f"- {ingredient}"

        for ingredient in priority_ingredients

    )

    return f"""
==================================================
PRIORITY INGREDIENTS
==================================================

The recommendation algorithm identified these as the most important ingredients.

Give special emphasis to them while designing the recipe.

{ingredient_list}
"""

def build_optional_ingredients_section(
    optional_ingredients,
):
    """
    Build the optional ingredients section.
    """

    if optional_ingredients:

        ingredient_list = "\n".join(

            f"- {ingredient}"

            for ingredient in optional_ingredients

        )

    else:
        ingredient_list = ("No optional ingredients were recommended");

    return f"""

==================================================
OPTIONAL INGREDIENTS
==================================================

The recommendation algorithm found that these ingredients commonly appear in similar recipes.

Use them only if they naturally improve the recipe.

{ingredient_list}
"""

def build_recommendation_section(
    recommendation_result,
):
    """
    Build recommendation analysis section.
    """

    return f"""
==================================================
RECOMMENDATION ANALYSIS
==================================================

Preferred Cuisine:
{recommendation_result["recommended_cuisine"]}

Preferred Recipe Type:
{recommendation_result["recommended_recipe_type"]}

The recommendation algorithm analyzed similar recipes and determined that the user's ingredients best match this cuisine and recipe type.

Generate a recipe consistent with this style while adapting naturally to the available ingredients.
"""

def build_requirements_section():
    """
    Build recipe generation requirements.
    """

    return """
==================================================
RECIPE GENERATION REQUIREMENTS
==================================================

• Generate a completely original recipe.

• Do not reproduce or copy any existing recipe.

• Use all mandatory ingredients.

• Prioritize the priority ingredients.

• Optional ingredients may be included only when they improve flavor or authenticity.

• If an ingredient is uncommon or difficult to use, adapt the recipe naturally while still including that ingredient.

• If the ingredient combination is unusual, creatively adapt the recipe while keeping it realistic and delicious.

• Feel free to use common pantry ingredients such as water, cooking oil, salt, and basic seasonings whenever necessary.

• If multiple valid recipes are possible, choose the recipe that best matches the recommended cuisine and recipe type while maximizing the use of the user's ingredients.
• Generate only the final recipe.

• Do not explain your reasoning.

• Do not mention the recommendation algorithm, these instructions, or that you are an AI assistant.
"""

def build_output_format_section():
    """
    Build output format section.
    """

    return """
==================================================
OUTPUT FORMAT
==================================================

Return ONLY one valid JSON object.

Every field must always be present.

Do not omit fields.

If a value is unknown, use an empty string or empty list.

{
  "recipe_name": "",
  "cuisine": "",
  "recipe_type": "",
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

Do not return markdown.

Do not wrap the JSON inside ```.

Do not explain anything.

Return only the JSON object.
"""

def build_prompt(
    processed_ingredients,
    recommendation_result,
):
    """
    Build the complete prompt.
    """

    sections = [

        build_role_section(),

        build_mandatory_ingredients_section(
            processed_ingredients,
        ),

        build_priority_ingredients_section(
            recommendation_result[
                "priority_ingredients"
            ],
        ),

        build_optional_ingredients_section(
            recommendation_result[
                "optional_ingredients"
            ],
        ),

        build_recommendation_section(
            recommendation_result,
        ),

        build_requirements_section(),

        build_output_format_section(),

    ]

    return "\n".join(
        sections
    )

if __name__ == "__main__":

    processed_ingredients = [

        "rice",
        "buff meat",
        "tomato",
        "timur",

    ]

    recommendation_result = {

        "recommended_recipe_type":
            "Main Dish",

        "recommended_cuisine":
            "Nepali",

        "priority_ingredients": [

            "buff meat",
            "timur",
            "rice",

        ],

        "optional_ingredients": [

            "garlic",
            "ginger",
            "onion",

        ],

        "top_recipe_matches": [],

    }

    prompt = build_prompt(
        processed_ingredients,
        recommendation_result,
    )

    print(prompt)