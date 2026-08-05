import { useState } from "react";
import { X } from "lucide-react";

export default function GenerateRecipe() {
  const [input, setInput] = useState("");
  const [ingredients, setIngredients] = useState([]);

  const addIngredient = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const isDuplicate = ingredients.some(
      (item) => item.toLowerCase() === trimmed.toLowerCase()
    );
    if (isDuplicate) return;

    setIngredients((prev) => [...prev, trimmed]);
    setInput("");
  };

  const removeIngredient = (index) => {
    setIngredients((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addIngredient();
    }
  };

  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl text-ink">Generate Recipe</h1>
        <p className="mt-2 max-w-xl text-sm text-ink/60">
          Enter the ingredients you have on hand — we'll use them to generate a
          recipe tailored to your kitchen.
        </p>

        <div className="card mt-8">
          <label htmlFor="ingredient-input" className="form-label">
            Ingredients
          </label>

          <div className="mt-2 flex flex-col gap-3 sm:flex-row">
            <input
              id="ingredient-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. chicken, rice, garlic"
              className="input-field mt-0 flex-1"
            />
            <button
              type="button"
              onClick={addIngredient}
              className="rounded-md border border-clay px-4 py-2 text-sm font-medium text-ink hover:border-basil transition-colors sm:shrink-0"
            >
              Add
            </button>
          </div>

          {ingredients.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {ingredients.map((ingredient, index) => (
                <span
                  key={`${ingredient}-${index}`}
                  className="inline-flex items-center gap-1.5 rounded-full border border-clay bg-paper px-3 py-1 text-sm text-ink/70"
                >
                  {ingredient}
                  <button
                    type="button"
                    onClick={() => removeIngredient(index)}
                    aria-label={`Remove ${ingredient}`}
                    className="text-ink/40 hover:text-ink transition-colors"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          )}

          <button type="button" disabled className="btn-primary mt-6 w-full sm:w-auto">
            Generate Recipe
          </button>
        </div>
      </div>
    </div>
  );
}
