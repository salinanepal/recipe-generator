from app.algorithms.preprocessor import preprocess_ingredients
from app.algorithms.tfidf import build_tfidf_vectors
from app.algorithms.cosine_similarity import calculate_recipe_similarities
from app.algorithms.recommendation import generate_recommendation
from app.algorithms.instruction_features import (
    generate_questions,
    calculate_instruction_scores,
    answer_tokens,
)

CANDIDATE_POOL = 20
INSTRUCTION_WEIGHT = 0.30
TOP_N = 3


# Questions

def get_refinement_questions(request):
    preprocessing_result = preprocess_ingredients(
        request.ingredients
    )

    processed_ingredients = preprocessing_result[
        "processed_ingredients"
    ]

    return {
        "questions": generate_questions(processed_ingredients),
        "unknown_ingredients": preprocessing_result[
            "unknown_ingredients"
        ],
        "corrections": preprocessing_result["corrections"],
    }


# Recommend using ingredients + answers

def recommend_with_answers(request):
    preprocessing_result = preprocess_ingredients(
        request.ingredients
    )

    processed_ingredients = preprocessing_result[
        "processed_ingredients"
    ]

    unknown_ingredients = preprocessing_result[
        "unknown_ingredients"
    ]

    corrections = preprocessing_result["corrections"]

    if not processed_ingredients:
        return {
            "recommendations": [],
            "unknown_ingredients": unknown_ingredients,
            "corrections": corrections,
            "message": "No valid ingredients were provided.",
        }

    tfidf_result = build_tfidf_vectors(processed_ingredients)

    similarity_result = calculate_recipe_similarities(tfidf_result)

    # Wider pool than 3 so instruction answers can reorder the list
    candidates = generate_recommendation(
        similarity_result,
        processed_ingredients,
        top_n=CANDIDATE_POOL,
    )["recommendations"]

    # Yes  -> plain method once + ingredient|method pair twice
    # No   -> only the ingredient|method pair, so "don't fry the chicken"
    #         does not penalise every recipe that fries something else
    liked = []
    disliked = []

    for a in request.answers:
        if a.answer == "yes":
            liked += answer_tokens(a.ingredient, a.verb)
        elif a.answer == "no":
            disliked += answer_tokens(a.ingredient, a.verb)[1:]

    if not liked and not disliked:
        return {
            "recommendations": candidates[:TOP_N],
            "unknown_ingredients": unknown_ingredients,
            "corrections": corrections,
        }

    instruction_scores = calculate_instruction_scores(
        liked,
        disliked,
    )

    for recipe in candidates:
        base_score = recipe["similarity_score"]

        instruction_score = instruction_scores.get(
            recipe["recipe_name"].strip(),
            0.5,
        )

        recipe["base_score"] = base_score
        recipe["instruction_score"] = round(instruction_score, 4)
        recipe["similarity_score"] = round(
            (1 - INSTRUCTION_WEIGHT) * base_score
            + INSTRUCTION_WEIGHT * instruction_score,
            4,
        )

    candidates.sort(
        key=lambda recipe: recipe["similarity_score"],
        reverse=True,
    )

    return {
        "recommendations": candidates[:TOP_N],
        "unknown_ingredients": unknown_ingredients,
        "corrections": corrections,
    }