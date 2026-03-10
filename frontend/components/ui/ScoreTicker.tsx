import { formatNIL } from "@/lib/api";

interface ScoreTickerProps {
  score: number;
  changePct: number;
  size?: "sm" | "md" | "lg";
}

export function ScoreTicker({ score, changePct, size = "sm" }: ScoreTickerProps) {
  const isPositive = changePct >= 0;
  const isNeutral = changePct === 0;
  const arrow = isPositive ? "▲" : "▼";
  const colorClass = isNeutral
    ? "text-[var(--text-secondary)]"
    : isPositive
    ? "text-[var(--green)]"
    : "text-[var(--red)]";

  const sizeClasses = {
    sm: { value: "text-sm font-semibold", change: "text-xs" },
    md: { value: "text-lg font-bold", change: "text-sm" },
    lg: { value: "text-3xl font-bold", change: "text-base" },
  };

  const { value: valueClass, change: changeClass } = sizeClasses[size];

  return (
    <div className="text-right tabular-nums">
      <div className={valueClass}>{formatNIL(score)}</div>
      <div className={`${changeClass} font-medium ${colorClass}`}>
        {!isNeutral && arrow} {Math.abs(changePct).toFixed(2)}%
      </div>
    </div>
  );
}
