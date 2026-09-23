COOKING_METHOD_TERMS = {
    "boil":   ["boil", "boiling", "boiled"],
    "fry":    ["fry", "frying", "fried", "deep fry", "stir fry", "stir-fried"],
    "steam":  ["steam", "steaming", "steamed"],
    "bake":   ["bake", "baking", "baked"],
    "roast":  ["roast", "roasting", "roasted"],
    "grill":  ["grill", "grilling", "grilled"],
    "saute":  ["saute", "sauté", "sauteed", "sautéed"],
    "simmer": ["simmer", "simmering", "simmered"],
}

def extract_cooking_methods(instruction_steps):
    # tokenize instruction text and match against known cooking-method terms
    text = " ".join(instruction_steps).lower()
    found = []
    for canonical, variants in COOKING_METHOD_TERMS.items():
        if any(variant in text for variant in variants):
            found.append(canonical)
    return found