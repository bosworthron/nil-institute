import { getAthlete, formatNIL, AthleteDetail } from "@/lib/api";
import { ScoreTicker } from "@/components/ui/ScoreTicker";
import { ScoreChart } from "@/components/athletes/ScoreChart";
import { notFound } from "next/navigation";
import Link from "next/link";

export const dynamic = "force-dynamic";

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

        {/* Score breakdown — Pro gated */}
        <ScoreBreakdown athlete={athlete} />

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

async function ScoreBreakdown({ athlete }: { athlete: AthleteDetail }) {
  const clerkPubKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  const clerkEnabled = clerkPubKey && !clerkPubKey.startsWith("pk_replace");

  let isPro = false;
  if (clerkEnabled) {
    try {
      const { auth } = await import("@clerk/nextjs/server");
      const { sessionClaims } = await auth();
      isPro = (sessionClaims?.metadata as { plan?: string })?.plan === "pro";
    } catch {
      isPro = false;
    }
  }

  const breakdownItems = [
    {
      label: "Social Reach",
      weight: "35%",
      value:
        athlete.components.social_followers != null
          ? `${athlete.components.social_followers.toLocaleString()} followers`
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
  ];

  return (
    <div
      className="rounded-xl p-5 mb-4"
      style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
    >
      <h2
        className="text-xs font-semibold uppercase tracking-widest mb-4"
        style={{ color: "var(--text-secondary)" }}
      >
        Score Breakdown
      </h2>

      {isPro ? (
        <div className="space-y-3">
          {breakdownItems.map((item) => (
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
      ) : (
        <div className="text-center py-4">
          <p className="text-sm mb-1" style={{ color: "var(--text-secondary)" }}>
            See exactly how this score is calculated.
          </p>
          <p className="text-xs mb-4" style={{ color: "var(--text-muted)" }}>
            Social reach, athletic performance, school market, and position demand — all unlocked on Pro.
          </p>
          <Link
            href="/upgrade"
            className="inline-block text-xs font-semibold px-4 py-2 rounded-full transition-colors"
            style={{ background: "var(--accent)", color: "var(--bg)" }}
          >
            Upgrade to Pro — $9.99/mo
          </Link>
        </div>
      )}
    </div>
  );
}
