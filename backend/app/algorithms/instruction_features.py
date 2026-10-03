import ast
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

from app.algorithms.cosine_similarity import calculate_cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
RECIPES_FILE = BASE_DIR / "data" / "recipes.csv"

# -------------------------------------------------------
# Tunable settings
# -------------------------------------------------------

MIN_QUESTIONS = 1                 # per ingredient
MAX_QUESTIONS = 3                 # per ingredient
MIN_VERB_STEP_STARTS = 3          # a word must start >= 3 steps to count as a verb
STAPLE_THRESHOLD = 0.60           # skip ingredients in > 60% of recipes (salt, water...)
MIN_EXTRA_QUESTION_BALANCE = 0.30 # 2nd/3rd question must split recipes reasonably well
MAX_OVERLAP = 0.80                # skip questions that split recipes the same way

# Generic kitchen words that are not useful as "cooking method" questions.
# This is a language-level list, NOT tied to any recipe or ingredient.
NON_METHOD_WORDS = {
    "add", "heat", "serve", "stir", "mix", "garnish", "wash", "cut", "peel",
    "chop", "drain", "set", "let", "place", "pour", "combine", "cool",
    "transfer", "remove", "take", "use", "keep", "make", "slice", "dice",
    "cover", "rest", "sprinkle", "season", "toss", "taste", "continue",
    "reduce", "bring", "turn", "squeeze", "crush", "pinch", "divide",
    "arrange", "pat", "scrape", "trim", "snap", "pluck", "shell", "string",
    "grate", "mince", "clean", "sift", "rub", "wear", "roll", "shape",
    "fold", "finely", "thinly", "dry", "deep", "shallow", "pressure",
    "flame", "charcoal", "for", "in", "on", "then", "when", "once", "until",
    "with", "to", "the", "and", "of", "from", "after", "before", "while",
    "if", "as", "at", "by", "into", "over", "each", "every", "all", "oil",
    "half", "small", "large", "medium", "fresh", "hot", "warm", "cold",
}

_RECIPE_CACHE = None
_INDEX_CACHE = None
_VECTOR_CACHE = None


# -------------------------------------------------------
# Tokenizing helpers
# -------------------------------------------------------

def normalize_verb(word):
    """
    Light stemmer: frying/fried -> fry, boiled -> boil,
    chopped -> chop, sauteing -> saute.
    """
    word = re.sub(r"[^a-z]", "", word.lower())

    if len(word) <= 3:
        return word

    if word.endswith("ied") and len(word) > 4:
        return word[:-3] + "y"

    for suffix in ("ing", "ed"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            stem = word[: -len(suffix)]

            if (
                len(stem) >= 3
                and stem[-1] == stem[-2]
                and stem[-1] not in "lsz"
            ):
                stem = stem[:-1]

            return stem

    return word


def _words(text):
    return re.findall(r"[a-z]+", str(text).lower())


def _parse_list(value):
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, (list, tuple)):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return []


# -------------------------------------------------------
# Load dataset + build verb index
# -------------------------------------------------------

def load_recipes():
    global _RECIPE_CACHE

    if _RECIPE_CACHE is not None:
        return _RECIPE_CACHE

    if not RECIPES_FILE.exists():
        raise FileNotFoundError("recipes.csv not found.")

    recipes = []

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

            ingredients = {
                item.lower().strip()
                for item in _parse_list(row.get("ingredients", "[]"))
            }

            steps = _parse_list(row.get("instructions", "[]"))

            recipes.append(
                {
                    "name": name,
                    "ingredients": ingredients,
                    "steps": steps,
                }
            )

    _RECIPE_CACHE = recipes
    return recipes


def _get_index():
    """
    Learn the cooking-verb lexicon from the instructions column and
    tag every recipe with the verbs it uses.
    """
    global _INDEX_CACHE

    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    recipes = load_recipes()

    # Every instruction step starts with an imperative verb.
    step_starts = Counter()

    for recipe in recipes:
        for step in recipe["steps"]:
            words = _words(step)
            if words:
                step_starts[normalize_verb(words[0])] += 1

    lexicon = {
        verb
        for verb, count in step_starts.items()
        if count >= MIN_VERB_STEP_STARTS
        and len(verb) > 2
        and verb not in NON_METHOD_WORDS
    }

    recipe_verbs = []
    verb_sets = []

    for recipe in recipes:
        found = []

        for step in recipe["steps"]:
            for word in _words(step):
                verb = normalize_verb(word)
                if verb in lexicon:
                    found.append(verb)

        recipe_verbs.append(found)
        verb_sets.append(set(found))

    _INDEX_CACHE = {
        "recipes": recipes,
        "lexicon": lexicon,
        "recipe_verbs": recipe_verbs,
        "verb_sets": verb_sets,
    }

    return _INDEX_CACHE


# -------------------------------------------------------
# Dynamic question generation
# -------------------------------------------------------

def _rank_verbs(recipe_indices, index):
    """
    Rank verbs by how evenly they split the given recipes.
    A verb used by ~50% of recipes is the most informative question.
    """
    n = len(recipe_indices)
    holders = defaultdict(set)

    for i in recipe_indices:
        for verb in index["verb_sets"][i]:
            holders[verb].add(i)

    ranked = []

    for verb, holder_set in holders.items():
        if n > 1 and len(holder_set) == n:
            continue  # every recipe uses it, so it tells us nothing

        p = len(holder_set) / n
        balance = 1 - abs(2 * p - 1)
        ranked.append((verb, balance, holder_set))

    ranked.sort(key=lambda item: (-item[1], -len(item[2]), item[0]))
    return ranked


def _overlap(set_a, set_b):
    union = set_a | set_b
    if not union:
        return 0.0
    return len(set_a & set_b) / len(union)


def _pick_verbs(ranked, already_asked):
    chosen = []
    chosen_sets = []

    def try_pick(allow_asked, limit, need_balance):
        for verb, balance, holder_set in ranked:
            if len(chosen) >= limit:
                return

            if verb in [c for c in (x[0] for x in chosen)]:
                continue

            if not allow_asked and verb in already_asked:
                continue

            if need_balance and chosen and balance < MIN_EXTRA_QUESTION_BALANCE:
                continue

            if any(
                _overlap(holder_set, other) > MAX_OVERLAP
                for other in chosen_sets
            ):
                continue

            chosen.append((verb, balance))
            chosen_sets.append(holder_set)

    # Pass 1: prefer verbs not already asked for another ingredient
    try_pick(allow_asked=False, limit=MAX_QUESTIONS, need_balance=True)

    # Pass 2: guarantee the minimum, even if we must reuse a verb
    if len(chosen) < MIN_QUESTIONS:
        try_pick(allow_asked=True, limit=MIN_QUESTIONS, need_balance=False)

    return [verb for verb, _ in chosen]


def generate_questions(processed_ingredients):
    """
    Build 1-3 cooking questions per ingredient, learned from the
    instructions column of the dataset.
    """
    index = _get_index()
    recipes = index["recipes"]
    total = len(recipes)

    if total == 0:
        return []

    questions = []
    already_asked = set()

    for ingredient in processed_ingredients:
        subset = [
            i
            for i, recipe in enumerate(recipes)
            if ingredient in recipe["ingredients"]
        ]

        # Staples (salt, water, oil...) make meaningless questions
        if len(subset) / total > STAPLE_THRESHOLD:
            continue

        ranked = _rank_verbs(subset, index) if len(subset) >= 2 else []

        # Rare ingredient: fall back to dataset-wide verbs
        if not ranked:
            ranked = _rank_verbs(list(range(total)), index)

        for verb in _pick_verbs(ranked, already_asked):
            already_asked.add(verb)

            questions.append(
                {
                    "id": f"{ingredient}:{verb}",
                    "ingredient": ingredient,
                    "verb": verb,
                    "text": f"Do you want to {verb} the {ingredient}?",
                }
            )

    return questions


# -------------------------------------------------------
# Instruction feature vectors + scoring
# -------------------------------------------------------

def _get_vectors():
    global _VECTOR_CACHE

    if _VECTOR_CACHE is not None:
        return _VECTOR_CACHE

    index = _get_index()

    vectorizer = TfidfVectorizer(
        analyzer=lambda document: document,
    )

    matrix = vectorizer.fit_transform(index["recipe_verbs"]).toarray()

    _VECTOR_CACHE = (vectorizer, matrix)
    return _VECTOR_CACHE


def calculate_instruction_scores(liked_verbs, disliked_verbs):
    """
    Compare the user's answers against every recipe's instruction vector.

    Score is in [0, 1]:
      0.5 = neutral, above = matches liked verbs, below = matches disliked verbs.
    Returns {recipe_name: score}.
    """
    index = _get_index()
    vectorizer, matrix = _get_vectors()

    liked_vector = vectorizer.transform([list(liked_verbs)]).toarray()[0]
    disliked_vector = vectorizer.transform([list(disliked_verbs)]).toarray()[0]

    scores = {}

    for i, recipe in enumerate(index["recipes"]):
        recipe_vector = matrix[i]

        liked_similarity = calculate_cosine_similarity(
            liked_vector,
            recipe_vector,
        )

        disliked_similarity = calculate_cosine_similarity(
            disliked_vector,
            recipe_vector,
        )

        score = 0.5 + 0.5 * (liked_similarity - disliked_similarity)
        scores[recipe["name"]] = max(0.0, min(1.0, score))

    return scores


# Test
if __name__ == "__main__":
    for q in generate_questions(["chicken", "potato", "tomato", "rice"]):
        print(q["text"])

    scores = calculate_instruction_scores(["fry"], ["boil"])
    top = sorted(scores.items(), key=lambda x: -x[1])[:5]
    print()
    for name, score in top:
        print(name, round(score, 3))