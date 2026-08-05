import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-display text-3xl text-ink">
              Welcome, {user?.full_name}
            </h1>
            <p className="mt-1 text-sm text-ink/60">{user?.email}</p>
          </div>
          <button onClick={logout} className="btn-primary">
            Log out
          </button>
        </div>

        <div className="card mt-8">
          <p className="text-sm text-ink/60">
            Recipe generation, history, and favorites will live here once those modules are ready.
          </p>
        </div>
      </div>
    </div>
  );
}