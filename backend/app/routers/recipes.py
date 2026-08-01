from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user

from app.core.database import get_db
from app.schemas.recipe import RecipeGenerateRequest
from app.services.recipe_service import (
    generate_recipe_with_ai,
    get_recipe_by_id,
    get_all_recipes,
)
from app.core.exceptions import RecipeGenerationError

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)

@router.post("/generate")
def generate_recipe(
    request: RecipeGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        recipe = generate_recipe_with_ai(
            db=db,
            request=request,
            user_id=current_user.id if current_user else None,
        )

        return recipe

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
