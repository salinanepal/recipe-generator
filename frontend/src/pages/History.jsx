import { useEffect, useState } from "react";
import { Trash2, Clock, Users, X, Heart } from "lucide-react";
import {
  getHistory,
  getRecipeDetail,
  getFavorites,
  addFavorite,
  removeFavorite,
  deleteRecipeFromHistory,
} from "../services/recipeService";

export default function History() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [selected, setSelected] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const [message, setMessage] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [history, favorites] = await Promise.all([
          getHistory(),
          getFavorites(),
        ]);

        setRecipes(history);

        setFavoriteIds(
          new Set(
            favorites.map(
              (favorite) => favorite.recipe_id ?? favorite.id
            )
          )
        );
      } catch {
        setError("Couldn't load your recipe history");
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const showMessage = (text) => {
    setMessage(text);

    setTimeout(() => {
      setMessage("");
    }, 3500);
  };

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

  const handleFavorite = async (id, e) => {
    e.stopPropagation();

    const isFavorite = favoriteIds.has(id);

    try {
      if (isFavorite) {
        await removeFavorite(id);

        setFavoriteIds((prev) => {
          const updated = new Set(prev);
          updated.delete(id);
          return updated;
        });

        showMessage("Removed from favorites");
      } else {
        await addFavorite(id);

        setFavoriteIds((prev) => {
          const updated = new Set(prev);
          updated.add(id);
          return updated;
        });

        showMessage("Added to favorites");
      }
    } catch {
      setError(
        isFavorite
          ? "Couldn't remove that recipe from favorites"
          : "Couldn't add that recipe to favorites"
      );
    }
  };

  const handleDelete = async () => {
    if (!confirmDelete) return;

    try {
      await deleteRecipeFromHistory(confirmDelete);

      setRecipes((prev) =>
        prev.filter((recipe) => recipe.id !== confirmDelete)
      );

      if (selected?.id === confirmDelete) {
        setSelected(null);
      }

      setConfirmDelete(null);
      showMessage("Recipe deleted from history");
    } catch {
      setError("Couldn't delete that recipe");
      setConfirmDelete(null);
    }
  };

  if (loading) {
    return (
      <p className="p-10 text-center text-ink/60">
        Loading your history...
      </p>
    );
  }

  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl text-ink">
          Recipe History
        </h1>

        {message && (
          <p
            className={`mt-4 rounded-md px-3 py-2 text-sm ${
              message === "Removed from favorites"
                ? "bg-red-50 text-red-600"
                : "bg-basil/10 text-basil"
            }`}
          >
            {message}
          </p>
        )}

        {error && (
          <p className="mt-4 error-message">
            {error}
          </p>
        )}

        {recipes.length === 0 ? (
          <p className="mt-8 text-sm text-ink/60">
            No recipes generated yet — they'll show up here once you create one.
          </p>
        ) : (
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {recipes.map((recipe) => {
              const isFavorite = favoriteIds.has(recipe.id);

              return (
                <div
                  key={recipe.id}
                  onClick={() => openDetail(recipe.id)}
                  className="card cursor-pointer transition-colors hover:border-basil"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="font-display text-lg text-ink">
                      {recipe.title}
                    </h2>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) =>
                          handleFavorite(recipe.id, e)
                        }
                        aria-label={
                          isFavorite
                            ? "Remove from favorites"
                            : "Add to favorites"
                        }
                        className={
                          isFavorite
                            ? "text-basil transition-colors"
                            : "text-ink/40 transition-colors hover:text-basil"
                        }
                      >
                        <Heart
                          size={18}
                          fill={
                            isFavorite
                              ? "currentColor"
                              : "none"
                          }
                        />
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConfirmDelete(recipe.id);
                        }}
                        aria-label="Delete recipe"
                        className="text-ink/40 transition-colors hover:text-red-600"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>

                  <div className="mt-3 flex gap-4 text-sm text-ink/60">
                    {recipe.cooking_time && (
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {recipe.cooking_time} min
                      </span>
                    )}

                    {recipe.servings && (
                      <span className="flex items-center gap-1">
                        <Users size={14} />
                        {recipe.servings} servings
                      </span>
                    )}
                  </div>

                  <p className="mt-2 text-xs text-ink/40">
                    {new Date(
                      recipe.created_at
                    ).toLocaleDateString()}
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Recipe detail popup */}
      {(selected || detailLoading) && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-ink/40 px-4"
          onClick={() => setSelected(null)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="card max-h-[80vh] w-full max-w-lg overflow-y-auto"
          >
            {detailLoading ? (
              <p className="text-sm text-ink/60">
                Loading...
              </p>
            ) : (
              <>
                <div className="flex items-start justify-between">
                  <h2 className="font-display text-xl text-ink">
                    {selected.title}
                  </h2>

                  <button
                    onClick={() => setSelected(null)}
                    aria-label="Close"
                  >
                    <X
                      size={20}
                      className="text-ink/40 hover:text-ink"
                    />
                  </button>
                </div>

                <h3 className="mt-4 text-sm font-medium text-ink">
                  Ingredients
                </h3>

                <div className="mt-2 space-y-1 text-sm text-ink/70">
                  {JSON.parse(selected.ingredients).map(
                    (ing, i) => (
                      <p key={i}>
                        • {ing.quantity} {ing.name}
                      </p>
                    )
                  )}
                </div>

                <h3 className="mt-4 text-sm font-medium text-ink">
                  Instructions
                </h3>

                <div className="mt-2 space-y-2 text-sm text-ink/70">
                  {JSON.parse(selected.instructions).map(
                    (step, i) => (
                      <p key={i}>
                        {i + 1}. {step}
                      </p>
                    )
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Delete confirmation popup */}
      {confirmDelete && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40 px-4"
          onClick={() => setConfirmDelete(null)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-sm rounded-lg border border-clay bg-paper p-6 shadow-lg"
          >
            <h2 className="font-display text-xl text-ink">
              Delete recipe?
            </h2>

            <p className="mt-2 text-sm text-ink/60">
              Are you sure you want to delete this recipe from your history?
            </p>

            <div className="mt-5 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setConfirmDelete(null)}
                className="rounded-md border border-clay px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-basil"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleDelete}
                className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
