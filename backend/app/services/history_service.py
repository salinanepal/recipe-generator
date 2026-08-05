from sqlalchemy.orm import Session
from app.models.recipe import Recipe


def get_user_recipes(db: Session, user_id: int):
    return (
        db.query(Recipe)
        .filter(Recipe.user_id == user_id)
        .order_by(Recipe.created_at.desc())
        .all()
    )


def get_recipe_by_id(db: Session, recipe_id: int, user_id: int):
    return (
        db.query(Recipe)
        .filter(Recipe.id == recipe_id, Recipe.user_id == user_id)
        .first()
    )


def delete_recipe(db: Session, recipe: Recipe):
    db.delete(recipe)
    db.commit()