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
  { label: "Oil & Fat", key: "oilfat" },
];

export default function AuthLayout({ children }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      {/* Brand panel — hidden on mobile, shown from lg breakpoint up */}
      <div className="hidden lg:flex flex-col justify-between bg-basil px-16 py-12 text-white">
        <span className="font-display text-2xl">Recipe Generator</span>

        <div>
          <h2 className="font-display text-4xl leading-tight">
            Turn what's in your kitchen into your next meal.
          </h2>
          <p className="mt-4 max-w-sm text-sm text-white/70">
            Every ingredient you list gets classified, scored for compatibility, and
            ranked before a single recipe is generated.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map(({ label, key }) => (
            <span
              key={key}
              className="inline-flex items-center gap-1.5 rounded-full border border-white/20 px-3 py-1 text-xs"
            >
              <span className={`h-1.5 w-1.5 rounded-full ${CATEGORY_DOT[key]}`} />
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* Form panel */}
      <div className="flex min-h-screen items-center justify-center bg-paper px-6 py-12 sm:px-10">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}