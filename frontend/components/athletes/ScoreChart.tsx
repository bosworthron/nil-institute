"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { formatNIL } from "@/lib/api";

interface ScoreChartProps {
  data: { date: string; score: number }[];
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function ScoreChart({ data }: ScoreChartProps) {
  if (!data || data.length < 2) {
    return (
      <div
        className="h-28 flex items-center justify-center text-sm"
        style={{ color: "var(--text-muted)" }}
      >
        Not enough history yet — check back after next Monday&apos;s update.
      </div>
    );
  }

  const isPositive = data[data.length - 1].score >= data[0].score;
  const lineColor = isPositive ? "var(--green)" : "var(--red)";

  return (
    <ResponsiveContainer width="100%" height={120}>
      <LineChart data={data} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
        <XAxis
          dataKey="date"
          tickFormatter={formatDate}
          tick={{ fill: "var(--text-muted)", fontSize: 10 }}
          axisLine={false}
          tickLine={false}
          interval="preserveStartEnd"
        />
        <YAxis hide domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
          labelStyle={{ color: "var(--text-secondary)", fontSize: 10 }}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          labelFormatter={(label: any) => formatDate(String(label))}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          formatter={(val: any) => [formatNIL(Number(val)), "NIL Value"]}
          itemStyle={{ color: "var(--text-primary)" }}
        />
        <Line
          type="monotone"
          dataKey="score"
          stroke={lineColor}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, fill: lineColor, stroke: "var(--bg)", strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
