import csv
import re
from difflib import get_close_matches
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

_INGREDIENT_CACHE = None


# -------------------------------------------------------
# Clean Ingredient
# -------------------------------------------------------

def clean_ingredient(ingredient):
    """
    Clean ingredient text.
    """

    ingredient = str(ingredient).lower().strip()

    ingredient = re.sub(
        r"\s+",
        " ",
        ingredient,
    )

    ingredient = re.sub(
        r"[^a-z0-9\s\-]",
        "",
        ingredient,
    )

    ingredient = re.sub(
        r"-+",
        "-",
        ingredient,
    )

    return ingredient.strip()


# -------------------------------------------------------
# Normalize Ingredient
# -------------------------------------------------------

IRREGULAR_PLURALS = {
    "tomatoes": "tomato",
    "potatoes": "potato",
    "chilies": "chili",
    "chillies": "chili",
    "leaves": "leaf",
    "mangoes": "mango",
}


def normalize_ingredient(ingredient):
    """
    Normalize simple plural ingredient names.
    """

    if ingredient in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[ingredient]

    if (
        ingredient.endswith("ies")
        and len(ingredient) > 3
    ):
        return ingredient[:-3] + "y"

    if (
        ingredient.endswith("s")
        and not ingredient.endswith("ss")
        and len(ingredient) > 3
    ):
        return ingredient[:-1]

    return ingredient


# -------------------------------------------------------
# Load Ingredient Metadata
# -------------------------------------------------------

def load_ingredient_metadata():
    """
    Build ingredient vocabulary and synonym mapping
    from the master ingredient metadata file.
    """

    global _INGREDIENT_CACHE

    if _INGREDIENT_CACHE is not None:
        return _INGREDIENT_CACHE

    if not INGREDIENT_METADATA_FILE.exists():
        raise FileNotFoundError(
            "ingredients_metadata.csv not found."
        )

    vocabulary = set()

    synonym_map = {}

    with open(
        INGREDIENT_METADATA_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            canonical = clean_ingredient(
                row.get(
                    "ingredient",
                    "",
                )
            )

            if not canonical:
                continue

            vocabulary.add(canonical)

            synonym_map[canonical] = canonical

            synonyms = row.get(
                "synonyms",
                "",
            )

            if not synonyms:
                continue

            for synonym in synonyms.split(";"):

                synonym = clean_ingredient(
                    synonym
                )

                if synonym:

                    synonym_map[synonym] = canonical

    _INGREDIENT_CACHE = {
        "vocabulary": vocabulary,
        "synonym_map": synonym_map,
    }

    return _INGREDIENT_CACHE


# -------------------------------------------------------
# Correct Ingredient Spelling
# -------------------------------------------------------

def correct_spelling(
    ingredient,
    searchable_names,
    cutoff=0.85,
):
    """
    Find closest known ingredient name.
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
# Process Single Ingredient
# -------------------------------------------------------

def process_ingredient(
    ingredient,
    vocabulary,
    synonym_map,
):
    """
    Process one ingredient.
    """

    original = ingredient

    ingredient = clean_ingredient(
        ingredient
    )

    ingredient = normalize_ingredient(
        ingredient
    )

    searchable_names = set(
        synonym_map.keys()
    )

    ingredient = correct_spelling(
        ingredient,
        searchable_names,
    )

    canonical = synonym_map.get(
        ingredient,
        ingredient,
    )

    is_valid = canonical in vocabulary

    return {
        "original": original,
        "processed": canonical,
        "valid": is_valid,
    }


# -------------------------------------------------------
# Preprocess Ingredient List
# -------------------------------------------------------

def preprocess_ingredients(ingredients):
    """
    Preprocess user ingredient list.
    """

    metadata = load_ingredient_metadata()

    vocabulary = metadata["vocabulary"]

    synonym_map = metadata["synonym_map"]

    processed_ingredients = []

    unknown_ingredients = []

    corrections = []

    seen = set()

    seen_corrections = set()

    for ingredient in ingredients:

        result = process_ingredient(
            ingredient,
            vocabulary,
            synonym_map,
        )

        processed = result["processed"]

        if not result["valid"]:

            if (
                result["original"]
                not in unknown_ingredients
            ):
                unknown_ingredients.append(
                    result["original"]
                )

            continue

        original_cleaned = clean_ingredient(
            result["original"]
        )

        if original_cleaned != processed:

            correction_key = (
                original_cleaned,
                processed,
            )

            if (
                correction_key
                not in seen_corrections
            ):

                corrections.append(
                    {
                        "original":
                            result["original"],

                        "processed":
                            processed,
                    }
                )

                seen_corrections.add(
                    correction_key
                )

        if processed not in seen:

            processed_ingredients.append(
                processed
            )

            seen.add(processed)

    return {
        "processed_ingredients":
            processed_ingredients,

        "unknown_ingredients":
            unknown_ingredients,

        "corrections":
            corrections,
    }


# -------------------------------------------------------
# Test
# -------------------------------------------------------

if __name__ == "__main__":

    test_ingredients = [
        "Tomatoes",
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

    result = preprocess_ingredients(
        test_ingredients
    )

    print("\nProcessed ingredients:")

    print(
        result["processed_ingredients"]
    )

    print("\nUnknown ingredients:")

    print(
        result["unknown_ingredients"]
    )

    print("\nCorrections:")

    for correction in result["corrections"]:
        print(correction)