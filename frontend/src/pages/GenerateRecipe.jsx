import { useState } from "react";
import { X } from "lucide-react";
import { generateRecipe } from "../services/recipeService";

export default function GenerateRecipe() {
  const [input, setInput] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [recipe, setRecipe] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [cuisine, setCuisine] = useState("");
  const [mealType, setMealType] = useState("");
  const [servings, setServings] = useState(2);
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

  const handleGenerate = async () => {
    if (ingredients.length === 0) {
      setError("Please add at least one ingredient.");
      return;
    }
  
    try {
      setLoading(true);
      setError("");
  
      const data = await generateRecipe({
        ingredients,
        cuisine: cuisine || null,
        meal_type: mealType || null,
        servings,
      });
  
      setRecipe(data);
    } catch (err) {
      console.error(err);
  
      setError(
        err.response?.data?.detail ||
        "Failed to generate recipe."
      );
    } finally {
      setLoading(false);
    }
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
          <div className="mt-6">
  <label className="form-label">Cuisine</label>

  <select
    value={cuisine}
    onChange={(e) => setCuisine(e.target.value)}
    className="input-field mt-2"
  >
    <option value="">Any Cuisine</option>
    <option value="Nepali">Nepali</option>
    <option value="Indian">Indian</option>
    <option value="Chinese">Chinese</option>
    <option value="Italian">Italian</option>
    <option value="Japanese">Japanese</option>
    <option value="Mexican">Mexican</option>
    <option value="Thai">Thai</option>
    <option value="American">American</option>
  </select>
</div>

<div className="mt-6">
  <label className="form-label">Meal Type</label>

  <select
    value={mealType}
    onChange={(e) => setMealType(e.target.value)}
    className="input-field mt-2"
  >
    <option value="">Any Meal</option>
    <option value="Breakfast">Breakfast</option>
    <option value="Lunch">Lunch</option>
    <option value="Dinner">Dinner</option>
    <option value="Snack">Snack</option>
    <option value="Dessert">Dessert</option>
  </select>
</div>

<div className="mt-6">
  <label className="form-label">Servings</label>

  <input
    type="number"
    min="1"
    max="10"
    value={servings}
    onChange={(e) => setServings(Number(e.target.value))}
    className="input-field mt-2"
  />
</div>

<button
  type="button"
  onClick={handleGenerate}
  disabled={loading}
  className="btn-primary mt-6 w-full sm:w-auto"
>
  {loading ? "Generating..." : "Generate Recipe"}
</button>
{recipe && (
  <>
    {recipe.analysis && (
      <div className="card mt-8 space-y-6">

        {recipe.analysis.recognized?.length > 0 && (
          <div>
            <h3 className="font-semibold">
              Recognized Ingredients
            </h3>

            <ul className="mt-2 list-disc list-inside">
              {recipe.analysis.recognized.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {recipe.analysis.corrections?.length > 0 && (
          <div>
            <h3 className="font-semibold">
              Corrections
            </h3>

            <ul className="mt-2 list-disc list-inside">
              {recipe.analysis.corrections.map((item, i) => (
                <li key={i}>
                  {item.original} → {item.corrected}
                </li>
              ))}
            </ul>
          </div>
        )}

        {recipe.analysis.removed?.length > 0 && (
          <div>
            <h3 className="font-semibold">
              Ignored Ingredients
            </h3>

            <ul className="mt-2 list-disc list-inside">
              {recipe.analysis.removed.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}

        {recipe.analysis.recommended?.length > 0 && (
          <div>
            <h3 className="font-semibold">
              Recommended Ingredients
            </h3>

            <ul className="mt-2 list-disc list-inside">
              {recipe.analysis.recommended.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    )}

    <div className="card mt-8">
      <h2 className="font-display text-2xl">
        {recipe.title}
      </h2>

      <p className="mt-2 text-sm text-ink/60">
        {recipe.cuisine} · {recipe.recipe_type}
      </p>

      <div className="mt-6">
        <h3 className="font-semibold">
          Ingredients
        </h3>

        {recipe.ingredients.map((ing, i) => (
          <p key={i}>
            • {ing.quantity} {ing.name}
          </p>
        ))}
      </div>

      <div className="mt-6">
        <h3 className="font-semibold">
          Instructions
        </h3>

        {recipe.instructions.map((step, i) => (
          <p key={i}>
            {i + 1}. {step}
          </p>
        ))}
      </div>

      <div className="mt-6">
        <h3 className="font-semibold">
          Cooking Tips
        </h3>

        <ul className="list-disc list-inside">
          {recipe.cooking_tips.map((tip, i) => (
            <li key={i}>{tip}</li>
          ))}
        </ul>
      </div>
    </div>
  </>
)}

{error && (
  <p className="mt-4 text-red-600">
    {error}
  </p>
)}
        </div>
      </div>
    </div>
  );
}
