from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.recipe import RecipeSummary, RecipeDetail
from app.services import history_service

router = APIRouter(prefix="/history", tags=["Recipe History"])


@router.get("/", response_model=list[RecipeSummary])
def list_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return history_service.get_user_recipes(db, current_user.id)


@router.get("/{recipe_id}", response_model=RecipeDetail)
def get_history_item(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = history_service.get_recipe_by_id(db, recipe_id, current_user.id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = history_service.get_recipe_by_id(db, recipe_id, current_user.id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    history_service.delete_recipe(db, recipe)