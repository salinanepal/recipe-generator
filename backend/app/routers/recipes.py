from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.recipe import (
    RecipeGenerateRequest,
    RecipeSelectionRequest,
    RecipeCandidatesRequest, 
)
from app.services.recipe_service import (
    recommend_recipes,
    generate_selected_recipe,
    get_recipe_by_id,
    get_all_recipes,
    get_recipe_candidates, 
)
from app.core.exceptions import RecipeGenerationError

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

#priority-candidate flow with dynamic cooking styles
@router.post("/candidates")
def candidates(
    request: RecipeCandidatesRequest,
    db: Session = Depends(get_db),
):
    return get_recipe_candidates(request)

# Recommend top 3 recipes
@router.post("/recommend")
def recommend(
    request: RecipeGenerateRequest,
    db: Session = Depends(get_db),
):
    return recommend_recipes(db, request)

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