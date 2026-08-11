import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  ChefHat,
  Menu,
  X,
  History,
  Heart,
  LogOut,
} from "lucide-react";
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
    <header className="relative border-b border-clay bg-paper">
      <div className="mx-auto flex h-[57px] max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* logo */}
        <Link
          to="/"
          className="flex items-center gap-2"
          onClick={() => setOpen(false)}
        >
          <ChefHat size={22} className="text-basil" />
          <span className="font-display text-xl text-ink">
            Nepali Recipe Generator
          </span>
        </Link>

        {/* desktop nav */}
        <nav className="hidden items-center gap-6 md:flex">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `text-sm transition-colors ${
                  isActive
                    ? "font-medium text-ink"
                    : "text-ink/60 hover:text-ink"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}

          {user ? (
            <>
              <NavLink
                to="/history"
                className={({ isActive }) =>
                  `flex items-center gap-1.5 text-sm transition-colors ${
                    isActive
                      ? "font-medium text-ink"
                      : "text-ink/60 hover:text-ink"
                  }`
                }
              >
                <History size={16} />
                History
              </NavLink>

              <NavLink
                to="/favorites"
                className={({ isActive }) =>
                  `flex items-center gap-1.5 text-sm transition-colors ${
                    isActive
                      ? "font-medium text-ink"
                      : "text-ink/60 hover:text-ink"
                  }`
                }
              >
                <Heart size={16} />
                Favorites
              </NavLink>

              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-sm text-ink/60 transition-colors hover:text-red-600"
              >
                <LogOut size={16} />
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink
                to="/login"
                className={({ isActive }) =>
                  `text-sm transition-colors ${
                    isActive
                      ? "font-medium text-ink"
                      : "text-ink/60 hover:text-ink"
                  }`
                }
              >
                Log in
              </NavLink>

              <NavLink
                to="/register"
                className={({ isActive }) =>
                  `btn-primary ${
                    isActive ? "ring-2 ring-basil/30" : ""
                  }`
                }
              >
                Sign up
              </NavLink>
            </>
          )}
        </nav>

        {/* mobile toggle */}
        <button
          onClick={() => setOpen((v) => !v)}
          className="text-ink md:hidden"
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
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                onClick={() => setOpen(false)}
                className={({ isActive }) =>
                  `rounded-md px-2 py-2 text-sm transition-colors ${
                    isActive
                      ? "bg-basil-light font-medium text-ink"
                      : "text-ink/70 hover:bg-basil-light hover:text-ink"
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}

            {user ? (
              <>
                <NavLink
                  to="/history"
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-md px-2 py-2 text-sm transition-colors ${
                      isActive
                        ? "bg-basil-light font-medium text-ink"
                        : "text-ink/70 hover:bg-basil-light hover:text-ink"
                    }`
                  }
                >
                  History
                </NavLink>

                <NavLink
                  to="/favorites"
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-md px-2 py-2 text-sm transition-colors ${
                      isActive
                        ? "bg-basil-light font-medium text-ink"
                        : "text-ink/70 hover:bg-basil-light hover:text-ink"
                    }`
                  }
                >
                  Favorites
                </NavLink>

                <button
                  onClick={handleLogout}
                  className="rounded-md px-2 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <NavLink
                  to="/login"
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `rounded-md px-2 py-2 text-sm transition-colors ${
                      isActive
                        ? "bg-basil-light font-medium text-ink"
                        : "text-ink/70 hover:bg-basil-light hover:text-ink"
                    }`
                  }
                >
                  Log in
                </NavLink>

                <NavLink
                  to="/register"
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `btn-primary mt-1 text-center ${
                      isActive ? "ring-2 ring-basil/30" : ""
                    }`
                  }
                >
                  Sign up
                </NavLink>
              </>
            )}
          </nav>
        </>
      )}
    </header>
  );
}
