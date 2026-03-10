import Link from "next/link";

export function Navbar() {
  return (
    <nav
      style={{
        background: "var(--bg)",
        borderBottom: "1px solid var(--border)",
      }}
      className="sticky top-0 z-50 px-6 py-4"
    >
      <div className="max-w-3xl mx-auto flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-lg font-bold tracking-tight text-[var(--text-primary)]">
            NIL{" "}
            <span className="text-[var(--green)]">Institute</span>
          </span>
        </Link>

        <div className="flex items-center gap-5">
          <Link
            href="/leaderboard"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            Leaderboard
          </Link>
          <Link
            href="/search"
            className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            Search
          </Link>
          <Link
            href="/upgrade"
            className="text-xs font-semibold px-3 py-1.5 rounded-full bg-[var(--accent)] text-black hover:bg-gray-200 transition-colors"
          >
            Go Pro
          </Link>
        </div>
      </div>
    </nav>
  );
}
