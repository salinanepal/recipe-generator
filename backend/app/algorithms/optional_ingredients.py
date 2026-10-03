import ast
import csv
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RECIPES_FILE = BASE_DIR / "data" / "recipes.csv"

# -------------------------------------------------------
# Tunable settings
# -------------------------------------------------------

# Ingredients used in more than this share of ALL recipes are treated as
# pantry staples (salt, water, oil...) and are never offered as options.
PANTRY_THRESHOLD = 0.50

# Maximum number of checkboxes shown for one recipe.
MAX_OPTIONS = 10

_CACHE = None


def _load():
    global _CACHE

    if _CACHE is not None:
        return _CACHE

    if not RECIPES_FILE.exists():
        raise FileNotFoundError("recipes.csv not found.")

    recipes = {}
    frequency = Counter()
    total = 0

    with open(
        RECIPES_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        for row in csv.DictReader(file):
            name = (row.get("recipe_name") or "").strip()

            if not name:
                continue

            try:
                ingredients = ast.literal_eval(
                    row.get("ingredients") or "[]"
                )
            except (ValueError, SyntaxError):
                ingredients = []

            # Keep dataset order, remove duplicates
            ingredients = list(
                dict.fromkeys(
                    str(item).lower().strip()
                    for item in ingredients
                    if str(item).strip()
                )
            )

            total += 1

            for item in ingredients:
                frequency[item] += 1

            key = name.lower()

            # First recipe with this name wins
            if key not in recipes:
                recipes[key] = ingredients

    _CACHE = {
        "recipes": recipes,
        "frequency": frequency,
        "total": total,
    }

    return _CACHE


def get_optional_ingredients(recipe_name, processed_ingredients):
    """
    Return the ingredients of the selected recipe that the user did not
    provide and that are not pantry staples.
    """
    data = _load()

    recipe_ingredients = data["recipes"].get(
        str(recipe_name).strip().lower()
    )

    if not recipe_ingredients:
        return []

    user_set = {
        item.lower().strip()
        for item in processed_ingredients
    }

    total = data["total"] or 1
    options = []

    for ingredient in recipe_ingredients:
        if ingredient in user_set:
            continue

        if data["frequency"][ingredient] / total > PANTRY_THRESHOLD:
            continue

        options.append({"name": ingredient})

    return options[:MAX_OPTIONS]


# Test
if __name__ == "__main__":
    for name, mine in [
        ("Chicken Curry", ["chicken", "onion"]),
        ("Dal Bhat", ["rice", "lentils"]),
        ("Aloo Dum", ["potato"]),
    ]:
        print(name, "->", [o["name"] for o in get_optional_ingredients(name, mine)])