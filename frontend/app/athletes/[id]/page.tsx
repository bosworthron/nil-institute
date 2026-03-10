import { getAthlete, formatNIL } from "@/lib/api";
import { ScoreTicker } from "@/components/ui/ScoreTicker";
import { ScoreChart } from "@/components/athletes/ScoreChart";
import { notFound } from "next/navigation";
import Link from "next/link";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function AthletePage({ params }: PageProps) {
  const { id } = await params;

  let athlete;
  try {
    athlete = await getAthlete(id);
  } catch {
    notFound();
  }

  const weeklyChange = athlete.score_change_pct;
  const isPositive = weeklyChange >= 0;

  return (
    <main style={{ background: "var(--bg)", minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-4 py-8">

        {/* Back nav */}
        <Link
          href="/leaderboard"
          className="inline-flex items-center gap-1 text-sm mb-6 transition-colors hover:opacity-80"
          style={{ color: "var(--text-secondary)" }}
        >
          ← Leaderboard
        </Link>

        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>
              {athlete.name}
            </h1>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {[athlete.school, athlete.position, athlete.year]
                .filter(Boolean)
                .join(" · ")}
            </p>
            {athlete.conference && (
              <span
                className="inline-block text-xs px-2 py-0.5 rounded-full mt-2 font-medium"
                style={{
                  background: "var(--surface-2)",
                  color: "var(--text-secondary)",
                  border: "1px solid var(--border)",
                }}
              >
                {athlete.conference}
              </span>
            )}
          </div>
          <ScoreTicker
            score={athlete.current_score}
            changePct={athlete.score_change_pct}
            size="lg"
          />
        </div>

        {/* Score history chart */}
        <div
          className="rounded-xl p-5 mb-4"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
              NIL Value History
            </h2>
            <span
              className="text-xs font-medium"
              style={{ color: isPositive ? "var(--green)" : "var(--red)" }}
            >
              {isPositive ? "▲" : "▼"} {Math.abs(weeklyChange).toFixed(2)}% this week
            </span>
          </div>
          <ScoreChart data={athlete.history} />
        </div>

        {/* Score breakdown */}
        <div
          className="rounded-xl p-5 mb-4"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: "var(--text-secondary)" }}>
            Score Breakdown
          </h2>
          <div className="space-y-3">
            {[
              {
                label: "Social Reach",
                weight: "35%",
                value:
                  athlete.components.social_followers != null
                    ? athlete.components.social_followers.toLocaleString() + " followers"
                    : "—",
              },
              {
                label: "Athletic Performance",
                weight: "30%",
                value:
                  athlete.components.athletic != null
                    ? `${athlete.components.athletic.toFixed(0)}/100`
                    : "—",
              },
              {
                label: "School Market",
                weight: "20%",
                value:
                  athlete.components.school != null
                    ? `${athlete.components.school.toFixed(0)}/100`
                    : "—",
              },
              {
                label: "Position Demand",
                weight: "15%",
                value:
                  athlete.components.position != null
                    ? `${athlete.components.position.toFixed(0)}/100`
                    : "—",
              },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between text-sm">
                <div>
                  <span style={{ color: "var(--text-primary)" }}>{item.label}</span>
                  <span className="ml-2 text-xs" style={{ color: "var(--text-muted)" }}>
                    {item.weight}
                  </span>
                </div>
                <span
                  className="tabular-nums font-medium"
                  style={{ color: "var(--text-secondary)" }}
                >
                  {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Similar athletes placeholder */}
        <div
          className="rounded-xl p-5"
          style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
        >
          <h2 className="text-xs font-semibold uppercase tracking-widest mb-2" style={{ color: "var(--text-secondary)" }}>
            Compare Athletes
          </h2>
          <p className="text-sm" style={{ color: "var(--text-muted)" }}>
            Similar athlete comparisons available on{" "}
            <Link href="/upgrade" className="underline" style={{ color: "var(--text-secondary)" }}>
              Pro
            </Link>
            .
          </p>
        </div>

      </div>
    </main>
  );
}
