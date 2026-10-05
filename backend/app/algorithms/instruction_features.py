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

MAX_QUESTIONS = 4
MIN_EXTRA_BALANCE = 0.30           # 2nd..4th question must split this ingredient's
                                   # recipes reasonably (1.0 = perfect 50/50 split)

MIN_VERB_STEP_STARTS = 2           # a word must start >= 2 steps to be a cooking verb
MIN_VERB_BREADTH = 4               # a verb must be used with >= 4 different ingredients
                                   # (filters one-off verbs such as "pound" or "pluck")
BACKFILL_BREADTH_RATIO = 0.30      # filler questions (tiers 2 and 3) only use verbs that are
                                   # used with at least 30% as many ingredients as the most
                                   # common verb, so "knead" is never asked about spinach
STAPLE_THRESHOLD = 0.60            # skip ingredients in > 60% of recipes (salt, water...)
GENERIC_TOKEN_MIN_NAMES = 5        # a word in >= 5 ingredient names ("powder", "seeds")
                                   # is not used to recognise an ingredient in a step

# Garnish, flavouring and seasoning items: the user has no cooking choice to make
NO_QUESTION_INGREDIENTS = {
    "lemon juice", "fresh coriander", "mint", "sugar",
    "cumin seeds", "turmeric powder", "sichuan pepper", "mustard oil",
}

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
    "cook", "drop", "top", "gently", "gradually", "well", "hard", "pan",
    "allow", "apply", "close", "finish", "prepare",
    "pack", "spread", "layer", "flip", "seal", "crack", "grease", "drizzle",
}

# Preparation steps (not a cooking choice for the user). These showed up in
# the test output as questions like "knead the yogurt" or "soak the lentils".
# Set PREP_WORDS = set() to go back to the previous behaviour.
PREP_WORDS = {
    "soak", "whisk", "coat", "knead", "melt", "blend", "mash", "ferment",
    "grind", "shred", "stuff", "wrap", "dip", "churn", "strain", "distill",
}

NON_METHOD_WORDS = NON_METHOD_WORDS | PREP_WORDS

# Words that come in front of a cooking verb ("deep fry", "stir fry",
# "dry roast", "pressure cook"). When a step starts with one of them,
# the next word is the real cooking verb.
COMPOUND_PREFIXES = {
    "deep", "shallow", "stir", "pan", "pressure", "flash", "dry", "slow",
    "charcoal", "flame", "hard", "gently", "gradually", "slowly",
}


_RECIPE_CACHE = None
_INDEX_CACHE = None
_VECTOR_CACHE = None

# Words that end in "ed"/"ing" but are NOT inflected forms
PROTECTED_VERBS = {"shred", "bleed", "feed", "seed", "speed", "weed"}

# -------------------------------------------------------
# Tokenizing helpers
# -------------------------------------------------------

def normalize_verb(word):
    """
    Light stemmer: frying/fried -> fry, boiled -> boil,
    chopped -> chop, sauteing -> saute.
    """
    word = re.sub(r"[^a-z]", "", word.lower())

    if word in PROTECTED_VERBS:
        return word

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


def _stem(word):
    """
    Very light singular stemmer used only to recognise an ingredient
    inside a step: potatoes -> potato, chillies -> chilli, onions -> onion.
    """
    w = word.lower()

    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "i"

    if len(w) > 4 and w.endswith("oes"):
        return w[:-2]

    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]

    if len(w) > 3 and w.endswith("y"):
        w = w[:-1] + "i"

    return w


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
# Load dataset
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

            ingredients = list(
                dict.fromkeys(
                    item.lower().strip()
                    for item in _parse_list(row.get("ingredients") or "[]")
                    if item.strip()
                )
            )

            steps = _parse_list(row.get("instructions") or "[]")

            recipes.append(
                {
                    "name": name,
                    "ingredients": ingredients,
                    "steps": steps,
                }
            )

    _RECIPE_CACHE = recipes
    return recipes


# -------------------------------------------------------
# Build the index (done once)
# -------------------------------------------------------

def _build_match_tokens(recipes):
    """
    For every ingredient name, the words that identify it inside a step.
    Words that occur in many ingredient names ("powder", "seeds", "green")
    are generic and are ignored when the name has other words.
    """
    names = {item for recipe in recipes for item in recipe["ingredients"]}

    name_tokens = {
        name: [_stem(w) for w in _words(name)]
        for name in names
    }

    token_count = Counter()
    for tokens in name_tokens.values():
        for token in set(tokens):
            token_count[token] += 1

    match_tokens = {}

    for name, tokens in name_tokens.items():
        distinctive = [
            token for token in tokens
            if token_count[token] < GENERIC_TOKEN_MIN_NAMES
        ]
        match_tokens[name] = set(distinctive or tokens)

    return match_tokens


def _get_index():
    """
    Learn the cooking verbs from the instructions column and link each
    verb to the ingredients it is actually used with.
    """
    global _INDEX_CACHE

    if _INDEX_CACHE is not None:
        return _INDEX_CACHE

    recipes = load_recipes()
    total = len(recipes)

    # 1. Cooking-verb lexicon: words that begin steps (an imperative verb).
    #    "deep fry", "stir fry", "dry roast" count the second word.
    step_starts = Counter()

    for recipe in recipes:
        for step in recipe["steps"]:
            words = _words(step)

            if not words:
                continue

            step_starts[normalize_verb(words[0])] += 1

            if words[0] in COMPOUND_PREFIXES and len(words) > 1:
                step_starts[normalize_verb(words[1])] += 1

    lexicon = {
        verb
        for verb, count in step_starts.items()
        if count >= MIN_VERB_STEP_STARTS
        and len(verb) > 2
        and verb not in NON_METHOD_WORDS
    }

    # 2. Verbs used anywhere in a recipe (for the plain verb features).
    # 3. Verbs used WITH each ingredient (step level link).
    match_tokens = _build_match_tokens(recipes)

    recipe_verbs = []
    recipe_assoc = []

    for recipe in recipes:
        steps = recipe["steps"]

        step_stems = [
            {_stem(w) for w in _words(step)}
            for step in steps
        ]

        step_verbs = [
            [
                verb
                for verb in (normalize_verb(w) for w in _words(step))
                if verb in lexicon
            ]
            for step in steps
        ]

        recipe_verbs.append(
            [verb for verbs in step_verbs for verb in verbs]
        )

        per_ingredient = {}

        for ingredient in recipe["ingredients"]:
            tokens = match_tokens.get(ingredient)

            if not tokens:
                continue

            found = set()

            for i, stems in enumerate(step_stems):
                if not tokens <= stems:
                    continue

                verbs = step_verbs[i]

                # "add chopped spinach and salt" has no cooking verb:
                # the method is in the next step ("stir fry ...")
                if not verbs and i + 1 < len(steps):
                    verbs = step_verbs[i + 1]

                found.update(verbs)

            if found:
                per_ingredient[ingredient] = found

        recipe_assoc.append(per_ingredient)

    # 4. Summaries used by the question generator.
    ingredient_recipes = defaultdict(set)

    for r, recipe in enumerate(recipes):
        for ingredient in recipe["ingredients"]:
            ingredient_recipes[ingredient].add(r)

    staples = {
        ingredient
        for ingredient, rs in ingredient_recipes.items()
        if total and len(rs) / total > STAPLE_THRESHOLD
    }

    ingredient_verb_recipes = defaultdict(lambda: defaultdict(set))

    for r, per_ingredient in enumerate(recipe_assoc):
        for ingredient, verbs in per_ingredient.items():
            for verb in verbs:
                ingredient_verb_recipes[ingredient][verb].add(r)

    verb_ingredients = defaultdict(set)

    for ingredient, verb_map in ingredient_verb_recipes.items():
        if ingredient in staples:
            continue

        for verb in verb_map:
            verb_ingredients[verb].add(ingredient)

    breadth = {verb: len(s) for verb, s in verb_ingredients.items()}

    max_breadth = max(breadth.values(), default=0)

    backfill_verbs = {
        v for v, b in breadth.items()
        if b >= MIN_VERB_BREADTH and b >= BACKFILL_BREADTH_RATIO * max_breadth
    }

    global_verbs = sorted(backfill_verbs, key=lambda v: (-breadth[v], v))

    # Feature tokens of each recipe: plain verbs + "ingredient|verb" pairs
    recipe_tokens = []

    for r in range(len(recipes)):
        pairs = [
            f"{ingredient}|{verb}"
            for ingredient, verbs in recipe_assoc[r].items()
            for verb in verbs
        ]
        recipe_tokens.append(recipe_verbs[r] + pairs)

    _INDEX_CACHE = {
        "recipes": recipes,
        "lexicon": lexicon,
        "recipe_tokens": recipe_tokens,
        "ingredient_recipes": ingredient_recipes,
        "ingredient_verb_recipes": ingredient_verb_recipes,
        "staples": staples,
        "breadth": breadth,
        "global_verbs": global_verbs,
        "backfill_verbs": set(global_verbs),
    }

    return _INDEX_CACHE


# -------------------------------------------------------
# Dynamic question generation
# -------------------------------------------------------

def _choose_verbs(ingredient, index):
    chosen = []

    breadth = index["breadth"]
    ingredient_recipes = index["ingredient_recipes"]
    ingredient_verb_recipes = index["ingredient_verb_recipes"]

    mine = ingredient_recipes.get(ingredient, set())

    if not mine:
        return chosen

    ranked = []

    min_support = 2 if len(mine) >= 8 else 1

    for verb, rs in ingredient_verb_recipes.get(ingredient, {}).items():
        if breadth.get(verb, 0) < MIN_VERB_BREADTH:
            continue

        if len(rs) < min_support:
            continue

        p = len(rs) / len(mine)
        balance = 1 - abs(2 * p - 1)
        ranked.append((verb, balance, len(rs)))

    ranked.sort(key=lambda item: (-item[1], -item[2], item[0]))

    for verb, balance, _ in ranked:
        if len(chosen) >= MAX_QUESTIONS:
            break

        if not chosen or balance >= MIN_EXTRA_BALANCE:
            chosen.append(verb)

    return chosen


def generate_questions(processed_ingredients):
    """
    Build cooking questions for every ingredient, learned from the
    instructions column of the dataset.
    """
    index = _get_index()

    if not index["recipes"]:
        return []

    questions = []

    for ingredient in processed_ingredients:
        # Staples (salt, water, oil...) and garnish/seasoning items
        # make meaningless questions
        if ingredient in index["staples"] or ingredient in NO_QUESTION_INGREDIENTS:
            continue

        for verb in _choose_verbs(ingredient, index):
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

    matrix = vectorizer.fit_transform(index["recipe_tokens"]).toarray()

    _VECTOR_CACHE = (vectorizer, matrix)
    return _VECTOR_CACHE


def answer_tokens(ingredient, verb):
    """
    Feature tokens of one answer: the plain verb once and the
    ingredient|verb pair (the verb used with that ingredient) twice,
    so recipes that really apply the verb to the ingredient count more.
    """
    pair = f"{ingredient}|{verb}"
    return [verb, pair, pair]


def calculate_instruction_scores(liked_tokens, disliked_tokens):
    """
    Compare the user's answers against every recipe's instruction vector.

    Score is in [0, 1]:
      0.5 = neutral, above = matches liked tokens, below = matches disliked tokens.
    Returns {recipe_name: score}.
    """
    index = _get_index()
    vectorizer, matrix = _get_vectors()

    liked_vector = vectorizer.transform([list(liked_tokens)]).toarray()[0]
    disliked_vector = vectorizer.transform([list(disliked_tokens)]).toarray()[0]

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
    for q in generate_questions(["spinach", "chicken", "potato", "rice"]):
        print(q["text"])

    liked = answer_tokens("chicken", "fry")
    disliked = answer_tokens("chicken", "boil")
    scores = calculate_instruction_scores(liked, disliked)
    top = sorted(scores.items(), key=lambda x: -x[1])[:5]
    print()
    for name, score in top:
        print(name, round(score, 3))