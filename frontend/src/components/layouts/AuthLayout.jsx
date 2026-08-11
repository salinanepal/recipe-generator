const STEPS = [
  {
    title: "Enter your ingredients",
    body: "Tell us what ingredients you currently have and choose your serving size.",
  },
  {
    title: "Find matching recipes",
    body: "Our recommendation system compares your ingredients with Nepali recipes.",
  },
  {
    title: "Generate your recipe",
    body: "Select a recommendation and get a complete recipe generated for you.",
  },
];

export default function AuthLayout({ children }) {
  return (
    <div className="grid min-h-[calc(100vh-57px)] lg:grid-cols-2">
      {/* Information panel */}
      <div className="relative hidden overflow-hidden bg-basil px-10 py-12 text-white lg:flex lg:flex-col lg:justify-between xl:px-16">
        {/* Background pattern */}
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage:
              "radial-gradient(circle, white 1px, transparent 1px)",
            backgroundSize: "22px 22px",
          }}
        />

        <div className="relative">
          <p className="text-sm font-medium uppercase tracking-wider text-white/60">
            Nepali Recipe Generator
          </p>

          <h2 className="mt-5 font-display text-[2.5rem] leading-[1.1]">
            Turn your ingredients into your next Nepali meal.
          </h2>

          <p className="mt-5 max-w-md text-sm leading-6 text-white/65">
            Find recipes that match what you have and generate a complete
            recipe for the dish you choose.
          </p>
        </div>

        <div className="relative space-y-5 border-l border-white/20 pl-5">
          {STEPS.map((step, i) => (
            <div key={step.title}>
              <p className="text-sm font-medium text-white">
                <span className="text-white/50">
                  {String(i + 1).padStart(2, "0")}
                </span>{" "}
                {step.title}
              </p>

              <p className="mt-0.5 text-sm text-white/60">
                {step.body}
              </p>
            </div>
          ))}
        </div>

        <p className="relative text-xs text-white/40">
          Recipe recommendations powered by ingredient similarity.
        </p>
      </div>

      {/* Form panel */}
      <div className="flex min-h-[calc(100vh-57px)] items-center justify-center bg-paper px-6 py-12 sm:px-10">
        <div className="w-full max-w-sm">
          {children}
        </div>
      </div>
    </div>
  );
}