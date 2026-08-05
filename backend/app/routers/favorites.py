from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services import favorite_service
from app.schemas.recipe import FavoriteRecipe

router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.get("/", response_model=list[FavoriteRecipe])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return favorite_service.get_user_favorites(
        db,
        current_user.id,
    )


@router.post("/{recipe_id}", status_code=status.HTTP_201_CREATED)
def add_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = favorite_service.get_favorite(
        db,
        current_user.id,
        recipe_id,
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Recipe already favorited",
        )

    return favorite_service.add_favorite(
        db,
        current_user.id,
        recipe_id,
    )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite = favorite_service.get_favorite(
        db,
        current_user.id,
        recipe_id,
    )

    if not favorite:
        raise HTTPException(
            status_code=404,
            detail="Favorite not found",
        )

    favorite_service.remove_favorite(
        db,
        favorite,
    )