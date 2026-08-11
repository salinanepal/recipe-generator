import { Link } from "react-router-dom";
import { ChefHat } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-clay bg-white">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-center gap-2">
            <ChefHat size={18} className="text-basil" />
            <span className="font-display text-base text-ink">Nepali Recipe Generator</span>
          </div>

          <nav className="flex gap-5 text-sm text-ink/60">
            <Link to="/" className="hover:text-ink">Home</Link>
            <Link to="/generate" className="hover:text-ink">Generate recipe</Link>
            <Link to="/login" className="hover:text-ink">Log in</Link>
          </nav>
        </div>

        <p className="mt-6 text-center text-xs text-ink/40 sm:text-left">
          Final-year project — ingredients analyzed by a custom algorithm, recipes generated via Google Gemini.
        </p>
      </div>
    </footer>
  );
}