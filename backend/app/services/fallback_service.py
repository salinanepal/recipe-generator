import ast
import pandas as pd
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes.csv"


def generate_recipe_from_dataset(processed_ingredients, servings=2):
    df = pd.read_csv(DATASET_PATH)

    best_score = -1
    best_row = None

    for _, row in df.iterrows():
        try:
            recipe_ingredients = ast.literal_eval(row["ingredients"])
        except Exception:
            recipe_ingredients = [
                x.strip().lower()
                for x in str(row["ingredients"]).split(",")
            ]

        recipe_set = {str(i).strip().lower() for i in recipe_ingredients}
        input_set = {str(i).strip().lower() for i in processed_ingredients}

        score = len(recipe_set.intersection(input_set))

        if score > best_score:
            best_score = score
            best_row = row

    if best_row is None:
        raise Exception("No matching recipe found in dataset.")

    try:
        instructions = ast.literal_eval(best_row["instructions"])
    except Exception:
        instructions = [
            x.strip()
            for x in str(best_row["instructions"]).split(".")
            if x.strip()
        ]

    return {
        "recipe_name": best_row["recipe_name"],
        "cuisine": best_row.get("cuisine", "General"),
        "recipe_type": best_row.get("recipe_type", "main dish"),
        "preparation_time": "15 minutes",
        "cooking_time": 20,
        "servings": servings,
        "ingredients": [
            {"name": ing, "quantity": "to taste"}
            for ing in recipe_ingredients
        ],
        "instructions": instructions,
        "cooking_tips": [
            "This recipe was generated from the local dataset fallback."
        ],
    }