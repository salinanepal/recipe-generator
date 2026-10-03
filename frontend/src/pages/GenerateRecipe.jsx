import { useState, useEffect } from "react";
import { X, Trash2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import {
  recommendRecipes,
  getRecipeQuestions,
  recommendRefined,
  getOptionalIngredients,
  generateSelectedRecipe,
  addFavorite,
} from "../services/recipeService";
import QuestionFlow from "../components/QuestionFlow";
import OptionalIngredients from "../components/OptionalIngredients";

const LOADING_MESSAGES = [
  "Reading your ingredients...",
  "Finding the perfect combination...",
  "Balancing the flavors...",
  "Putting the recipe together...",
  "Adding the finishing touches...",
  "Almost ready to serve...",
];

export default function GenerateRecipe() {
  const [input, setInput] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [recipe, setRecipe] = useState(null);
  const [hasRecommended, setHasRecommended] = useState(false);

  const [questions, setQuestions] = useState([]);
  const [asking, setAsking] = useState(false);

  const [pendingRecipe, setPendingRecipe] = useState(null);
  const [optionalOptions, setOptionalOptions] = useState([]);
  const [optionsLoadingFor, setOptionsLoadingFor] = useState(null);

  const [error, setError] = useState("");

  const [servings, setServings] = useState(2);

  const { user } = useAuth();
  const [saved, setSaved] = useState(false);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(LOADING_MESSAGES[0]);

  useEffect(() => {
    if (!generateLoading) return;

    let index = 0;

    const interval = setInterval(() => {
      index = (index + 1) % LOADING_MESSAGES.length;
      setLoadingMessage(LOADING_MESSAGES[index]);
    }, 1800);

    return () => clearInterval(interval);
  }, [generateLoading]);

  const resetQuestions = () => {
    setQuestions([]);
    setAsking(false);
  };

  const resetOptional = () => {
    setPendingRecipe(null);
    setOptionalOptions([]);
    setOptionsLoadingFor(null);
  };

  const addIngredient = () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    const isDuplicate = ingredients.some(
      (item) => item.toLowerCase() === trimmed.toLowerCase(),
    );
    if (isDuplicate) return;

    setIngredients((prev) => [...prev, trimmed]);
    setInput("");
    resetQuestions();
    resetOptional();
  };

  const removeIngredient = (index) => {
    setIngredients((prev) => prev.filter((_, i) => i !== index));
    resetQuestions();
    resetOptional();
  };

  const clearIngredients = () => {
    setIngredients([]);
    setRecommendations([]);
    setRecipe(null);
    setHasRecommended(false);
    setError("");
    resetQuestions();
    resetOptional();
  };

  // Fetch the final top 3, optionally refined by the user's answers
  const fetchRecommendations = async (answers = []) => {
    try {
      setRecommendLoading(true);
      setError("");

      const hasAnswers = answers.some((a) => a.answer !== "skip");

      const data = hasAnswers
        ? await recommendRefined({ ingredients, servings, answers })
        : await recommendRecipes({ ingredients, servings });

      setRecommendations(data.recommendations || []);
      setHasRecommended(true);
      setRecipe(null);
      setSaved(false);
    } catch (err) {
      console.error(err);

      setError(err.response?.data?.detail || "Failed to get recommendations.");
    } finally {
      setRecommendLoading(false);
    }
  };

  const handleRecommend = async () => {
    if (!servings || servings < 1) {
      setError("Minimum serving is 1.");
      setServings(1);
      return;
    }

    if (servings > 10) {
      setError("Maximum serving is 10.");
      setServings(10);
      return;
    }

    if (ingredients.length === 0) {
      setError("Please add at least one ingredient.");
      return;
    }

    setError("");
    setRecommendations([]);
    setHasRecommended(false);
    setRecipe(null);
    resetQuestions();
    resetOptional();

    try {
      setRecommendLoading(true);

      const data = await getRecipeQuestions({ ingredients, servings });
      const fetched = data.questions || [];

      if (fetched.length === 0) {
        // Nothing to ask, go straight to recommendations
        setRecommendLoading(false);
        await fetchRecommendations([]);
        return;
      }

      setQuestions(fetched);
      setAsking(true);
      setRecommendLoading(false);
    } catch (err) {
      console.error(err);
      // If the questions endpoint fails, fall back to the normal flow
      setRecommendLoading(false);
      await fetchRecommendations([]);
    }
  };

  const handleQuestionsFinished = async (answers) => {
    resetQuestions();
    await fetchRecommendations(answers);
  };

  const handleSkipAllQuestions = async () => {
    resetQuestions();
    await fetchRecommendations([]);
  };

  // Generate the final recipe with the chosen optional ingredients
  const generateRecipe = async (recipeName, selected = [], excluded = []) => {
    try {
      resetOptional();
      setGenerateLoading(true);
      setLoadingMessage(LOADING_MESSAGES[0]);
      setError("");

      const data = await generateSelectedRecipe({
        recipe_name: recipeName,
        ingredients,
        servings,
        selected_optional: selected,
        excluded_optional: excluded,
      });

      const normalized = {
        ...data,
        title: data.title || data.recipe_name,

        ingredients:
          typeof data.ingredients === "string"
            ? JSON.parse(data.ingredients)
            : data.ingredients,

        instructions:
          typeof data.instructions === "string"
            ? JSON.parse(data.instructions)
            : data.instructions,

        cooking_tips:
          typeof data.cooking_tips === "string"
            ? JSON.parse(data.cooking_tips)
            : data.cooking_tips,
      };

      setRecipe(normalized);
      setSaved(false);
    } catch (err) {
      console.error(err);

      setError(err.response?.data?.detail || "Failed to generate recipe.");
    } finally {
      setGenerateLoading(false);
    }
  };

  // Clicking a recommended recipe: check for optional ingredients first
  const handleSelectRecipe = async (recipeName) => {
    setError("");
    setRecipe(null);
    setPendingRecipe(null);
    setOptionalOptions([]);

    try {
      setOptionsLoadingFor(recipeName);

      const data = await getOptionalIngredients({
        recipe_name: recipeName,
        ingredients,
      });

      const options = data.optional_ingredients || [];

      setOptionsLoadingFor(null);

      if (options.length === 0) {
        // Nothing optional, generate right away
        await generateRecipe(recipeName);
        return;
      }

      setPendingRecipe(recipeName);
      setOptionalOptions(options);
    } catch (err) {
      console.error(err);
      // If the options endpoint fails, fall back to the normal flow
      setOptionsLoadingFor(null);
      await generateRecipe(recipeName);
    }
  };

  const handleOptionalConfirmed = async (selected, excluded) => {
    await generateRecipe(pendingRecipe, selected, excluded);
  };

  const handleAddFavorite = async () => {
    if (!user) {
      setError("Please log in to save recipes to your favorites.");
      return;
    }

    if (!recipe?.id) {
      setError("This recipe must be saved before it can be favorited.");
      return;
    }

    try {
      setError("");
      await addFavorite(recipe.id);
      setSaved(true);
    } catch (err) {
      if (err.response?.status === 400) {
        setSaved(true);
      } else {
        setError("Failed to save favorite.");
      }
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
      <div className="mx-auto max-w-6xl">
        <h1 className="font-display text-3xl text-ink">Generate Recipe</h1>
        <p className="mt-2 max-w-xl text-sm text-ink/60">
          Enter the ingredients you have on hand, we'll use them to generate a
          recipe tailored to your kitchen.
        </p>

        <div className="mt-8 grid gap-6 lg:grid-cols-2 lg:items-start">
          {/* ---------------- Left column: input + recommendations ---------------- */}
          <div className="card">
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
              <div className="mt-4 flex items-center justify-between gap-3">
                <div className="flex flex-wrap gap-2">
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
                        className="text-ink/40 transition-colors hover:text-red-600"
                      >
                        <X size={14} />
                      </button>
                    </span>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={clearIngredients}
                  className="flex shrink-0 items-center gap-1.5 rounded-md border border-clay px-3 py-1.5 text-xs font-medium text-ink/60 transition-colors hover:border-red-300 hover:text-red-600"
                >
                  <Trash2 size={14} />
                  Clear
                </button>
              </div>
            )}

            <div className="mt-6">
              <label className="form-label">Servings</label>

              <input
                type="number"
                min="1"
                max="10"
                value={servings}
                onChange={(e) => {
                  const value = e.target.value;

                  if (value === "") {
                    setServings("");
                    return;
                  }

                  const number = Number(value);

                  if (number < 1) {
                    setServings(1);
                    setError("Minimum serving is 1.");
                    return;
                  }

                  if (number > 10) {
                    setServings(10);
                    return;
                  }

                  setServings(number);
                  setError("");
                }}
                className="input-field mt-2 appearance-none"
              />
            </div>

            <button
              type="button"
              onClick={handleRecommend}
              disabled={recommendLoading || asking}
              className="btn-primary mt-6 w-full sm:w-auto"
            >
              {recommendLoading ? "Finding recipes..." : "Get Recommendations"}
            </button>

            {asking && (
              <QuestionFlow
                questions={questions}
                onFinish={handleQuestionsFinished}
                onSkipAll={handleSkipAllQuestions}
              />
            )}

            {recommendations.length > 0 && (
              <div className="mt-8">
                <h2 className="font-display text-2xl">
                  Recommended Nepali Recipes
                </h2>

                <div className="mt-4 space-y-3">
                  {recommendations.map((item, index) => (
                    <div key={index}>
                      <button
                        type="button"
                        onClick={() => handleSelectRecipe(item.recipe_name)}
                        disabled={optionsLoadingFor !== null || generateLoading}
                        className="w-full rounded-lg border border-clay bg-paper p-4 text-left hover:border-basil transition-colors disabled:opacity-60"
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-semibold text-lg">
                            {item.recipe_name}
                          </div>

                          <div className="text-sm font-medium text-basil">
                            Match Score:{" "}
                            {(item.similarity_score * 100).toFixed(2)}%
                          </div>
                        </div>
                      </button>

                      {optionsLoadingFor === item.recipe_name && (
                        <div className="mt-3 rounded-lg border border-clay bg-white px-5 py-4 text-center">
                          <p className="text-sm font-medium text-basil">
                            Checking optional ingredients...
                          </p>
                        </div>
                      )}

                      {pendingRecipe === item.recipe_name &&
                        optionalOptions.length > 0 && (
                          <OptionalIngredients
                            key={pendingRecipe}
                            recipeName={pendingRecipe}
                            options={optionalOptions}
                            onConfirm={handleOptionalConfirmed}
                            onCancel={resetOptional}
                          />
                        )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {hasRecommended &&
              recommendations.length === 0 &&
              !recommendLoading && (
                <div className="mt-8 rounded-lg border border-clay bg-paper px-5 py-6 text-center">
                  <p className="font-medium text-ink">
                    No matching recipes found.
                  </p>
                </div>
              )}

            {error && <p className="mt-4 text-red-600">{error}</p>}
          </div>

          {/* ---------------- Right column: generated recipe ---------------- */}
          <div className="space-y-6">
            {generateLoading && (
              <div className="rounded-lg border border-clay bg-white px-5 py-6 text-center">
                <div className="mx-auto mb-3 flex justify-center gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-basil [animation-delay:-0.3s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-basil [animation-delay:-0.15s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-basil" />
                </div>

                <p className="font-medium text-basil">{loadingMessage}</p>

                <p className="mt-1 text-xs text-ink/50">
                  Creating something delicious from what you have.
                </p>
              </div>
            )}

            {recipe && (
              <>
                {recipe.analysis && (
                  <div className="card space-y-6">
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
                        <h3 className="font-semibold">Corrections</h3>

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
                        <h3 className="font-semibold">Ignored Ingredients</h3>

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

                <div className="card">
                  <h2 className="font-display text-2xl">{recipe.title}</h2>

                  <p className="mt-2 text-sm text-ink/60">{recipe.cuisine}</p>

                  <div className="mt-6">
                    <h3 className="font-semibold">Ingredients</h3>

                    {recipe.ingredients.map((ing, i) => (
                      <p key={i}>
                        • {ing.quantity} {ing.name}
                      </p>
                    ))}
                  </div>

                  <div className="mt-6">
                    <h3 className="font-semibold">Instructions</h3>

                    {recipe.instructions.map((step, i) => (
                      <p key={i}>
                        {i + 1}. {step}
                      </p>
                    ))}
                  </div>

                  <div className="mt-6">
                    <h3 className="font-semibold">Cooking Tips</h3>

                    <ul className="list-disc list-inside">
                      {recipe.cooking_tips.map((tip, i) => (
                        <li key={i}>{tip}</li>
                      ))}
                    </ul>
                  </div>

                  <button
                    type="button"
                    onClick={handleAddFavorite}
                    disabled={saved}
                    className={`mt-6 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                      saved
                        ? "bg-category-protein/10 text-category-protein border border-category-protein/30 cursor-default"
                        : "bg-basil text-white hover:bg-basil-dark"
                    }`}
                  >
                    {saved ? "Added to Favorites" : "Add to Favorites"}
                  </button>
                </div>
              </>
            )}

            {!generateLoading && !recipe && (
              <div className="hidden rounded-lg border border-dashed border-clay px-6 py-16 text-center lg:block">
                <p className="text-sm text-ink/50">
                  Your generated recipe will appear here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}