from collections import Counter

# -------------------------------------------------------
# Category Weights
# -------------------------------------------------------

CATEGORY_WEIGHTS = {
    "Protein": 1.00,
    "Grain": 0.90,
    "Vegetable": 0.80,
    "Dairy": 0.75,
    "Fruit": 0.70,
    "Spice": 0.60,
    "Oil/Fat": 0.50,
    "Unknown": 0.40,
}

# -------------------------------------------------------
# Pantry Ingredients (low recommendation priority)
# -------------------------------------------------------

PANTRY_INGREDIENTS = {
    "salt",
    "black salt",
    "water",
    "hot water",
    "ice cubes",
    "vegetable oil",
    "mustard oil",
    "sesame oil",
    "ghee",
    "butter",
    "oil",
    "vinegar",
    "soy sauce",
    "sugar",
    "brown sugar",
    "white sugar",
    "honey",
    "corn syrup",
    "baking soda",
    "baking powder",
    "yeast",
}


# -------------------------------------------------------
# Calculate Frequency Scores
# -------------------------------------------------------

def calculate_frequency_scores(
    processed_ingredients,
    similarity_result,
    top_n=10,
):
    """
    Calculate how frequently each user ingredient
    appears in the top similar recipes.
    """

    top_recipes = similarity_result[
        "recipe_similarities"
    ][:top_n]

    ingredient_counter = Counter()

    for recipe in top_recipes:

        for ingredient in recipe[
            "ingredients"
        ]:

            if (
                ingredient
                in processed_ingredients
            ):

                ingredient_counter[
                    ingredient
                ] += 1

    if ingredient_counter:

        max_count = max(
            ingredient_counter.values()
        )

    else:

        max_count = 1

    frequency_scores = {}

    for ingredient in processed_ingredients:

        frequency_scores[
            ingredient
        ] = round(

            ingredient_counter.get(
                ingredient,
                0,
            ) / max_count,

            2,
        )

    return frequency_scores

# -------------------------------------------------------
# Calculate Ranking Scores
# -------------------------------------------------------

def calculate_ranking_scores(
    processed_ingredients,
    classification_result,
    frequency_scores,
    compatibility_scores,
):
    """
    Calculate the final ranking score
    for each ingredient.
    """

    ingredient_categories = (
        classification_result[
            "ingredient_categories"
        ]
    )

    ranked_ingredients = []

    for ingredient in processed_ingredients:

        category = (
            ingredient_categories.get(
                ingredient,
                "Unknown",
            )
        )

        category_weight = (
            CATEGORY_WEIGHTS.get(
                category,
                CATEGORY_WEIGHTS[
                    "Unknown"
                ],
            )
        )

        frequency_score = (
            frequency_scores.get(
                ingredient,
                0.0,
            )
        )

        compatibility_score = (
            compatibility_scores.get(
                ingredient,
                0.0,
            )
        )

        ranking_score = (
        0.50 * category_weight
        + 0.30 * frequency_score
        + 0.20 * compatibility_score
        )

        # Pantry ingredients should not dominate ranking
        if ingredient in PANTRY_INGREDIENTS:
            ranking_score *= 0.4

        ranking_score = round(ranking_score, 2)

        ranked_ingredients.append(

            {
                "ingredient":
                    ingredient,

                "category":
                    category,

                "category_weight":
                    category_weight,

                "frequency_score":
                    frequency_score,

                "compatibility_score":
                    compatibility_score,

                "ranking_score":
                    ranking_score,
            }

        )

    return ranked_ingredients

# -------------------------------------------------------
# Rank Ingredients
# -------------------------------------------------------

def rank_ingredients(
    processed_ingredients,
    classification_result,
    similarity_result,
    compatibility_scores,
):
    """
    Rank ingredients by combining
    category importance,
    recipe frequency,
    and compatibility.
    """

    frequency_scores = (
        calculate_frequency_scores(
            processed_ingredients,
            similarity_result,
        )
    )

    ranked_ingredients = (
        calculate_ranking_scores(
            processed_ingredients,
            classification_result,
            frequency_scores,
            compatibility_scores,
        )
    )

    ranked_ingredients.sort(

        key=lambda ingredient:
            ingredient[
                "ranking_score"
            ],

        reverse=True,
    )

    return {

        "ranked_ingredients":
            ranked_ingredients,

    }

# -------------------------------------------------------
# Test
# -------------------------------------------------------

if __name__ == "__main__":

    from classifier import (
        classify_ingredients,
    )

    from tfidf import (
        build_tfidf_vectors,
    )

    from cosine_similarity import (
        calculate_recipe_similarities,
    )

    from compatibility import (
        calculate_ingredient_compatibility_scores,
    )

    test_ingredients = [

        "rice",
        "buff meat",
        "tomato",
        "timur",

    ]

    classification_result = (
        classify_ingredients(
            test_ingredients
        )
    )

    tfidf_result = (
        build_tfidf_vectors(
            test_ingredients
        )
    )

    similarity_result = (
        calculate_recipe_similarities(
            tfidf_result
        )
    )

    compatibility_scores = (
        calculate_ingredient_compatibility_scores(
            test_ingredients
        )
    )

    result = rank_ingredients(

        test_ingredients,

        classification_result,

        similarity_result,

        compatibility_scores,

    )

    print("\nRanked Ingredients:\n")

    for ingredient in result[
        "ranked_ingredients"
    ]:

        print(ingredient)
        