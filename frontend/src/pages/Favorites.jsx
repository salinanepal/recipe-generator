import { useEffect, useState } from "react";
import { Trash2, Clock, Users, X } from "lucide-react";
import { getFavorites, getRecipeDetail, removeFavorite } from "../services/recipeService";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        const data = await getFavorites();
        setFavorites(data);
      } catch {
        setError("Couldn't load your favorite recipes.");
      }finally {
        setLoading(false);
      }
    };
    fetchFavorites();
  }, []);

  const handleDetail = async (id) => {
    setDetailLoading(true);
    try {
      const detail = await getRecipeDetail(id);
      setSelected(detail);
    } catch {
      setError("Couldn't load recipe details.");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleRemove = async (id) => {
    if (!window.confirm("Remove this recipe from your favorites?")) return;
    try {
      await removeFavorite(id);
      setFavorites((prev) => prev.filter((recipe) => recipe.id !== id));
    } catch {
      setError("Couldn't remove the recipe from your favorites.");
    }
  };

  if (loading) {
    return <p className="p-10 text-center text-ink/60">Loading favorites...</p>;
  }

  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl text-ink">Favorites</h1>
        <p className="mt-2 text-sm text-ink/60">
          Recipes you save will appear here for quick access anytime.
        </p>

        {error && (
          <p className="mt-4 rounded-md bg-category-protein/10 px-3 py-2 text-sm text-category-protein">
            {error}
          </p>
        )}

        {favorites.length === 0 ? (
          <p className="mt-8 text-sm text-ink/60">
            You haven't saved any favorite recipes yet.
          </p>
        ) : (
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {favorites.map((recipe) => (
              <div key={recipe.id} onClick={() => handleDetail(recipe.id)} className="card cursor-pointer hover:border-basil transition-colors">
                <div className="flex items-start justify-between">
                  <h2 className="font-display text-lg text-ink">{recipe.title}</h2>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemove(recipe.id);
                    }}
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
                <div className="mt-2 space-y-1 text-sm text-ink/70">
                  {JSON.parse(selected.ingredients).map((ing, i) => (
                    <p key={i}>• {ing.quantity} {ing.name}</p>
                  ))}
                </div>

                <h3 className="mt-4 text-sm font-medium text-ink">Instructions</h3>
                <div className="mt-2 space-y-2 text-sm text-ink/70">
                  {JSON.parse(selected.instructions).map((step, i) => (
                    <p key={i}>{i + 1}. {step}</p>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}