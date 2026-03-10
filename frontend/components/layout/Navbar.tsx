import Link from "next/link";

const clerkPubKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
const clerkEnabled = clerkPubKey && !clerkPubKey.startsWith("pk_replace");

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
        <Link href="/" className="flex items-center gap-2">
          <span className="text-lg font-bold tracking-tight" style={{ color: "var(--text-primary)" }}>
            NIL <span style={{ color: "var(--green)" }}>Institute</span>
          </span>
        </Link>

        <div className="flex items-center gap-5">
          <Link
            href="/leaderboard"
            className="text-sm transition-colors"
            style={{ color: "var(--text-secondary)" }}
          >
            Leaderboard
          </Link>
          <Link
            href="/search"
            className="text-sm transition-colors"
            style={{ color: "var(--text-secondary)" }}
          >
            Search
          </Link>
          {clerkEnabled ? (
            <NavbarAuthButtons />
          ) : (
            <Link
              href="/upgrade"
              className="text-xs font-semibold px-3 py-1.5 rounded-full transition-colors"
              style={{ background: "var(--accent)", color: "var(--bg)" }}
            >
              Go Pro
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

async function NavbarAuthButtons() {
  const { auth } = await import("@clerk/nextjs/server");
  const { userId } = await auth();

  if (userId) {
    const { UserButton } = await import("@clerk/nextjs");
    return <UserButton />;
  }

  const { SignInButton } = await import("@clerk/nextjs");
  return (
    <div className="flex items-center gap-3">
      <SignInButton mode="modal">
        <button className="text-sm" style={{ color: "var(--text-secondary)" }}>
          Sign in
        </button>
      </SignInButton>
      <Link
        href="/upgrade"
        className="text-xs font-semibold px-3 py-1.5 rounded-full transition-colors"
        style={{ background: "var(--accent)", color: "var(--bg)" }}
      >
        Go Pro
      </Link>
    </div>
  );
}
