import csv
import re
from difflib import get_close_matches
from pathlib import Path

# -------------------------------------------------------
# File Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INGREDIENT_METADATA_FILE = BASE_DIR / "data" / "ingredients_metadata.csv"
INGREDIENT_VOCABULARY_FILE = BASE_DIR / "data" / "ingredient_vocabulary.csv"

# -------------------------------------------------------
# Cache
# -------------------------------------------------------

_METADATA_CACHE = None
_VOCABULARY_CACHE = None

# Irregular plural mappings
IRREGULAR_PLURALS = {
    "tomatoes": "tomato",
    "potatoes": "potato",
    "chilies": "chili",
    "chillies": "chili",
    "leaves": "leaf",
    "mangoes": "mango",
    "radishes": "radish",
}

# -------------------------------------------------------
# Clean Ingredient
# -------------------------------------------------------

def clean_ingredient(ingredient):
    """
    Clean ingredient text and strip common quantity/unit prefixes.
    """
    ingredient = str(ingredient).lower().strip()

    # Strip leading units/quantities (e.g., "100g timur" -> "timur")
    ingredient = re.sub(
        r"^[\d\.\/]+\s*(g|kg|tbsp|tsp|cup|cups|pinch|gram|grams|ml|liter|liters)?\s*(of)?\s*",
        "",
        ingredient,
    )

    ingredient = re.sub(r"\s+", " ", ingredient)
    ingredient = re.sub(r"[^a-z0-9\s\-]", "", ingredient)
    ingredient = re.sub(r"-+", "-", ingredient)

    return ingredient.strip()

# -------------------------------------------------------
# Normalize Ingredient
# -------------------------------------------------------

def normalize_ingredient(ingredient, vocabulary=None):
    """
    Normalize plural ingredient names safely using vocabulary checks.
    """
    if ingredient in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[ingredient]

    # If the word itself is already in vocabulary (e.g. "molasses"), don't truncate
    if vocabulary and ingredient in vocabulary:
        return ingredient

    if ingredient.endswith("ies") and len(ingredient) > 4:
        return ingredient[:-3] + "y"

    if (
        ingredient.endswith("s")
        and not ingredient.endswith("ss")
        and len(ingredient) > 3
    ):
        candidate = ingredient[:-1]
        # Only truncate if candidate is valid or vocabulary isn't provided
        if vocabulary is None or candidate in vocabulary:
            return candidate

    return ingredient

# -------------------------------------------------------
# Load Data & Vocabulary
# -------------------------------------------------------

def load_ingredient_vocabulary():
    """
    Load all valid ingredient names from ingredient_vocabulary.csv.
    """
    global _VOCABULARY_CACHE

    if _VOCABULARY_CACHE is not None:
        return _VOCABULARY_CACHE

    if not INGREDIENT_VOCABULARY_FILE.exists():
        raise FileNotFoundError("ingredient_vocabulary.csv not found.")

    vocabulary = set()

    with open(
        INGREDIENT_VOCABULARY_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            ingredient = clean_ingredient(row.get("ingredient", ""))
            if ingredient:
                vocabulary.add(ingredient)

    _VOCABULARY_CACHE = vocabulary
    return vocabulary


def load_ingredient_metadata():
    """
    Load synonym mappings from ingredients_metadata.csv.
    """
    global _METADATA_CACHE

    if _METADATA_CACHE is not None:
        return _METADATA_CACHE

    if not INGREDIENT_METADATA_FILE.exists():
        raise FileNotFoundError("ingredients_metadata.csv not found.")

    synonym_map = {}

    with open(
        INGREDIENT_METADATA_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            canonical = clean_ingredient(row.get("ingredient", ""))
            if not canonical:
                continue

            synonym_map[canonical] = canonical
            synonyms = row.get("synonyms", "")

            if synonyms:
                for synonym in synonyms.split(";"):
                    synonym = clean_ingredient(synonym)
                    if synonym:
                        synonym_map[synonym] = canonical

    _METADATA_CACHE = synonym_map
    return synonym_map

# -------------------------------------------------------
# Correct Ingredient Spelling
# -------------------------------------------------------

def correct_spelling(ingredient, searchable_names, cutoff=0.82):
    """
    Find closest known ingredient name using SequenceMatcher.
    """
    if ingredient in searchable_names:
        return ingredient

    matches = get_close_matches(
        ingredient,
        searchable_names,
        n=1,
        cutoff=cutoff,
    )

    if matches:
        return matches[0]

    return ingredient

# -------------------------------------------------------
# Process Single & Multiple Ingredients
# -------------------------------------------------------

def process_ingredient(ingredient, vocabulary, synonym_map):
    """
    Process one ingredient.
    """
    original = ingredient

    ingredient = clean_ingredient(ingredient)
    ingredient = normalize_ingredient(ingredient, vocabulary)

    searchable_names = set(synonym_map.keys())

    ingredient = correct_spelling(ingredient, searchable_names)

    canonical = synonym_map.get(ingredient, ingredient)
    is_valid = canonical in vocabulary

    return {
        "original": original,
        "processed": canonical,
        "valid": is_valid,
    }


def preprocess_ingredients(ingredients):
    """
    Preprocess user ingredient list.
    """
    vocabulary = load_ingredient_vocabulary()
    synonym_map = load_ingredient_metadata()

    processed_ingredients = []
    unknown_ingredients = []
    corrections = []

    seen = set()
    seen_corrections = set()

    for ingredient in ingredients:
        result = process_ingredient(ingredient, vocabulary, synonym_map)
        processed = result["processed"]

        if not result["valid"]:
            if result["original"] not in unknown_ingredients:
                unknown_ingredients.append(result["original"])
            continue

        original_cleaned = clean_ingredient(result["original"])

        if original_cleaned != processed:
            correction_key = (original_cleaned, processed)
            if correction_key not in seen_corrections:
                corrections.append(
                    {
                        "original": result["original"],
                        "processed": processed,
                    }
                )
                seen_corrections.add(correction_key)

        if processed not in seen:
            processed_ingredients.append(processed)
            seen.add(processed)

    return {
        "processed_ingredients": processed_ingredients,
        "unknown_ingredients": unknown_ingredients,
        "corrections": corrections,
    }


# -------------------------------------------------------
# Test
# -------------------------------------------------------

if __name__ == "__main__":
    test_ingredients = [
        "250g Tomatoes",
        "potatos",
        "capsicum",
        "chiura",
        "gundruk",
        "timur",
        "urad dal",
        "buff meat",
        "asgd",
        "Tomatoes",
    ]

    result = preprocess_ingredients(test_ingredients)

    print("\nProcessed ingredients:")
    print(result["processed_ingredients"])

    print("\nUnknown ingredients:")
    print(result["unknown_ingredients"])

    print("\nCorrections:")
    for correction in result["corrections"]:
        print(correction)