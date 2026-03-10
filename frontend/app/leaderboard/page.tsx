"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { getLeaderboard, type AthleteRow } from "@/lib/api";
import { AthleteRow as AthleteRowComponent } from "@/components/athletes/AthleteRow";

const SPORTS = [
  { value: "football", label: "Football" },
  { value: "basketball", label: "Basketball" },
];

const CONFERENCES = ["All", "SEC", "Big Ten", "Big 12", "ACC", "Pac-12", "American"];

function LeaderboardContent() {
  const searchParams = useSearchParams();
  const [sport, setSport] = useState(() => searchParams.get("sport") ?? "football");
  const [conference, setConference] = useState("All");
  const [athletes, setAthletes] = useState<AthleteRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getLeaderboard(sport, 100)
      .then((d) => setAthletes(d.athletes))
      .catch(() => setAthletes([]))
      .finally(() => setLoading(false));
  }, [sport]);

  const filtered =
    conference === "All"
      ? athletes
      : athletes.filter((a) => a.conference === conference);

  return (
    <>
      {/* Sport filter */}
      <div className="flex gap-2 mb-4">
        {SPORTS.map((s) => (
          <button
            key={s.value}
            onClick={() => setSport(s.value)}
            aria-pressed={sport === s.value}
            className="px-4 py-1.5 rounded-full text-sm font-medium transition-colors"
            style={{
              background: sport === s.value ? "var(--accent)" : "var(--surface)",
              color: sport === s.value ? "var(--bg)" : "var(--text-secondary)",
              border: "1px solid var(--border)",
            }}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Conference filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {CONFERENCES.map((c) => (
          <button
            key={c}
            onClick={() => setConference(c)}
            aria-pressed={conference === c}
            className="px-3 py-1 rounded-full text-xs font-medium transition-colors"
            style={{
              background: conference === c ? "var(--surface-2)" : "transparent",
              color: conference === c ? "var(--text-primary)" : "var(--text-muted)",
              border: `1px solid ${conference === c ? "var(--border)" : "transparent"}`,
            }}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Results count */}
      <div className="mb-3">
        <span className="text-xs" style={{ color: "var(--text-muted)" }}>
          {loading ? "Loading..." : `${filtered.length} athletes`}
        </span>
      </div>

      {/* Athlete list */}
      <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--border)" }}>
        {loading ? (
          <div className="px-5 py-10 text-center">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Loading valuations...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="px-5 py-10 text-center">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>No athletes found.</p>
          </div>
        ) : (
          filtered.map((athlete, i) => (
            <AthleteRowComponent key={athlete.id} rank={i + 1} athlete={athlete} />
          ))
        )}
      </div>
    </>
  );
}

export default function LeaderboardPage() {
  return (
    <main style={{ background: "var(--bg)", minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-4 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1" style={{ color: "var(--text-primary)" }}>
            Leaderboard
          </h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Top athletes by predicted NIL valuation.
          </p>
        </div>
        <Suspense fallback={
          <div className="px-5 py-10 text-center">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Loading...</p>
          </div>
        }>
          <LeaderboardContent />
        </Suspense>
      </div>
    </main>
  );
}
