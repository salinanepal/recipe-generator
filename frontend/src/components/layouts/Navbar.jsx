import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ChefHat, Menu, X, History, Heart, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    setOpen(false);
    navigate("/");
  };

  const navLinks = [
    { to: "/", label: "Home" },
    { to: "/generate", label: "Generate recipe" },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-clay bg-paper/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3 sm:px-6">
        <Link
          to="/"
          className="flex items-center gap-2"
          onClick={() => setOpen(false)}
        >
          <ChefHat size={22} className="text-basil" />
          <span className="font-display text-lg text-ink">
            Recipe Generator
          </span>
        </Link>

        {/* desktop nav */}
        <nav className="hidden items-center gap-6 md:flex">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className="text-sm text-ink/70 hover:text-ink"
            >
              {link.label}
            </Link>
          ))}

          {user ? (
            <>
              <Link
                to="/history"
                className="flex items-center gap-1.5 text-sm text-ink/70 hover:text-ink"
              >
                <History size={16} /> History
              </Link>
              <Link
                to="/favorites"
                className="flex items-center gap-1.5 text-sm text-ink/70 hover:text-ink"
              >
                <Heart size={16} /> Favorites
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-sm text-ink/70 hover:text-category-protein"
              >
                <LogOut size={16} /> Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-ink/70 hover:text-ink">
                Log in
              </Link>
              <Link to="/register" className="btn-primary">
                Sign up
              </Link>
            </>
          )}
        </nav>

        {/* mobile toggle */}
        <button
          onClick={() => setOpen((v) => !v)}
          className="md:hidden text-ink"
          aria-label={open ? "Close menu" : "Open menu"}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {open && (
        <>
          {/* backdrop */}

          <div
            className="fixed inset-0 top-[57px] z-30 bg-ink/10 backdrop-blur-sm md:hidden"
            onClick={() => setOpen(false)}
          />

          <nav className="absolute inset-x-0 top-full z-40 flex flex-col gap-1 border-t border-clay bg-paper px-4 py-3 shadow-md md:hidden">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setOpen(false)}
                className="rounded-md px-2 py-2 text-sm text-ink/80 hover:bg-basil-light"
              >
                {link.label}
              </Link>
            ))}

            {user ? (
              <>
                <Link
                  to="/history"
                  onClick={() => setOpen(false)}
                  className="rounded-md px-2 py-2 text-sm text-ink/80 hover:bg-basil-light"
                >
                  History
                </Link>
                <Link
                  to="/favorites"
                  onClick={() => setOpen(false)}
                  className="rounded-md px-2 py-2 text-sm text-ink/80 hover:bg-basil-light"
                >
                  Favorites
                </Link>
                <button
                  onClick={handleLogout}
                  className="rounded-md px-2 py-2 text-left text-sm text-category-protein hover:bg-category-protein/10"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setOpen(false)}
                  className="rounded-md px-2 py-2 text-sm text-ink/80 hover:bg-basil-light"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  onClick={() => setOpen(false)}
                  className="btn-primary mt-1 text-center"
                >
                  Sign up
                </Link>
              </>
            )}
          </nav>
        </>
      )}
    </header>
  );
}
