"use client";

import Link from "next/link";
import { ScoreTicker } from "@/components/ui/ScoreTicker";
import type { AthleteRow } from "@/lib/api";

interface AthleteRowProps {
  rank: number;
  athlete: AthleteRow;
}

export function AthleteRow({ rank, athlete }: AthleteRowProps) {
  return (
    <Link href={`/athletes/${athlete.id}`} className="block">
      <div
        className="flex items-center gap-4 px-5 py-3.5 transition-colors cursor-pointer"
        style={{
          borderBottom: "1px solid var(--border)",
        }}
        onMouseEnter={(e) => {
          (e.currentTarget as HTMLDivElement).style.background = "var(--surface)";
        }}
        onMouseLeave={(e) => {
          (e.currentTarget as HTMLDivElement).style.background = "transparent";
        }}
      >
        {/* Rank */}
        <span
          className="text-sm w-7 text-right tabular-nums shrink-0"
          style={{ color: "var(--text-muted)" }}
        >
          {rank}
        </span>

        {/* Athlete info */}
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm truncate" style={{ color: "var(--text-primary)" }}>
            {athlete.name}
          </div>
          <div className="text-xs truncate mt-0.5" style={{ color: "var(--text-secondary)" }}>
            {athlete.school}
            {athlete.position ? ` · ${athlete.position}` : ""}
            {athlete.conference ? ` · ${athlete.conference}` : ""}
          </div>
        </div>

        {/* Score ticker */}
        <ScoreTicker score={athlete.current_score} changePct={athlete.score_change_pct} size="sm" />
      </div>
    </Link>
  );
}
