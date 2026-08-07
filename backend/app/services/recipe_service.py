import json
from sqlalchemy.orm import Session

from app.models.recipe import Recipe

from app.algorithms.preprocessor import preprocess_ingredients
from app.algorithms.classifier import classify_ingredients
from app.algorithms.tfidf import build_tfidf_vectors
from app.algorithms.cosine_similarity import calculate_recipe_similarities
from app.algorithms.compatibility import (
    analyze_compatibility,
    calculate_ingredient_compatibility_scores,
)
from app.algorithms.ranking import rank_ingredients
from app.algorithms.recommendation import (
    generate_recommendation,
)
from app.algorithms.prompt_builder import build_prompt

from app.services.gemini_service import generate_recipe
from app.services.fallback_service import generate_recipe_from_dataset
from app.core.exceptions import RecipeGenerationError

def generate_recipe_with_ai(
    db: Session,
    request,
    user_id: int,
):
    # --------------------------------------------
    # Preprocess Ingredients
    # --------------------------------------------

    preprocessing_result = preprocess_ingredients(
        request.ingredients
     )

    processed_ingredients = preprocessing_result["processed_ingredients"]
    unknown_ingredients = preprocessing_result["unknown_ingredients"]
    corrections = preprocessing_result["corrections"]

    print("\n===== Preprocessor =====")
    print("Input:", request.ingredients)
    print("Processed:", processed_ingredients)
    print("Unknown:", unknown_ingredients)
    print("Corrections:", corrections)
    print("========================\n")

    # --------------------------------------------~
    # Classify Ingredients
    # --------------------------------------------

    classification_result = classify_ingredients(
        processed_ingredients
    )

    print("\n===== Classifier =====")

    print("Ingredient Categories:")
    for ingredient, category in classification_result["ingredient_categories"].items():
        print(f"  {ingredient} -> {category}")

    if classification_result["unknown_ingredients"]:
        print("\nUnknown Ingredients:")
        for ingredient in classification_result["unknown_ingredients"]:
            print(f"  - {ingredient}")

    print("\nCategory Groups:")
    for category, items in classification_result["category_groups"].items():
        print(f"  {category}: {items}")

    print("======================\n")

    # --------------------------------------------
    # Build TF-IDF Vectors
    # --------------------------------------------

    tfidf_result = build_tfidf_vectors(
        processed_ingredients
    )

    print("\n===== TF-IDF =====")
    print(f"Recipe count: {len(tfidf_result['recipe_names'])}")
    print(f"Vocabulary size: {len(tfidf_result['feature_names'])}")

    # Show which terms from the user query are active in the TF-IDF vector
    feature_names = tfidf_result["feature_names"]
    user_vector = tfidf_result["user_vector"]

    active_indices = user_vector.nonzero()[1]
    active_terms = [feature_names[i] for i in active_indices]

    print("User TF-IDF terms:", active_terms)
    print("=================\n")
    

    # --------------------------------------------
    # Calculate Recipe Similarities
    # --------------------------------------------

    similarity_result = (
        calculate_recipe_similarities(
            tfidf_result
        )
    )

    print("\n===== Cosine Similarity =====")

    top_matches = similarity_result["recipe_similarities"][:5]

    if not top_matches:
        print("No similar recipes found.")
    else:
        print("Top 5 Similar Recipes:")
        for i, recipe in enumerate(top_matches, 1):
            print(
                f"{i}. {recipe['recipe_name']} | "
                f"{recipe['cuisine']} | "
                f"{recipe['recipe_type']} | "
                f"Score: {recipe['similarity_score']:.4f}"
            )

    print("=============================\n")

    # --------------------------------------------
    # Calculate Compatibility Scores
    # --------------------------------------------

    compatibility_scores = (
        calculate_ingredient_compatibility_scores(
            processed_ingredients
        )
    )

    print("\n===== Compatibility =====")

    analysis = analyze_compatibility(processed_ingredients)

    print(f"Average compatibility: {analysis['average_compatibility']}")

    print("\nHigh Compatibility Pairs:")
    if analysis["high_compatibility_pairs"]:
        for pair in analysis["high_compatibility_pairs"]:
            print(
                f"  {pair['ingredient_1']} + {pair['ingredient_2']} "
                f"-> {pair['score']:.2f}"
            )
    else:
        print("  None")

    print("\nModerate Compatibility Pairs:")
    if analysis["moderate_compatibility_pairs"]:
        for pair in analysis["moderate_compatibility_pairs"]:
            print(
                f"  {pair['ingredient_1']} + {pair['ingredient_2']} "
                f"-> {pair['score']:.2f}"
            )
    else:
        print("  None")

    print("\nLow Compatibility Pairs:")
    if analysis["low_compatibility_pairs"]:
        for pair in analysis["low_compatibility_pairs"]:
            print(
                f"  {pair['ingredient_1']} + {pair['ingredient_2']} "
                f"-> {pair['score']:.2f}"
            )
    else:
        print("  None")

    if analysis["unknown_pairs"]:
        print(f"\nUnknown Pairs: {len(analysis['unknown_pairs'])}")

    print("\nIngredient Compatibility Scores:")
    for ingredient, score in compatibility_scores.items():
        print(f"  {ingredient}: {score:.2f}")

    print("=========================\n")

    

    # --------------------------------------------
    # Rank Ingredients
    # --------------------------------------------

    ranking_result = rank_ingredients(
        processed_ingredients,
        classification_result,
        similarity_result,
        compatibility_scores,
    )

    print("\n===== Ranking =====")

    ranked = ranking_result["ranked_ingredients"]

    print("Ranked Ingredients:")
    for i, item in enumerate(ranked, 1):
        print(
            f"{i}. {item['ingredient']} "
            f"({item['category']}) "
            f"-> Final: {item['ranking_score']:.2f} "
            f"[Category: {item['category_weight']:.2f}, "
            f"Frequency: {item['frequency_score']:.2f}, "
            f"Compatibility: {item['compatibility_score']:.2f}]"
        )

    print("===================\n")

    # --------------------------------------------
    # Generate Recommendation
    # --------------------------------------------

    recommendation_result = (
        generate_recommendation(
            processed_ingredients,
            similarity_result,
            ranking_result,
            classification_result,
            request.cuisine,
        )
    )

    print("\n===== Recommendation =====")

    print(f"Recommended cuisine: {recommendation_result['recommended_cuisine']}")
    print(f"Recommended recipe type: {recommendation_result['recommended_recipe_type']}")

    print("\nPriority ingredients:")
    for ingredient in recommendation_result["priority_ingredients"]:
        print(f"  - {ingredient}")

    print("\nOptional ingredients:")
    for ingredient in recommendation_result["optional_ingredients"]:
        print(f"  - {ingredient}")

    print("\nTop recipe matches:")
    for i, recipe in enumerate(recommendation_result["top_recipe_matches"][:5], 1):
        print(
            f"{i}. {recipe['recipe_name']} "
            f"({recipe['cuisine']} | {recipe['recipe_type']}) "
            f"-> {recipe['similarity_score']:.4f}"
        )

    print("==========================\n")

    print("\n===== Recommendation =====")
    print(recommendation_result)
    print("==========================\n")

    # --------------------------------------------
    # Build Prompt
    # --------------------------------------------

    prompt = build_prompt(
        processed_ingredients,
        recommendation_result,
        request.cuisine,
        request.meal_type,
        request.servings,
    )

    print("\n===== Prompt Summary =====")
    print("Cuisine:", recommendation_result["recommended_cuisine"])
    print("Recipe Type:", recommendation_result["recommended_recipe_type"])
    print("Priority Ingredients:", recommendation_result["priority_ingredients"])
    print("Optional Ingredients:", recommendation_result["optional_ingredients"])
    print("Prompt length:", len(prompt), "characters")
    print("==========================\n")

    # --------------------------------------------
    # Generate Recipe with Gemini
    # --------------------------------------------

    
    try:
        gemini_response = generate_recipe(prompt)

    except Exception as e:
        print(f"Gemini unavailable, using local dataset fallback: {e}")

        recipe_data = generate_recipe_from_dataset(
            processed_ingredients,
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
                cuisine=recipe_data["cuisine"],
                recipe_type=recipe_data["recipe_type"],
                cooking_tips=json.dumps(
                    recipe_data["cooking_tips"]
                ),
                cooking_time=recipe_data["cooking_time"],
                servings=recipe_data["servings"],
                user_id=user_id,
            )
            return recipe
        return recipe_data

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
    # Save Recipe (only for authenticated users)
    # --------------------------------------------

    if user_id is not None:
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
                cooking_tips=json.dumps(
                    recipe_data["cooking_tips"]
                ),
                cooking_time=recipe_data["cooking_time"],
                servings=recipe_data["servings"],
                user_id=user_id,
            )
        except Exception as e:
            raise RecipeGenerationError(
                f"Failed to save recipe: {e}"
            )

        return recipe

    # Guest user: return recipe without saving
    return recipe_data

   
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
