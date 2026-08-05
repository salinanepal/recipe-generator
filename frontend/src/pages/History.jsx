import { useEffect, useState } from "react";
import { Trash2, Clock, Users, X } from "lucide-react";
import { getHistory, getRecipeDetail, deleteRecipeFromHistory } from "../services/recipeService";

export default function History() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    getHistory()
      .then(setRecipes)
      .catch(() => setError("Couldn't load your recipe history"))
      .finally(() => setLoading(false));
  }, []);

  const openDetail = async (id) => {
    setDetailLoading(true);
    try {
      const detail = await getRecipeDetail(id);
      setSelected(detail);
    } catch {
      setError("Couldn't load that recipe");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this recipe from your history?")) return;

    try {
      await deleteRecipeFromHistory(id);
      setRecipes((prev) => prev.filter((r) => r.id !== id));
      if (selected?.id === id) setSelected(null);
    } catch {
      setError("Couldn't delete that recipe");
    }
  };

  if (loading) {
    return <p className="p-10 text-center text-ink/60">Loading your history...</p>;
  }

  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl text-ink">Recipe History</h1>

        {error && (
          <p className="mt-4 rounded-md bg-category-protein/10 px-3 py-2 text-sm text-category-protein">
            {error}
          </p>
        )}

        {recipes.length === 0 ? (
          <p className="mt-8 text-sm text-ink/60">
            No recipes generated yet — they'll show up here once you create one.
          </p>
        ) : (
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                onClick={() => openDetail(recipe.id)}
                className="card cursor-pointer hover:border-basil transition-colors"
              >
                <div className="flex items-start justify-between">
                  <h2 className="font-display text-lg text-ink">{recipe.title}</h2>
                  <button
                    onClick={(e) => handleDelete(recipe.id, e)}
                    aria-label="Delete recipe"
                    className="text-ink/40 hover:text-category-protein"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                <div className="mt-3 flex gap-4 text-sm text-ink/60">
                  {recipe.cooking_time && (
                    <span className="flex items-center gap-1">
                      <Clock size={14} /> {recipe.cooking_time} min
                    </span>
                  )}
                  {recipe.servings && (
                    <span className="flex items-center gap-1">
                      <Users size={14} /> {recipe.servings} servings
                    </span>
                  )}
                </div>

                <p className="mt-2 text-xs text-ink/40">
                  {new Date(recipe.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {(selected || detailLoading) && (
        <div
          className="fixed inset-0 flex items-center justify-center bg-ink/40 px-4"
          onClick={() => setSelected(null)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="card max-h-[80vh] w-full max-w-lg overflow-y-auto"
          >
            {detailLoading ? (
              <p className="text-sm text-ink/60">Loading...</p>
            ) : (
              <>
                <div className="flex items-start justify-between">
                  <h2 className="font-display text-xl text-ink">{selected.title}</h2>
                  <button onClick={() => setSelected(null)} aria-label="Close">
                    <X size={20} className="text-ink/40 hover:text-ink" />
                  </button>
                </div>

                <h3 className="mt-4 text-sm font-medium text-ink">Ingredients</h3>
                <p className="mt-1 whitespace-pre-wrap text-sm text-ink/70">
                  {selected.ingredients}
                </p>

                <h3 className="mt-4 text-sm font-medium text-ink">Instructions</h3>
                <p className="mt-1 whitespace-pre-wrap text-sm text-ink/70">
                  {selected.instructions}
                </p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}