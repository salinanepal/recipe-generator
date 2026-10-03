import { useState } from "react";

export default function OptionalIngredients({
  recipeName,
  options,
  onConfirm,
  onCancel,
}) {
  const [selected, setSelected] = useState([]);

  const toggle = (name) => {
    setSelected((prev) =>
      prev.includes(name)
        ? prev.filter((item) => item !== name)
        : [...prev, name],
    );
  };

  const selectAll = () => setSelected(options.map((o) => o.name));
  const clearAll = () => setSelected([]);

  const confirm = () => {
    const excluded = options
      .map((o) => o.name)
      .filter((name) => !selected.includes(name));

    onConfirm(selected, excluded);
  };

  return (
    <div className="mt-3 rounded-lg border border-clay bg-white px-5 py-5">
      <p className="text-sm text-ink/60">
        Do you want to add any of these ingredients to your{" "}
        <span className="font-medium text-ink">{recipeName}</span>? Anything
        you leave unchecked will not be used.
      </p>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {options.map((option) => {
          const checked = selected.includes(option.name);

          return (
            <label
              key={option.name}
              className={`flex cursor-pointer items-center gap-3 rounded-md border px-3 py-2 text-sm capitalize transition-colors ${
                checked
                  ? "border-basil bg-paper text-ink"
                  : "border-clay bg-paper text-ink/70 hover:border-basil"
              }`}
            >
              <input
                type="checkbox"
                checked={checked}
                onChange={() => toggle(option.name)}
                className="h-4 w-4 accent-basil"
              />
              {option.name}
            </label>
          );
        })}
      </div>

      <div className="mt-3 flex gap-4 text-xs">
        <button
          type="button"
          onClick={selectAll}
          className="text-ink/50 underline hover:text-ink/80"
        >
          Select all
        </button>

        <button
          type="button"
          onClick={clearAll}
          className="text-ink/50 underline hover:text-ink/80"
        >
          Clear
        </button>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={confirm}
          className="rounded-md bg-basil px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-basil-dark"
        >
          Generate Recipe
        </button>

        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-clay px-5 py-2 text-sm font-medium text-ink/70 transition-colors hover:border-basil"
        >
          Back
        </button>
      </div>
    </div>
  );
}