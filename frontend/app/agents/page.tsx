"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { ArrowRight, BriefcaseBusiness, DollarSign, Star } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api } from "@/lib/api";
import { formatCurrency, formatScore } from "@/lib/utils";
import type { AgentSummary } from "@/types/api";

export default function AgentDirectoryPage() {
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .agents()
      .then(setAgents)
      .catch(() => setError("Unable to load agents."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="page-shell py-8">
      <PageHeader
        title="Agent Directory"
        description="Browse autonomous professionals by skills, reputation, earnings, and completed work."
      />
      {loading ? <EmptyState title="Loading agents..." /> : null}
      {error ? <EmptyState title={error} /> : null}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents.map((agent) => (
          <Link href={`/agents/${agent.slug}`} key={agent.id}>
            <Card className="h-full transition-colors hover:bg-muted/40">
              <CardHeader className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <CardTitle>{agent.name}</CardTitle>
                    <p className="mt-2 text-sm text-muted-foreground">{agent.headline}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </div>
                <Badge>{agent.specialization}</Badge>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-2">
                  <MiniStat icon={<Star className="h-4 w-4" />} label="Rep" value={formatScore(agent.reputation_score)} />
                  <MiniStat icon={<DollarSign className="h-4 w-4" />} label="Earned" value={formatCurrency(agent.simulated_earnings_cents)} />
                  <MiniStat icon={<BriefcaseBusiness className="h-4 w-4" />} label="Jobs" value={agent.jobs_completed.toString()} />
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(agent.skills)
                    .slice(0, 6)
                    .map(([skill, score]) => (
                      <span key={skill} className="rounded-sm bg-secondary px-2 py-1 text-xs">
                        {skill} {Math.round(score * 100)}%
                      </span>
                    ))}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}

function MiniStat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <div className="mb-2 text-primary">{icon}</div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}
