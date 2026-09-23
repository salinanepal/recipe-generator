import ast
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from app.algorithms.cooking_methods import extract_cooking_methods

INGREDIENT_FAMILIES = {
    "lentils": {
        "lentils",
        "red lentils",
        "black gram lentils",
        "split yellow lentils",
    }
}

BASE_DIR = Path(__file__).resolve().parent.parent
RECIPES_FILE = BASE_DIR / "data" / "recipes.csv"

_RECIPE_CACHE = None


# Load Recipe Documents

def load_recipe_documents():
    # Load recipes and convert ingredient lists into plain text documents for TF-IDF.

    global _RECIPE_CACHE

    if _RECIPE_CACHE is not None:
        return _RECIPE_CACHE

    if not RECIPES_FILE.exists():
        raise FileNotFoundError(
            "recipes.csv not found."
        )

    recipe_names = []
    recipe_documents = []
    recipe_ingredients = []
    recipe_cuisines = []
    recipe_cooking_methods = []

    with open(
        RECIPES_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            recipe_name = row.get(
                "recipe_name",
                "",
            ).strip()

            recipe_cuisine = row.get(
                "cuisine",
                "",
            ).strip()

            ingredients = row.get(
                "ingredients",
                "[]",
            )

            try:
                ingredients = ast.literal_eval(
                    ingredients
                )
            except (
                ValueError,
                SyntaxError,
            ):
                ingredients = []

            # parse instructions the same way ingredients are parsed,
            # then extract which cooking methods this recipe actually uses
            instructions = row.get(
                "instructions",
                "[]",
            )

            try:
                instructions = ast.literal_eval(
                    instructions
                )
            except (
                ValueError,
                SyntaxError,
            ):
                instructions = []

            cooking_methods = extract_cooking_methods(
                instructions
            )

            recipe_ingredients.append(
                ingredients
            )

            recipe_cuisines.append(
                recipe_cuisine
            )

            recipe_cooking_methods.append(
                cooking_methods
            )

            document = " ||| ".join(
                ingredient.lower().strip()
                for ingredient in ingredients
            )

            recipe_names.append(
                recipe_name
            )

            recipe_documents.append(
                document
            )

    _RECIPE_CACHE = {
        "recipe_names": recipe_names,
        "recipe_documents": recipe_documents,
        "recipe_ingredients": recipe_ingredients,
        "recipe_cuisines": recipe_cuisines,
        "recipe_cooking_methods": recipe_cooking_methods,
    }

    return _RECIPE_CACHE


# Build TF-IDF Vectors

def build_tfidf_vectors(
    processed_ingredients,
):

    recipe_data = load_recipe_documents()

    recipe_names = recipe_data[
        "recipe_names"
    ]

    recipe_documents = recipe_data[
        "recipe_documents"
    ]

    recipe_ingredients = recipe_data[
        "recipe_ingredients"
    ]

    recipe_cuisines = recipe_data[
        "recipe_cuisines"
    ]

    user_document = " ||| ".join(
        ingredient.lower().strip()
        for ingredient in processed_ingredients
    )

    all_documents = (
        recipe_documents
        + [user_document]
    )

    vectorizer = TfidfVectorizer(
        analyzer=lambda document: [
            ingredient.strip()
            for ingredient in document.split("|||")
            if ingredient.strip()
        ]
    )

    tfidf_matrix = vectorizer.fit_transform(
        all_documents
    )

    recipe_vectors = tfidf_matrix[:-1]

    user_vector = tfidf_matrix[-1]

    return {
        "recipe_names": recipe_names,
        "recipe_ingredients": recipe_ingredients,
        "recipe_cuisines": recipe_cuisines,
        "recipe_vectors": recipe_vectors,
        "user_vector": user_vector,
        "feature_names": vectorizer.get_feature_names_out(),
        "idf_weights": vectorizer.idf_,
        "processed_ingredients": processed_ingredients,
    }


# Test

if __name__ == "__main__":

    test_ingredients = [
        "tomato",
        "garlic",
        "onion",
    ]

    result = build_tfidf_vectors(
        test_ingredients
    )

    print("\nRecipe Count:")
    print(
        len(
            result["recipe_names"]
        )
    )

    print("\nVocabulary Size:")
    print(
        len(
            result["feature_names"]
        )
    )

    print("\nUser Vector Shape:")
    print(
        result[
            "user_vector"
        ].shape
    )

    print("\nRecipe Matrix Shape:")
    print(
        result[
            "recipe_vectors"
        ].shape
    )