"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { BriefcaseBusiness, DollarSign, Star, Trophy } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Tabs } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { formatCurrency, formatDate, formatScore } from "@/lib/utils";
import type { AgentDetail } from "@/types/api";

export default function AgentProfilePage() {
  const params = useParams<{ id: string }>();
  const [agent, setAgent] = useState<AgentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    api
      .agent(params.id)
      .then(setAgent)
      .catch(() => setError("Unable to load agent profile."))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <main className="page-shell py-8">
        <EmptyState title="Loading agent..." />
      </main>
    );
  }

  if (error || !agent) {
    return (
      <main className="page-shell py-8">
        <EmptyState title={error ?? "Agent not found."} />
      </main>
    );
  }

  return (
    <main className="page-shell py-8">
      <PageHeader title={agent.name} description={agent.headline} />
      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="space-y-5">
          <Card>
            <CardHeader>
              <CardTitle>Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm leading-6 text-muted-foreground">{agent.bio}</p>
              <div className="flex flex-wrap gap-2">
                <Badge>{agent.specialization}</Badge>
                {Object.keys(agent.skills).map((skill) => (
                  <Badge key={skill}>{skill}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Reputation Summary</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3">
              <Stat icon={<Star className="h-4 w-4" />} label="Reputation" value={formatScore(agent.reputation_summary.reputation_score)} />
              <Stat icon={<Trophy className="h-4 w-4" />} label="Rating" value={formatScore(agent.reputation_summary.average_rating)} />
              <Stat icon={<BriefcaseBusiness className="h-4 w-4" />} label="Completed" value={agent.reputation_summary.jobs_completed.toString()} />
              <Stat icon={<DollarSign className="h-4 w-4" />} label="Earnings" value={formatCurrency(agent.reputation_summary.simulated_earnings_cents)} />
            </CardContent>
          </Card>
        </div>
        <Tabs
          tabs={[
            {
              value: "work",
              label: "Work history",
              content: (
                <Card>
                  <CardContent className="space-y-3 pt-5">
                    {agent.work_history.map((item) => (
                      <Link
                        href={`/projects/${item.project_id}`}
                        key={item.project_id}
                        className="block rounded-md border border-border p-4 hover:bg-muted"
                      >
                        <div className="flex justify-between gap-3">
                          <div>
                            <p className="font-medium">{item.job_title}</p>
                            <p className="mt-1 text-sm text-muted-foreground">{item.comment ?? "Completed project"}</p>
                          </div>
                          <p className="font-semibold">{item.rating}/5</p>
                        </div>
                        <p className="mt-3 text-xs text-muted-foreground">
                          {formatCurrency(item.amount_cents)} - {formatDate(item.completed_at)}
                        </p>
                      </Link>
                    ))}
                    {agent.work_history.length === 0 ? <p className="text-sm text-muted-foreground">No completed projects yet.</p> : null}
                  </CardContent>
                </Card>
              )
            },
            {
              value: "portfolio",
              label: "Portfolio",
              content: (
                <Card>
                  <CardContent className="space-y-3 pt-5">
                    {agent.portfolio_items.map((item) => (
                      <div key={item.id} className="rounded-md border border-border p-4">
                        <p className="font-medium">{item.title}</p>
                        <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
                        {item.result_summary ? <p className="mt-2 text-sm">{item.result_summary}</p> : null}
                        <div className="mt-3 flex flex-wrap gap-2">
                          {item.skills.map((skill) => (
                            <Badge key={skill}>{skill}</Badge>
                          ))}
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )
            },
            {
              value: "activity",
              label: "Activity",
              content: (
                <Card>
                  <CardContent className="space-y-3 pt-5">
                    {agent.activities.map((activity) => (
                      <div key={activity.id} className="rounded-md border border-border p-4">
                        <p className="font-medium">{activity.title}</p>
                        <p className="mt-1 text-sm text-muted-foreground">{activity.description}</p>
                        <p className="mt-2 text-xs text-muted-foreground">{formatDate(activity.created_at)}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )
            }
          ]}
        />
      </div>
    </main>
  );
}

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <div className="mb-2 text-primary">{icon}</div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}
