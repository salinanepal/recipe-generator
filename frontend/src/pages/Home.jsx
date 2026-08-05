import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const CATEGORY_DOT = {
  protein: "bg-category-protein",
  vegetable: "bg-category-vegetable",
  grain: "bg-category-grain",
  dairy: "bg-category-dairy",
  spice: "bg-category-spice",
  fruit: "bg-category-fruit",
  oilfat: "bg-category-oilfat",
};

const CATEGORIES = [
  { label: "Protein", key: "protein" },
  { label: "Vegetable", key: "vegetable" },
  { label: "Grain", key: "grain" },
  { label: "Dairy", key: "dairy" },
  { label: "Spice", key: "spice" },
  { label: "Fruit", key: "fruit" },
  { label: "Oil & fat", key: "oilfat" },
];

const STEPS = [
  { title: "List what you have", body: "Type in whatever's sitting in your kitchen right now." },
  { title: "We analyze it", body: "Ingredients are classified, scored for compatibility, and ranked by our own algorithm." },
  { title: "Get a recipe", body: "A recipe is generated from that analysis — tailored to what you actually have." },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <div>
      {/* hero */}
      <section className="mx-auto max-w-3xl px-4 py-16 text-center sm:px-6 sm:py-24">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-clay bg-white px-3 py-1 text-xs text-ink/60">
          No account needed to generate a recipe
        </span>

        <h1 className="mt-5 font-display text-4xl leading-tight text-ink sm:text-5xl">
          Turn what's in your kitchen into your next meal.
        </h1>

        <p className="mx-auto mt-4 max-w-xl text-ink/60">
          List your ingredients and get a recipe built around what you actually have —
          analyzed by our own compatibility algorithm before Gemini writes it up.
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
              Sign up to save favorites
            </Link>
          )}
        </div>
      </section>

      {/* how it works */}
      <section className="border-t border-clay bg-white">
        <div className="mx-auto max-w-4xl px-4 py-14 sm:px-6">
          <h2 className="text-center font-display text-2xl text-ink">How it works</h2>

          <div className="mt-10 grid gap-8 sm:grid-cols-3">
            {STEPS.map((step, i) => (
              <div key={step.title}>
                <span className="font-display text-3xl text-basil">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className="mt-2 font-display text-lg text-ink">{step.title}</h3>
                <p className="mt-1 text-sm text-ink/60">{step.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* categories */}
      <section className="mx-auto max-w-3xl px-4 py-14 text-center sm:px-6">
        <h2 className="font-display text-2xl text-ink">Every ingredient, classified</h2>
        <p className="mx-auto mt-2 max-w-md text-sm text-ink/60">
          Our algorithm sorts what you enter into categories before scoring how well they work together.
        </p>

        <div className="mt-6 flex flex-wrap justify-center gap-2">
          {CATEGORIES.map(({ label, key }) => (
            <span
              key={key}
              className="inline-flex items-center gap-1.5 rounded-full border border-clay bg-white px-3 py-1 text-sm text-ink/70"
            >
              <span className={`h-2 w-2 rounded-full ${CATEGORY_DOT[key]}`} />
              {label}
            </span>
          ))}
        </div>
      </section>
    </div>
  );
}