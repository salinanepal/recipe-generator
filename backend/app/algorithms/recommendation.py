from collections import Counter


# -------------------------------------------------------
# Recommend Recipe Type
# -------------------------------------------------------

def recommend_recipe_type(
    similarity_result,
    top_n=10,
):
    """
    Recommend the recipe type based on
    the most common recipe type among
    the top similar recipes.
    """

    top_recipes = similarity_result[
        "recipe_similarities"
    ][:top_n]

    if not top_recipes:
        return None

    recipe_types = Counter()

    for recipe in top_recipes:

        recipe_types[
            recipe["recipe_type"]
        ] += 1

    return (
        recipe_types
        .most_common(1)[0][0]
    )


# -------------------------------------------------------
# Recommend Cuisine
# -------------------------------------------------------

def recommend_cuisine(
    similarity_result,
    user_cuisine=None,
    top_n=10,
):
    """
    Recommend cuisine unless the user
    already selected one.
    """

    if user_cuisine:

        return user_cuisine

    top_recipes = similarity_result[
        "recipe_similarities"
    ][:top_n]

    if not top_recipes:
        return None

    cuisines = Counter()

    for recipe in top_recipes:

        cuisines[
            recipe["cuisine"]
        ] += 1

    return (
        cuisines
        .most_common(1)[0][0]
    )


# -------------------------------------------------------
# Recommend Optional Ingredients
# -------------------------------------------------------

def recommend_optional_ingredients(
    processed_ingredients,
    similarity_result,
    top_n=10,
    max_ingredients=5,
):
    """
    Recommend ingredients that appear
    frequently in similar recipes but
    were not supplied by the user.
    """

    top_recipes = similarity_result[
        "recipe_similarities"
    ][:top_n]

    ingredient_counter = Counter()

    user_ingredients = set(
        processed_ingredients
    )

    for recipe in top_recipes:

        for ingredient in recipe[
            "ingredients"
        ]:

            ingredient = ingredient.lower()

            if ingredient in user_ingredients:
                continue

            ingredient_counter[
                ingredient
            ] += 1

    optional_ingredients = []

    for ingredient, _ in (
        ingredient_counter.most_common(
            max_ingredients
        )
    ):

        optional_ingredients.append(
            ingredient
        )

    return optional_ingredients


# -------------------------------------------------------
# Select Priority Ingredients
# -------------------------------------------------------

def select_priority_ingredients(
    ranking_result,
    top_n=5,
):
    """
    Select the highest ranked
    user ingredients.
    """

    ranked_ingredients = (
        ranking_result[
            "ranked_ingredients"
        ]
    )

    priority_ingredients = []

    for ingredient in ranked_ingredients[:top_n]:

        priority_ingredients.append(
            ingredient["ingredient"]
        )

    return priority_ingredients


# -------------------------------------------------------
# Generate Recommendation
# -------------------------------------------------------

def generate_recommendation(
    processed_ingredients,
    similarity_result,
    ranking_result,
    user_cuisine=None,
):
    """
    Generate the final recommendation.
    """

    return {

        "recommended_recipe_type":

            recommend_recipe_type(
                similarity_result,
            ),

        "recommended_cuisine":

            recommend_cuisine(
                similarity_result,
                user_cuisine,
            ),

        "priority_ingredients":

            select_priority_ingredients(
                ranking_result,
            ),

        "optional_ingredients":

            recommend_optional_ingredients(
                processed_ingredients,
                similarity_result,
            ),

        "top_recipe_matches":

            similarity_result[
                "recipe_similarities"
            ][:10],

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

    from ranking import (
        rank_ingredients,
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

    ranking_result = (
        rank_ingredients(
            test_ingredients,
            classification_result,
            similarity_result,
            compatibility_scores,
        )
    )

    recommendation = (
        generate_recommendation(
            test_ingredients,
            similarity_result,
            ranking_result,
        )
    )

    print("\nRecommended Recipe Type:\n")
    print(
        recommendation[
            "recommended_recipe_type"
        ]
    )

    print("\nRecommended Cuisine:\n")
    print(
        recommendation[
            "recommended_cuisine"
        ]
    )

    print("\nPriority Ingredients:\n")

    for ingredient in recommendation[
        "priority_ingredients"
    ]:

        print(ingredient)

    print("\nOptional Ingredients:\n")

    print(
        recommendation[
            "optional_ingredients"
        ]
    )

    print("\nTop Recipe Matches:\n")

    for recipe in recommendation[
        "top_recipe_matches"
    ]:

        print(
            recipe["recipe_name"],
            "->",
            recipe["similarity_score"],
        )