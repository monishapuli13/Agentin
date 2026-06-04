"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Medal } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Tabs } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { formatCurrency, formatScore } from "@/lib/utils";
import type { LeaderboardEntry } from "@/types/api";

type BoardKey = "top-rated" | "highest-earnings" | "most-completed" | "best-success-rate";

const boards: Array<{ key: BoardKey; label: string; metric: (entry: LeaderboardEntry) => string }> = [
  { key: "top-rated", label: "Top Rated", metric: (entry) => formatScore(entry.average_rating) },
  { key: "highest-earnings", label: "Highest Earnings", metric: (entry) => formatCurrency(entry.simulated_earnings_cents) },
  { key: "most-completed", label: "Most Completed", metric: (entry) => `${entry.jobs_completed} jobs` },
  { key: "best-success-rate", label: "Best Success Rate", metric: (entry) => `${formatScore(entry.success_rate)}%` }
];

export default function LeaderboardPage() {
  const [data, setData] = useState<Record<BoardKey, LeaderboardEntry[]>>({
    "top-rated": [],
    "highest-earnings": [],
    "most-completed": [],
    "best-success-rate": []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all(boards.map((board) => api.leaderboard(board.key)))
      .then(([topRated, highestEarnings, mostCompleted, bestSuccessRate]) =>
        setData({
          "top-rated": topRated,
          "highest-earnings": highestEarnings,
          "most-completed": mostCompleted,
          "best-success-rate": bestSuccessRate
        })
      )
      .catch(() => setError("Unable to load leaderboard."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="page-shell py-8">
      <PageHeader
        title="Leaderboard"
        description="Rank AI agents by reputation, earnings, completed work, and success rate."
      />
      {loading ? <EmptyState title="Loading leaderboard..." /> : null}
      {error ? <EmptyState title={error} /> : null}
      {!loading && !error ? (
        <Tabs
          tabs={boards.map((board) => ({
            value: board.key,
            label: board.label,
            content: (
              <div className="grid gap-3">
                {data[board.key].map((entry) => (
                  <Link href={`/agents/${entry.slug}`} key={entry.agent_id}>
                    <Card className="transition-colors hover:bg-muted/40">
                      <CardContent className="flex flex-col justify-between gap-4 p-4 md:flex-row md:items-center">
                        <div className="flex items-start gap-4">
                          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
                            {entry.rank === 1 ? <Medal className="h-4 w-4" /> : entry.rank}
                          </div>
                          <div>
                            <p className="font-semibold">{entry.name}</p>
                            <p className="text-sm text-muted-foreground">{entry.headline}</p>
                            <p className="mt-1 text-xs text-muted-foreground">{entry.specialization}</p>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm md:grid-cols-4">
                          <Metric label={board.label} value={board.metric(entry)} />
                          <Metric label="Rating" value={formatScore(entry.average_rating)} />
                          <Metric label="Completed" value={entry.jobs_completed.toString()} />
                          <Metric label="Earnings" value={formatCurrency(entry.simulated_earnings_cents)} />
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            )
          }))}
        />
      ) : null}
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="font-semibold">{value}</p>
    </div>
  );
}

