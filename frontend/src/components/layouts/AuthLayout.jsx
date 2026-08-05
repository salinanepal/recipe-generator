import { ChefHat, Sparkles } from "lucide-react";

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
  { title: "List what you have", body: "Type in whatever's in your kitchen right now." },
  { title: "We analyze it", body: "Ingredients get classified, scored, and ranked by our own algorithm." },
  { title: "Get a recipe", body: "A tailored recipe is generated from the analysis." },
];

export default function AuthLayout({ children }) {
  return (
    <div className="h-full lg:grid lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden h-full overflow-hidden bg-basil px-14 py-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: "radial-gradient(circle, white 1px, transparent 1px)",
            backgroundSize: "22px 22px",
          }}
        />

        <div className="relative flex items-center gap-2">
          <ChefHat size={22} />
          <span className="font-display text-xl">Recipe Generator</span>
        </div>

        <div className="relative">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-white/10 px-3 py-1 text-xs">
            <Sparkles size={12} /> Powered by our own compatibility algorithm
          </span>

          <h2 className="mt-5 font-display text-[2.5rem] leading-[1.1]">
            Turn what's in your kitchen into your next meal.
          </h2>

          <div className="mt-8 space-y-5 border-l border-white/20 pl-5">
            {STEPS.map((step, i) => (
              <div key={step.title}>
                <p className="text-sm font-medium text-white">
                  <span className="text-white/50">{String(i + 1).padStart(2, "0")}</span>{" "}
                  {step.title}
                </p>
                <p className="mt-0.5 text-sm text-white/60">{step.body}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="relative flex flex-wrap gap-2">
          {CATEGORIES.map(({ label, key }) => (
            <span
              key={key}
              className="inline-flex items-center gap-1.5 rounded-full border border-white/20 px-3 py-1 text-xs text-white/80"
            >
              <span className={`h-1.5 w-1.5 rounded-full ${CATEGORY_DOT[key]}`} />
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* Form panel */}
      <div className="flex h-full min-h-[calc(100vh-57px-137px)] items-center justify-center bg-paper px-6 py-12 sm:px-10 lg:min-h-0">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}