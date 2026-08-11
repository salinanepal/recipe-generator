import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const STEPS = [
  {
    title: "Enter your ingredients",
    body: "Type in the ingredients you currently have and choose your serving size.",
  },
  {
    title: "Get recommendations",
    body: "Our system compares your ingredients with Nepali recipes and finds the top three matches.",
  },
  {
    title: "Get your recipe",
    body: "Select a recommended recipe and receive a complete recipe based on your ingredients and servings.",
  },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="bg-paper">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-4 py-20 text-center sm:px-6">
        <p className="text-sm font-medium text-basil">
          No account needed to generate a recipe
        </p>

        <h1 className="mt-5 font-display text-4xl leading-tight text-ink sm:text-5xl">
          Turn what's in your kitchen into your next meal.
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-ink/60">
          Enter your ingredients and get relevant Nepali recipe
          recommendations based on what you have available.
        </p>

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <Link to="/generate" className="btn-primary">
            Generate a recipe
          </Link>

          {!user && (
            <Link
              to="/register"
              className="rounded-md border border-clay px-4 py-2 text-sm font-medium text-ink hover:border-basil"
            >
              Create an account
            </Link>
          )}
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-clay bg-white">
        <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6">
          <h2 className="text-center font-display text-2xl text-ink">
            How it works
          </h2>

          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            {STEPS.map((step, i) => (
              <div key={step.title}>
                <span className="font-display text-3xl text-basil">
                  {String(i + 1).padStart(2, "0")}
                </span>

                <h3 className="mt-2 font-display text-lg text-ink">
                  {step.title}
                </h3>

                <p className="mt-1 text-sm text-ink/60">
                  {step.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Recommendation information */}
      <section className="mx-auto max-w-3xl px-4 py-14 text-center sm:px-6">
        <h2 className="font-display text-2xl text-ink">
          Discover Nepali recipes
        </h2>

        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-ink/60">
          Our recommendation system uses ingredient similarity to find
          Nepali recipes that best match the ingredients you have available.
        </p>
      </section>
    </div>
  );
}