import Link from "next/link";

const FEATURES = [
  { free: true, label: "Current NIL score" },
  { free: true, label: "Leaderboards & search" },
  { free: true, label: "Score history (4 weeks)" },
  { free: false, label: "Full score history & trend chart" },
  { free: false, label: "Score breakdown by component" },
  { free: false, label: "Price alerts (score moves 10%+)" },
  { free: false, label: "Similar athlete comparisons" },
  { free: false, label: "CSV data export" },
];

export default function UpgradePage() {
  return (
    <main style={{ background: "var(--bg)", minHeight: "100vh" }}>
      <div className="max-w-lg mx-auto px-4 py-16">

        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-3" style={{ color: "var(--text-primary)" }}>
            NIL Institute Pro
          </h1>
          <p className="text-base" style={{ color: "var(--text-secondary)" }}>
            The full picture on every athlete&apos;s NIL value.
          </p>
        </div>

        {/* Pricing cards */}
        <div className="grid grid-cols-2 gap-4 mb-10">
          {/* Free */}
          <div
            className="rounded-xl p-5"
            style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
          >
            <div
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: "var(--text-secondary)" }}
            >
              Free
            </div>
            <div className="text-2xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>
              $0
            </div>
            <div className="text-xs mb-4" style={{ color: "var(--text-muted)" }}>
              forever
            </div>
            <div className="space-y-2">
              {FEATURES.map((f) => (
                <div
                  key={f.label}
                  className="flex items-center gap-2 text-xs"
                  style={{ color: f.free ? "var(--text-primary)" : "var(--text-muted)" }}
                >
                  <span>{f.free ? "✓" : "–"}</span>
                  <span>{f.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Pro */}
          <div
            className="rounded-xl p-5"
            style={{ background: "var(--surface)", border: "1px solid var(--green)" }}
          >
            <div
              className="text-xs font-semibold uppercase tracking-widest mb-3"
              style={{ color: "var(--green)" }}
            >
              Pro
            </div>
            <div className="text-2xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>
              $9.99
            </div>
            <div className="text-xs mb-4" style={{ color: "var(--text-muted)" }}>
              per month
            </div>
            <div className="space-y-2">
              {FEATURES.map((f) => (
                <div
                  key={f.label}
                  className="flex items-center gap-2 text-xs"
                  style={{ color: "var(--text-primary)" }}
                >
                  <span style={{ color: "var(--green)" }}>✓</span>
                  <span>{f.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <button
            className="w-full py-3 rounded-full text-sm font-semibold mb-3 transition-colors"
            style={{ background: "var(--accent)", color: "var(--bg)" }}
          >
            Get Pro — $9.99/mo
          </button>
          <Link href="/" className="text-xs" style={{ color: "var(--text-muted)" }}>
            Continue with Free
          </Link>
        </div>

      </div>
    </main>
  );
}
