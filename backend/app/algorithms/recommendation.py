def generate_recommendation(similarity_result, top_n=3):
    """
    Return the top N matching Nepali recipes based on cosine similarity.
    """

    top_recipes = similarity_result["recipe_similarities"][:top_n]

    return {
        "recommendations": top_recipes
    }


# Test
if __name__ == "__main__":

    from tfidf import build_tfidf_vectors
    from cosine_similarity import calculate_recipe_similarities

    test_ingredients = [
        "rice",
        "lentils",
        "garlic",
    ]

    tfidf_result = build_tfidf_vectors(test_ingredients)

    similarity_result = calculate_recipe_similarities(tfidf_result)

    recommendation = generate_recommendation(similarity_result)

    print("\nTop 3 Recommended Recipes:\n")

    for recipe in recommendation["recommendations"]:
        print(
            f"{recipe['recipe_name']} | "
            f"{recipe['cuisine']} | "
            f"Score: {recipe['similarity_score']:.4f}"
        )