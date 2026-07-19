import pandas as pd
import ast

INPUT_FILE = "app/data/RAW_recipes.csv"
OUTPUT_FILE = "app/data/foodcom_recipes.csv"

df = pd.read_csv(INPUT_FILE)

print("Total recipes:", len(df))
print(df.columns.tolist())

SUPPORTED_CUISINES = [
    "indian",
    "chinese",
    "italian",
    "mexican",
    "thai",
    "japanese",
    "korean"
]


def extract_cuisine(tags):
    try:
        tags = ast.literal_eval(tags)

        for cuisine in SUPPORTED_CUISINES:
            if cuisine in tags:
                return cuisine

        return None

    except (ValueError, SyntaxError):
        return None
    
CATEGORY_TAGS = {
    "main-dish": "main dish",
    "side-dishes": "side dish",
    "desserts": "dessert",
    "breakfast": "breakfast",
    "lunch": "lunch",
    "snacks": "snack",
    "soups-stews": "soup",
    "salads": "salad",
    "appetizers": "appetizer",
    "beverages": "beverage"
}


def extract_category(tags):
    try:
        tags = ast.literal_eval(tags)

        for tag, recipe_type in CATEGORY_TAGS.items():
            if tag in tags:
                return recipe_type

        return None

    except (ValueError, SyntaxError):
        return None

df["cuisine"] = df["tags"].apply(extract_cuisine)
df["recipe_type"] = df["tags"].apply(extract_category)

df = df[
    df["cuisine"].notna() &
    df["recipe_type"].notna()
]

df = df.rename(columns={
    "name": "recipe_name",
    "steps": "instructions"
})

df = df[
    [
        "recipe_name",
        "cuisine",
        "recipe_type",
        "ingredients",
        "instructions"
    ]
]

df.to_csv(OUTPUT_FILE, index=False)

print("\nFinal recipes:", len(df))
print("\nCuisine count:")
print(df["cuisine"].value_counts())

print("\nRecipe type count:")
print(df["recipe_type"].value_counts())

print("\nSaved to:", OUTPUT_FILE)