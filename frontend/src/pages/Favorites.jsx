export default function Favorites() {
  return (
    <div className="min-h-screen bg-paper px-4 py-10">
      <div className="mx-auto max-w-3xl">
        <h1 className="font-display text-3xl text-ink">Favorites</h1>
        <p className="mt-2 text-sm text-ink/60">
          Recipes you save will appear here for quick access anytime.
        </p>

        <p className="mt-8 text-sm text-ink/60">
          You haven't saved any favorite recipes yet.
        </p>
      </div>
    </div>
  );
}
