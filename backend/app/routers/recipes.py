from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.recipe import (
    OptionalIngredientsRequest,
    RecipeGenerateRequest,
    RecipeRefineRequest,
    RecipeSelectionRequest,
)
from app.services.recipe_service import (
    recommend_recipes,
    generate_selected_recipe,
    get_optional_ingredient_options,
    get_recipe_by_id,
    get_all_recipes,
)
from app.services.refinement_service import (
    get_refinement_questions,
    recommend_with_answers,
)
from app.core.exceptions import RecipeGenerationError

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

# Recommend top 3 recipes
@router.post("/recommend")
def recommend(
    request: RecipeGenerateRequest,
    db: Session = Depends(get_db),
):
    return recommend_recipes(db, request)

# Dynamic follow-up cooking questions (learned from the instructions column)
@router.post("/questions")
def questions(request: RecipeGenerateRequest):
    return get_refinement_questions(request)

# Recommend top 3 recipes, refined by the user's answers
@router.post("/recommend-refined")
def recommend_refined(request: RecipeRefineRequest):
    return recommend_with_answers(request)

# Optional ingredients the user can add to the selected recipe
@router.post("/optional-ingredients")
def optional_ingredients(request: OptionalIngredientsRequest):
    return get_optional_ingredient_options(request)

# Generate recipe after user selects one recommendation
@router.post("/generate-selected")
def generate_selected(
    request: RecipeSelectionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        return generate_selected_recipe(
            db=db,
            request=request,
            user_id=current_user.id if current_user else None,
        )
    except RecipeGenerationError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get("/")
def list_recipes(db: Session = Depends(get_db)):
    return get_all_recipes(db)

@router.get("/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = get_recipe_by_id(db, recipe_id)

    if not recipe:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return recipe