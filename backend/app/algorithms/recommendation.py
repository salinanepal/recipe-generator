# -------------------------------------------------------
# Ingredient Families
# -------------------------------------------------------

INGREDIENT_FAMILIES = {
    "lentils": {
        "red lentils",
        "black gram lentils",
        "split yellow lentils",
    },

    "flour": {
        "rice flour",
        "wheat flour",
        "gram flour",
        "buckwheat flour",
        "finger millet flour",
        "barley flour",
        "all purpose flour",
        "sticky rice flour"
    },

}


# -------------------------------------------------------
# Ingredient Match Scores
# -------------------------------------------------------

def calculate_ingredient_match_scores(
    user_ingredients,
    recipe_ingredients,
):

    user_ingredients = {
        ingredient.lower().strip()
        for ingredient in user_ingredients
    }

    recipe_ingredients = {
        ingredient.lower().strip()
        for ingredient in recipe_ingredients
    }

    if not user_ingredients:
        return {
            "exact_coverage": 0.0,
            "family_coverage": 0.0,
        }

    # Exact ingredient matches
    exact_matches = user_ingredients.intersection(
        recipe_ingredients
    )

    exact_coverage = (
        len(exact_matches)
        / len(user_ingredients)
    )

    # Family ingredient matches
    family_matches = 0

    for family, members in INGREDIENT_FAMILIES.items():

        if family not in user_ingredients:
            continue

        if recipe_ingredients.intersection(members):
            family_matches += 1

    family_coverage = (
        family_matches
        / len(user_ingredients)
    )

    return {
        "exact_coverage": exact_coverage,
        "family_coverage": family_coverage,
    }


# -------------------------------------------------------
# Final Recommendation Score
# -------------------------------------------------------

COSINE_WEIGHT = 0.50
EXACT_COVERAGE_WEIGHT = 0.40
FAMILY_COVERAGE_WEIGHT = 0.10


def calculate_final_score(
    cosine_score,
    exact_coverage,
    family_coverage,
):
    """
    Calculate the final recommendation score.

    Cosine similarity remains the primary score.
    """

    final_score = (
        COSINE_WEIGHT * cosine_score
        + EXACT_COVERAGE_WEIGHT * exact_coverage
        + FAMILY_COVERAGE_WEIGHT * family_coverage
    )

    return round(
        final_score,
        4,
    )


# -------------------------------------------------------
# Generate Recommendation
# -------------------------------------------------------

def generate_recommendation(
    similarity_result,
    processed_ingredients,
    top_n=3,
):

    ranked_recipes = []

    for recipe in similarity_result[
        "recipe_similarities"
    ]:

        match_scores = (
            calculate_ingredient_match_scores(
                processed_ingredients,
                recipe["ingredients"],
            )
        )

        exact_coverage = (
            match_scores["exact_coverage"]
        )

        family_coverage = (
            match_scores["family_coverage"]
        )

        final_score = (
            calculate_final_score(
                recipe["cosine_score"],
                exact_coverage,
                family_coverage,
            )
        )

        ranked_recipes.append(
            {
                **recipe,

                "exact_coverage":
                    round(
                        exact_coverage,
                        4,
                    ),

                "family_coverage":
                    round(
                        family_coverage,
                        4,
                    ),

                "similarity_score":
                    final_score,
            }
        )

    # Sort by final recommendation score
    ranked_recipes.sort(
        key=lambda recipe:
            recipe["similarity_score"],
        reverse=True,
    )

    return {
        "recommendations":
            ranked_recipes[:top_n]
    }

