const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AthleteRow {
  id: string;
  name: string;
  school: string;
  conference?: string;
  sport: string;
  position?: string;
  current_score: number;
  score_change_pct: number;
}

export interface AthleteDetail extends AthleteRow {
  year?: string;
  components: {
    social_followers: number | null;
    athletic: number | null;
    school: number | null;
    position: number | null;
  };
  history: { date: string; score: number }[];
}

export async function getLeaderboard(sport = "football", limit = 100): Promise<{ athletes: AthleteRow[] }> {
  const res = await fetch(`${API_URL}/api/leaderboard?sport=${sport}&limit=${limit}`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) return { athletes: [] };
  return res.json();
}

export async function getAthlete(athleteId: string): Promise<AthleteDetail> {
  const res = await fetch(`${API_URL}/api/athletes/${athleteId}`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error("Athlete not found");
  return res.json();
}

export async function searchAthletes(query: string): Promise<{ athletes: AthleteRow[] }> {
  const res = await fetch(`${API_URL}/api/athletes?q=${encodeURIComponent(query)}`);
  if (!res.ok) return { athletes: [] };
  return res.json();
}

export function formatNIL(score: number): string {
  if (!isFinite(score) || score <= 0) return "$0";
  if (score >= 1_000_000) return `$${(score / 1_000_000).toFixed(2)}M`;
  if (score >= 1_000 && score < 1_000_000) return `$${Math.floor(score / 1_000)}K`;
  return `$${Math.round(score).toLocaleString()}`;
}
