import math


# Dot Product

def dot_product(
    vector1,
    vector2,
):

    total = 0.0

    for value1, value2 in zip(
        vector1,
        vector2,
    ):
        total += value1 * value2

    return total


# Vector Magnitude

def vector_magnitude(vector):
   
    total = 0.0

    for value in vector:
        total += value ** 2

    return math.sqrt(total)


# Cosine Similarity

def calculate_cosine_similarity(
    vector1,
    vector2,
):
    """
    Calculate cosine similarity between two vectors.
    """

    numerator = dot_product(
        vector1,
        vector2,
    )

    magnitude1 = vector_magnitude(
        vector1,
    )

    magnitude2 = vector_magnitude(
        vector2,
    )

    denominator = (
        magnitude1 * magnitude2
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


# Calculate Recipe Similarities

def calculate_recipe_similarities(
    tfidf_result,
):
    recipe_names = tfidf_result[
        "recipe_names"
    ]

    recipe_ingredients = tfidf_result[
        "recipe_ingredients"
    ]

    recipe_cuisines = tfidf_result[
        "recipe_cuisines"
    ]

    recipe_vectors = tfidf_result[
        "recipe_vectors"
    ]

    user_vector = tfidf_result[
        "user_vector"
    ]

    user_vector = (
        user_vector.toarray()[0]
    )

    recipe_similarities = []

    for index, recipe_vector in enumerate(
        recipe_vectors
    ):

        recipe_vector = (
            recipe_vector.toarray()[0]
        )

        cosine_score = (
            calculate_cosine_similarity(
                user_vector,
                recipe_vector,
            )
        )

        recipe_similarities.append(
            {
                "recipe_name":
                    recipe_names[index],

                "cuisine":
                    recipe_cuisines[index],

                "ingredients":
                    recipe_ingredients[index],

                "cosine_score":
                    round(cosine_score, 4),

                "similarity_score":
                    round(cosine_score, 4),
            }
        )

    recipe_similarities.sort(
        key=lambda recipe: recipe[
            "similarity_score"
        ],
        reverse=True,
    )

    return {
        "recipe_similarities":
            recipe_similarities,
    }


# Test
if __name__ == "__main__":

    from tfidf import (
        build_tfidf_vectors,
    )

    test_ingredients = [
        "tomato",
        "garlic",
        "onion",
    ]

    tfidf_result = build_tfidf_vectors(
        test_ingredients
    )

    similarity_result = (
        calculate_recipe_similarities(
            tfidf_result
        )
    )

    print(
        f"\nTotal Recipes: "
        f"{len(similarity_result['recipe_similarities'])}"
    )

    if not similarity_result[
        "recipe_similarities"
    ]:

        print(
            "\nNo recipes found in recipes.csv."
        )

    else:

        print(
            "\nTop 5 Similarities:\n"
        )

        for recipe in similarity_result[
            "recipe_similarities"
        ][:5]:

            print(
                f"{recipe['recipe_name']} | "
                f"{recipe['cuisine']} | "
                f"{recipe['similarity_score']:.4f}"
            )