import ast
import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = Path(__file__).resolve().parent.parent
RECIPES_FILE = BASE_DIR / "data" / "recipes.csv"

_RECIPE_CACHE = None


# Load Recipe Documents

def load_recipe_documents():
    """
    Load recipes and convert ingredient lists
    into plain text documents for TF-IDF.
    """

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

            recipe_ingredients.append(
                ingredients
            )

            recipe_cuisines.append(
                recipe_cuisine
            )

            document = " ".join(
                ingredient.lower()
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
    }

    return _RECIPE_CACHE


# Build TF-IDF Vectors

def build_tfidf_vectors(
    processed_ingredients,
):
    """
    Build TF-IDF vectors for recipes
    and the user's ingredients.
    """

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

    user_document = " ".join(
        processed_ingredients
    )

    all_documents = (
        recipe_documents
        + [user_document]
    )

    vectorizer = TfidfVectorizer()

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