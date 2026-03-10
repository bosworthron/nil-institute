import Link from "next/link";
import { getLeaderboard } from "@/lib/api";
import { AthleteRow } from "@/components/athletes/AthleteRow";

export default async function Home() {
  const [football, basketball] = await Promise.all([
    getLeaderboard("football", 25),
    getLeaderboard("basketball", 25),
  ]);

  return (
    <main style={{ background: "var(--bg)", minHeight: "100vh" }}>
      <div className="max-w-2xl mx-auto px-4 py-10">

        {/* Hero */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold tracking-tight mb-2" style={{ color: "var(--text-primary)" }}>
            NIL Institute
          </h1>
          <p className="text-base" style={{ color: "var(--text-secondary)" }}>
            Predicted NIL valuations for college athletes — updated every Monday.
          </p>
        </div>

        {/* Stats bar */}
        <div
          className="grid grid-cols-3 gap-px mb-8 rounded-xl overflow-hidden"
          style={{ background: "var(--border)" }}
        >
          {[
            { label: "Athletes Tracked", value: "4,500+" },
            { label: "Market Size", value: "$1.67B" },
            { label: "Updated", value: "Weekly" },
          ].map((stat) => (
            <div
              key={stat.label}
              className="px-4 py-3 text-center"
              style={{ background: "var(--surface)" }}
            >
              <div className="text-lg font-bold" style={{ color: "var(--text-primary)" }}>
                {stat.value}
              </div>
              <div className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        {/* Football leaderboard */}
        <section className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
              Top Football
            </h2>
            <Link href="/leaderboard?sport=football" className="text-xs hover:underline" style={{ color: "var(--green)" }}>
              View all →
            </Link>
          </div>
          <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--border)" }}>
            {football.athletes.length === 0 ? (
              <EmptyState sport="football" />
            ) : (
              football.athletes.map((athlete, i) => (
                <AthleteRow key={athlete.id} rank={i + 1} athlete={athlete} />
              ))
            )}
          </div>
        </section>

        {/* Basketball leaderboard */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-xs font-semibold uppercase tracking-widest" style={{ color: "var(--text-secondary)" }}>
              Top Basketball
            </h2>
            <Link href="/leaderboard?sport=basketball" className="text-xs hover:underline" style={{ color: "var(--green)" }}>
              View all →
            </Link>
          </div>
          <div className="rounded-xl overflow-hidden" style={{ border: "1px solid var(--border)" }}>
            {basketball.athletes.length === 0 ? (
              <EmptyState sport="basketball" />
            ) : (
              basketball.athletes.map((athlete, i) => (
                <AthleteRow key={athlete.id} rank={i + 1} athlete={athlete} />
              ))
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

function EmptyState({ sport }: { sport: string }) {
  return (
    <div className="px-5 py-10 text-center">
      <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
        {sport.charAt(0).toUpperCase() + sport.slice(1)} valuations loading soon.
      </p>
      <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
        Pipeline runs every Monday at 3am EST.
      </p>
    </div>
  );
}
