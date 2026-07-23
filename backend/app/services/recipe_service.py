import json
from sqlalchemy.orm import Session

from app.models.recipe import Recipe

from app.algorithms.preprocessor import preprocess_ingredients
from app.algorithms.classifier import classify_ingredients
from app.algorithms.tfidf import build_tfidf_vectors
from app.algorithms.cosine_similarity import calculate_recipe_similarities
from app.algorithms.compatibility import (
    calculate_ingredient_compatibility_scores,
)
from app.algorithms.ranking import rank_ingredients
from app.algorithms.recommendation import (
    generate_recommendation,
)
from app.algorithms.prompt_builder import build_prompt

from app.services.gemini_service import generate_recipe

from app.core.exceptions import RecipeGenerationError

def generate_recipe_with_ai(
    db: Session,
    request,
    user_id: int,
):
    # --------------------------------------------
    # Preprocess Ingredients
    # --------------------------------------------

    processed_ingredients = preprocess_ingredients(
        request.ingredients
    )

    # --------------------------------------------
    # Classify Ingredients
    # --------------------------------------------

    classification_result = classify_ingredients(
        processed_ingredients
    )

    # --------------------------------------------
    # Build TF-IDF Vectors
    # --------------------------------------------

    tfidf_result = build_tfidf_vectors(
        processed_ingredients
    )

    # --------------------------------------------
    # Calculate Recipe Similarities
    # --------------------------------------------

    similarity_result = (
        calculate_recipe_similarities(
            tfidf_result
        )
    )

    # --------------------------------------------
    # Calculate Compatibility Scores
    # --------------------------------------------

    compatibility_scores = (
        calculate_ingredient_compatibility_scores(
            processed_ingredients
        )
    )

    # --------------------------------------------
    # Rank Ingredients
    # --------------------------------------------

    ranking_result = rank_ingredients(
        processed_ingredients,
        classification_result,
        similarity_result,
        compatibility_scores,
    )

    # --------------------------------------------
    # Generate Recommendation
    # --------------------------------------------

    recommendation_result = (
        generate_recommendation(
            processed_ingredients,
            similarity_result,
            ranking_result,
            request.cuisine,
        )
    )

    # --------------------------------------------
    # Build Prompt
    # --------------------------------------------

    prompt = build_prompt(
        processed_ingredients,
        recommendation_result,
    )

    # --------------------------------------------
    # Generate Recipe with Gemini
    # --------------------------------------------

    try:

       gemini_response = generate_recipe(
           prompt,
        )

    except Exception as e:

       raise RecipeGenerationError(
           f"Recipe generation failed: {e}"
       )

    #deleted before project submission
    print("\n===== Gemini Response =====")
    print(gemini_response)
    print("===========================\n")

    # --------------------------------------------
    # Parse Gemini Response
    # --------------------------------------------

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

    # --------------------------------------------
    # Validate Required Fields
    # --------------------------------------------

    required_fields = [

        "recipe_name",
        "ingredients",
        "instructions",
        "cuisine",
        "recipe_type",
        "cooking_time",
        "servings",
        "cooking_tips",
   ]

    for field in required_fields:

        if field not in recipe_data:

            raise RecipeGenerationError(
                f"Missing field: {field}"
           )

    # --------------------------------------------
    # Save Recipe
    # --------------------------------------------

    try:
        recipe = save_recipe(
            db=db,
            title=recipe_data["recipe_name"],
            ingredients=json.dumps(
                recipe_data["ingredients"]
            ),
            instructions=json.dumps(
                recipe_data["instructions"]
            ),
            cuisine=recipe_data["cuisine"],
            recipe_type=recipe_data["recipe_type"],
            cooking_tips=recipe_data["cooking_tips"],
            cooking_time=recipe_data["cooking_time"],
            servings=recipe_data["servings"],
            user_id=user_id,
        )
    except Exception as e:
        raise RecipeGenerationError(
            f"Failed to save recipe: {e}"
        )

    return recipe

   
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


def get_recipe_by_id(db: Session, recipe_id: int):
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()


def get_all_recipes(db: Session):
    return db.query(Recipe).all()