import csv
from pathlib import Path


# -------------------------------------------------------
# File Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INGREDIENT_METADATA_FILE = (
    BASE_DIR / "data" / "ingredients_metadata.csv"
)


# -------------------------------------------------------
# Cache
# -------------------------------------------------------

_CATEGORY_CACHE = None


# -------------------------------------------------------
# Load Category Metadata
# -------------------------------------------------------

def load_category_metadata():
    """
    Build ingredient-to-category mapping
    from the master ingredient metadata file.
    """

    global _CATEGORY_CACHE

    if _CATEGORY_CACHE is not None:
        return _CATEGORY_CACHE

    if not INGREDIENT_METADATA_FILE.exists():
        raise FileNotFoundError(
            "ingredients_metadata.csv not found."
        )

    category_map = {}

    with open(
        INGREDIENT_METADATA_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            ingredient = (
                row.get("ingredient", "")
                .strip()
                .lower()
            )

            category = (
                row.get("category", "")
                .strip()
            )

            if (
                ingredient
                and category
            ):
                category_map[
                    ingredient
                ] = category

    _CATEGORY_CACHE = category_map

    return _CATEGORY_CACHE


# -------------------------------------------------------
# Classify Single Ingredient
# -------------------------------------------------------

def classify_ingredient(
    ingredient,
    category_map,
):
    """
    Classify a single ingredient.
    """

    return category_map.get(
        ingredient,
        None,
    )


# -------------------------------------------------------
# Classify Ingredient List
# -------------------------------------------------------

def classify_ingredients(
    ingredients,
):
    """
    Classify processed ingredients into
    food categories.
    """

    category_map = (
        load_category_metadata()
    )

    ingredient_categories = {}

    category_groups = {}

    unknown_ingredients = []

    for ingredient in ingredients:

        category = classify_ingredient(
            ingredient,
            category_map,
        )

        if category is None:

            unknown_ingredients.append(
                ingredient
            )

            continue

        ingredient_categories[
            ingredient
        ] = category

        category_groups.setdefault(
            category,
            [],
        ).append(
            ingredient
        )

    return {

        "ingredient_categories":
            ingredient_categories,

        "category_groups":
            category_groups,

        "unknown_ingredients":
            unknown_ingredients,
    }


# -------------------------------------------------------
# Test
# -------------------------------------------------------

if __name__ == "__main__":

    test_ingredients = [

        "tomato",
        "potato",
        "buff meat",
        "rice",
        "garlic",
        "timur",
        "unknown ingredient",

    ]

    result = classify_ingredients(
        test_ingredients
    )

    print("\nIngredient Categories:\n")

    for ingredient, category in (
        result[
            "ingredient_categories"
        ].items()
    ):

        print(
            f"{ingredient} -> {category}"
        )

    print("\nCategory Groups:\n")

    for category, items in (
        result[
            "category_groups"
        ].items()
    ):

        print(
            f"{category}: {items}"
        )

    print("\nUnknown Ingredients:\n")

    print(
        result[
            "unknown_ingredients"
        ]
    )