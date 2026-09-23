from app.algorithms.tfidf import load_recipe_documents, build_tfidf_vectors
from app.algorithms.priority_matching import get_priority_candidates, order_by_importance

recipe_data = load_recipe_documents()
test_ingredients = ["rice", "chicken"]

results = get_priority_candidates(
    test_ingredients,
    recipe_data["recipe_names"],
    recipe_data["recipe_ingredients"],
)

# build_tfidf_vectors needs to run once to get feature_names + idf_weights
vector_data = build_tfidf_vectors(test_ingredients)
feature_names = vector_data["feature_names"]
idf_weights = vector_data["idf_weights"]

for r in results[:3]:
    ordered = order_by_importance(r["extra_ingredients"], feature_names, idf_weights)
    print(f"{r['name']} (gap={r['gap_size']}):")
    for ing in ordered:
        print(f"   {ing}")
    print()