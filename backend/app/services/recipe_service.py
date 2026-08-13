import json
from sqlalchemy.orm import Session

from app.models.recipe import Recipe

from app.algorithms.preprocessor import preprocess_ingredients
from app.algorithms.tfidf import build_tfidf_vectors
from app.algorithms.cosine_similarity import calculate_recipe_similarities
from app.algorithms.recommendation import generate_recommendation
from app.algorithms.prompt_builder import build_prompt

from app.services.gemini_service import generate_recipe
from app.services.fallback_service import generate_recipe_from_dataset
from app.core.exceptions import RecipeGenerationError


# Recommend Recipes

def recommend_recipes(
    db: Session,
    request,
):
    preprocessing_result = preprocess_ingredients(
        request.ingredients
    )

    processed_ingredients = preprocessing_result[
        "processed_ingredients"
    ]

    unknown_ingredients = preprocessing_result[
        "unknown_ingredients"
    ]

    corrections = preprocessing_result[
        "corrections"
    ]

    print("\n===== Preprocessor =====")
    print("Input:", request.ingredients)
    print("Processed:", processed_ingredients)
    print("Unknown:", unknown_ingredients)
    print("Corrections:", corrections)
    print("========================\n")

    if not processed_ingredients:
        return {
            "recommendations": [],
            "unknown_ingredients": unknown_ingredients,
            "corrections": corrections,
            "message": "No valid ingredients were provided."
        }

    tfidf_result = build_tfidf_vectors(
        processed_ingredients
    )

    print("\n===== TF-IDF =====")
    print(
        f"Recipe count: {len(tfidf_result['recipe_names'])}"
    )
    print(
        f"Vocabulary size: {len(tfidf_result['feature_names'])}"
    )
    print("=================\n")

    similarity_result = calculate_recipe_similarities(
        tfidf_result
    )

    print("\n===== Cosine Similarity =====")

    top_matches = similarity_result[
        "recipe_similarities"
    ][:3]

    if not top_matches:
        print("No similar recipes found.")
    else:
        print("Top 3 Similar Recipes:")
        for i, recipe in enumerate(top_matches, 1):
            print(
                f"{i}. {recipe['recipe_name']} | "
                f"Score: {recipe['similarity_score']:.4f}"
            )

    print("=============================\n")

    recommendation_result = generate_recommendation(
        similarity_result,
        processed_ingredients,
    )

    print("\n===== Final Recommendation Ranking =====")

    final_matches = recommendation_result[
         "recommendations"
    ][:3]

    for i, recipe in enumerate(final_matches, 1):
        print(
            f"{i}. {recipe['recipe_name']} | "
            f"Cosine: {recipe['cosine_score']:.4f} | "
            f"Exact Coverage: {recipe['exact_coverage']:.4f} | "
            f"Family Coverage: {recipe['family_coverage']:.4f} | "
            f"Final Score: {recipe['similarity_score']:.4f}"
        )

    print("========================================\n")

    return recommendation_result



# Generate Selected Recipe

def generate_selected_recipe(
    db: Session,
    request,
    user_id: int,
):
    preprocessing_result = preprocess_ingredients(
        request.ingredients
    )

    processed_ingredients = preprocessing_result[
        "processed_ingredients"
    ]

    prompt = build_prompt(
        processed_ingredients,
        request.recipe_name,
        request.servings or 2,
    )

    try:
        gemini_response = generate_recipe(
            prompt
        )

    except Exception as e:

        print(
            f"Gemini unavailable, using local dataset fallback: {e}"
        )

        recipe_data = generate_recipe_from_dataset(
            request.recipe_name,
            request.servings or 2,
        )

        if user_id is not None:
            recipe = save_recipe(
                db=db,
                title=recipe_data["recipe_name"],
                ingredients=json.dumps(
                    recipe_data["ingredients"]
                ),
                instructions=json.dumps(
                    recipe_data["instructions"]
                ),
                cuisine=recipe_data.get(
                    "cuisine",
                    "Nepali",
                ),
                recipe_type="",
                cooking_tips=json.dumps(
                    recipe_data["cooking_tips"]
                ),
                cooking_time=recipe_data[
                    "cooking_time"
                ],
                servings=recipe_data[
                    "servings"
                ],
                user_id=user_id,
            )

            return recipe

        return recipe_data

    recipe_text = gemini_response.strip()

    if recipe_text.startswith("```json"):
        recipe_text = recipe_text[7:]

    if recipe_text.endswith("```"):
        recipe_text = recipe_text[:-3]

    try:
        recipe_data = json.loads(
            recipe_text.strip()
        )

    except json.JSONDecodeError:
        raise RecipeGenerationError(
            "Gemini returned invalid JSON."
        )

    required_fields = [
        "recipe_name",
        "ingredients",
        "instructions",
        "cuisine",
        "cooking_time",
        "servings",
        "cooking_tips",
    ]

    for field in required_fields:
        if field not in recipe_data:
            raise RecipeGenerationError(
                f"Missing field: {field}"
            )

    if user_id is not None:
        recipe = save_recipe(
            db=db,
            title=recipe_data["recipe_name"],
            ingredients=json.dumps(
                recipe_data["ingredients"]
            ),
            instructions=json.dumps(
                recipe_data["instructions"]
            ),
            cuisine=recipe_data.get(
                "cuisine",
                "Nepali",
            ),
            recipe_type="",
            cooking_tips=json.dumps(
                recipe_data["cooking_tips"]
            ),
            cooking_time=recipe_data[
                "cooking_time"
            ],
            servings=recipe_data[
                "servings"
            ],
            user_id=user_id,
        )

        return recipe

    return recipe_data


# Save Recipe

def save_recipe(
    db: Session,
    title: str,
    ingredients: str,
    instructions: str,
    cuisine: str,
    recipe_type: str,
    cooking_tips: str,
    cooking_time: int,
    servings: int,
    user_id: int,
):
    recipe = Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        cuisine=cuisine,
        recipe_type=recipe_type,
        cooking_tips=cooking_tips,
        cooking_time=cooking_time,
        servings=servings,
        user_id=user_id,
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return recipe


# Get Recipe By ID

def get_recipe_by_id(
    db: Session,
    recipe_id: int,
):
    return (
        db.query(Recipe)
        .filter(Recipe.id == recipe_id)
        .first()
    )


# Get All Recipes

def get_all_recipes(
    db: Session,
):
    return db.query(Recipe).all()