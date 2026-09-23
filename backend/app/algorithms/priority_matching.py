from app.algorithms.tfidf import build_tfidf_vectors
def get_priority_candidates(user_ingredients, recipe_names, recipe_ingredients):
    """
    Find recipes that contain ALL of the user's ingredients, ranked by
    smallest 'gap' (fewest additional ingredients needed beyond what the
    user already has).

    user_ingredients: list[str] — already preprocessed/normalized ingredients
    recipe_names: list[str] — from load_recipe_documents()["recipe_names"]
    recipe_ingredients: list[list[str]] — from load_recipe_documents()["recipe_ingredients"],
                         same order/length as recipe_names (parallel lists, not a dict)

    Returns a list of dicts, sorted smallest gap first:
      [{ "name": str, "extra_ingredients": list[str], "gap_size": int }, ...]
    """
    user_set = set(ing.lower().strip() for ing in user_ingredients)
    candidates = []

    for name, ingredients in zip(recipe_names, recipe_ingredients):
        recipe_set = set(ing.lower().strip() for ing in ingredients)
        if user_set.issubset(recipe_set):
            extra = recipe_set - user_set
            candidates.append({
                "name": name,
                "extra_ingredients": sorted(extra),
                "gap_size": len(extra),
            })

    candidates.sort(key=lambda c: c["gap_size"])
    return candidates

def order_by_importance(extra_ingredients, feature_names, idf_weights):
    # sort a recipe's extra ingredients so the most distinctive ones
    # (high IDF, rare across the dataset) come first
    idf_lookup = dict(zip(feature_names, idf_weights))
    return sorted(
        extra_ingredients,
        key=lambda ing: idf_lookup.get(ing, 0),
        reverse=True,
    )

# ingredients assumed present in every household — never asked about,
# silently included as confirmed
STAPLE_INGREDIENTS = {
    "water", "salt", "oil", "sugar", "mustard oil",
}

def split_staples(extra_ingredients):
    # returns (auto_confirmed, actually_askable)
    auto_confirmed = [i for i in extra_ingredients if i in STAPLE_INGREDIENTS]
    askable = [i for i in extra_ingredients if i not in STAPLE_INGREDIENTS]
    return auto_confirmed, askable


def get_questions_for_candidate(extra_ingredients, feature_names, idf_weights, max_questions=6):
    auto_confirmed, askable = split_staples(extra_ingredients)
    ordered = order_by_importance(askable, feature_names, idf_weights)
    questions = ordered[:max_questions]
    # anything ranked past the cap is neither asked about nor auto-confirmed —
    # it just isn't part of the interactive scoring step
    return {
        "auto_confirmed": auto_confirmed,
        "questions": questions,
    }

def get_available_styles_for_candidates(candidates, recipe_names, recipe_cooking_methods):
    # build a name -> methods lookup from the parallel lists
    methods_lookup = dict(zip(recipe_names, recipe_cooking_methods))
    styles = set()
    for c in candidates:
        styles.update(methods_lookup.get(c["name"], []))
    return sorted(styles)

def get_recommendation_flow(user_ingredients, recipe_data):
    candidates = get_priority_candidates(
        user_ingredients,
        recipe_data["recipe_names"],
        recipe_data["recipe_ingredients"],
    )

    # attach each candidate's own cooking methods — needed so the
    # frontend can filter candidates by chosen style
    methods_lookup = dict(zip(
        recipe_data["recipe_names"],
        recipe_data["recipe_cooking_methods"],
    ))
    for c in candidates:
        c["cooking_methods"] = methods_lookup.get(c["name"], [])

    available_styles = get_available_styles_for_candidates(
        candidates,
        recipe_data["recipe_names"],
        recipe_data["recipe_cooking_methods"],
    )

    # get IDF weights so each candidate's extra ingredients can be
    # ranked by distinctiveness for the question walk
    vector_data = build_tfidf_vectors(user_ingredients)
    feature_names = vector_data["feature_names"]
    idf_weights = vector_data["idf_weights"]

    for c in candidates:
        question_data = get_questions_for_candidate(
            c["extra_ingredients"],
            feature_names,
            idf_weights,
        )
        c["auto_confirmed"] = question_data["auto_confirmed"]
        c["questions"] = question_data["questions"]

    return {
        "candidates": candidates,
        "available_styles": available_styles,
    }