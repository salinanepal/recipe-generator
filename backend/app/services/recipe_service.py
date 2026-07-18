from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.schemas.recipe import RecipeResponse


def save_recipe(
    db: Session,
    title: str,
    ingredients: str,
    instructions: str,
    cooking_time: int,
    servings: int,
    user_id: int,
):
    recipe = Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
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