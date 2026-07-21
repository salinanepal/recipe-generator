import csv
from itertools import combinations
from pathlib import Path


# -------------------------------------------------------
# File Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

COMPATIBILITY_MATRIX_FILE = (
    BASE_DIR / "data" / "compatibility_matrix.csv"
)


# -------------------------------------------------------
# Compatibility Thresholds
# -------------------------------------------------------

HIGH_COMPATIBILITY_THRESHOLD = 0.70

MODERATE_COMPATIBILITY_THRESHOLD = 0.40

LOW_COMPATIBILITY_THRESHOLD = 0.10


# -------------------------------------------------------
# Cache
# -------------------------------------------------------

_COMPATIBILITY_CACHE = None


# -------------------------------------------------------
# Load Compatibility Matrix
# -------------------------------------------------------

def load_compatibility_matrix():
    """
    Load compatibility scores from CSV.
    """

    global _COMPATIBILITY_CACHE

    if _COMPATIBILITY_CACHE is not None:
        return _COMPATIBILITY_CACHE

    if not COMPATIBILITY_MATRIX_FILE.exists():
        raise FileNotFoundError(
            "compatibility_matrix.csv not found."
        )

    compatibility_map = {}

    with open(
        COMPATIBILITY_MATRIX_FILE,
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            ingredient1 = (
                row["ingredient_1"]
                .strip()
                .lower()
            )

            ingredient2 = (
                row["ingredient_2"]
                .strip()
                .lower()
            )

            score = float(
                row["score"]
            )

            compatibility_map[
                (
                    ingredient1,
                    ingredient2,
                )
            ] = score

            compatibility_map[
                (
                    ingredient2,
                    ingredient1,
                )
            ] = score

    _COMPATIBILITY_CACHE = compatibility_map

    return compatibility_map


# -------------------------------------------------------
# Get Compatibility Score
# -------------------------------------------------------

def get_compatibility_score(
    ingredient1,
    ingredient2,
    compatibility_map,
):
    """
    Get compatibility score for two ingredients.
    """

    return compatibility_map.get(
        (
            ingredient1,
            ingredient2,
        )
    )


# -------------------------------------------------------
# Analyze Compatibility
# -------------------------------------------------------

def analyze_compatibility(
    processed_ingredients,
):
    """
    Analyze compatibility levels between ingredient pairs.
    """

    compatibility_map = (
        load_compatibility_matrix()
    )

    high_compatibility_pairs = []

    moderate_compatibility_pairs = []

    low_compatibility_pairs = []

    unknown_pairs = []

    total_score = 0.0

    pair_count = 0

    for ingredient1, ingredient2 in combinations(
        processed_ingredients,
        2,
    ):

        score = (
            get_compatibility_score(
                ingredient1,
                ingredient2,
                compatibility_map,
            )
        )

        if score is None:

            unknown_pairs.append(
                {
                    "ingredient_1":
                        ingredient1,

                    "ingredient_2":
                        ingredient2,
                }
            )

            continue

        pair = {
            "ingredient_1":
                ingredient1,

            "ingredient_2":
                ingredient2,

            "score":
                score,
        }

        total_score += score

        pair_count += 1

        if (
            score
            >= HIGH_COMPATIBILITY_THRESHOLD
        ):

            high_compatibility_pairs.append(
                pair
            )

        elif (
            score
            >= MODERATE_COMPATIBILITY_THRESHOLD
        ):

            moderate_compatibility_pairs.append(
                pair
            )

        else:

            low_compatibility_pairs.append(
                pair
            )

    if pair_count > 0:

        average = (
            total_score
            / pair_count
        )

    else:

        average = 0.0

    return {

        "high_compatibility_pairs":
            high_compatibility_pairs,

        "moderate_compatibility_pairs":
            moderate_compatibility_pairs,

        "low_compatibility_pairs":
            low_compatibility_pairs,

        "unknown_pairs":
            unknown_pairs,

        "average_compatibility":
            round(
                average,
                2,
            ),
    }

# -------------------------------------------------------
# Ingredient Compatibility Scores
# -------------------------------------------------------

def calculate_ingredient_compatibility_scores(
    processed_ingredients,
):
    """
    Calculate the average compatibility score
    for each ingredient.
    """

    compatibility_map = (
        load_compatibility_matrix()
    )

    ingredient_scores = {}

    for ingredient in processed_ingredients:

        total_score = 0.0

        known_pairs = 0

        for other in processed_ingredients:

            if ingredient == other:
                continue

            score = get_compatibility_score(
                ingredient,
                other,
                compatibility_map,
            )

            if score is None:
                continue

            total_score += score

            known_pairs += 1

        if known_pairs > 0:

            ingredient_scores[
                ingredient
            ] = round(
                total_score / known_pairs,
                2,
            )

        else:

            ingredient_scores[
                ingredient
            ] = 0.0

    return ingredient_scores

# -------------------------------------------------------
# Test
# -------------------------------------------------------

if __name__ == "__main__":

    test_ingredients = [

        "rice",
        "buff meat",
        "tomato",
        "timur",

    ]

    result = analyze_compatibility(
        test_ingredients
    )

    print(
        "\nHigh Compatibility Pairs:\n"
    )

    for pair in result[
        "high_compatibility_pairs"
    ]:

        print(pair)

    print(
        "\nModerate Compatibility Pairs:\n"
    )

    for pair in result[
        "moderate_compatibility_pairs"
    ]:

        print(pair)

    print(
        "\nLow Compatibility Pairs:\n"
    )

    for pair in result[
        "low_compatibility_pairs"
    ]:

        print(pair)

    print(
        "\nUnknown Pairs:\n"
    )

    for pair in result[
        "unknown_pairs"
    ]:

        print(pair)

    print(
        "\nAverage Compatibility:\n"
    )

    print(
        result[
            "average_compatibility"
        ]
    )
    
    print(
    "\nIngredient Compatibility Scores:\n"
  )

    scores = calculate_ingredient_compatibility_scores(
    test_ingredients
   )

    for ingredient, score in scores.items():

     print(
        ingredient,
        "->",
        score,
        )

