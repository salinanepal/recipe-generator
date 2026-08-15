import ast
import pandas as pd
from pathlib import Path

DATASET_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "recipes.csv"
)


# Generate Recipe From Dataset

def generate_recipe_from_dataset(
    recipe_name,
    servings=2,
):
    df = pd.read_csv(DATASET_PATH)

    best_row = None

    for _, row in df.iterrows():

        if (
            str(row["recipe_name"]).strip().lower()
            == recipe_name.strip().lower()
        ):

            best_row = row
            break

    if best_row is None:
        raise Exception(
            "Selected recipe not found in dataset."
        )

    try:
        recipe_ingredients = ast.literal_eval(
            best_row["ingredients"]
        )
    except Exception:
        recipe_ingredients = [
            x.strip()
            for x in str(
                best_row["ingredients"]
            ).split(",")
            if x.strip()
        ]

    try:
        instructions = ast.literal_eval(
            best_row["instructions"]
        )
    except Exception:
        instructions = [
            x.strip()
            for x in str(
                best_row["instructions"]
            ).split(".")
            if x.strip()
        ]

    return {
        "recipe_name": best_row["recipe_name"],
        "cuisine": "Nepali",
        "preparation_time": "",
        "cooking_time": 0,
        "servings": servings,
        "ingredients": [
            {
                "name": ingredient,
                "quantity": "",
            }
            for ingredient in recipe_ingredients
        ],
        "instructions": instructions,
        "cooking_tips": [],
    }