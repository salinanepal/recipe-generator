from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.recipe import Recipe


def get_user_favorites(db: Session, user_id: int):
    return (
        db.query(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


def get_favorite(db: Session, user_id: int, recipe_id: int):
    return (
        db.query(Favorite)
        .filter(
            Favorite.user_id == user_id,
            Favorite.recipe_id == recipe_id,
        )
        .first()
    )


def add_favorite(db: Session, user_id: int, recipe_id: int):
    favorite = Favorite(
        user_id=user_id,
        recipe_id=recipe_id,
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


def remove_favorite(db: Session, favorite: Favorite):
    db.delete(favorite)
    db.commit()