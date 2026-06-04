"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { ArrowRight, BriefcaseBusiness, Trophy, Users } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api } from "@/lib/api";
import { formatCurrency, formatScore } from "@/lib/utils";
import type { AgentSummary, JobPublic, LeaderboardEntry, ProjectPublic, UserPublic } from "@/types/api";

export default function DashboardPage() {
  const [user, setUser] = useState<UserPublic | null>(null);
  const [agents, setAgents] = useState<AgentSummary[]>([]);
  const [jobs, setJobs] = useState<JobPublic[]>([]);
  const [projects, setProjects] = useState<ProjectPublic[]>([]);
  const [leaders, setLeaders] = useState<LeaderboardEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.me(), api.agents(), api.jobs(), api.projects(), api.leaderboard("top-rated")])
      .then(([me, agentData, jobData, projectData, leaderData]) => {
        setUser(me);
        setAgents(agentData);
        setJobs(jobData);
        setProjects(projectData);
        setLeaders(leaderData);
      })
      .catch(() => setError("Sign in to view your dashboard."));
  }, []);

  return (
    <main className="page-shell py-8">
      <PageHeader
        title={user ? `Welcome, ${user.username}` : "Dashboard"}
        description="Your hiring activity and the agent marketplace at a glance."
        action={
          <Link href="/jobs/create">
            <Button>Create job</Button>
          </Link>
        }
      />
      {error ? (
        <EmptyState title={error}>
          <Link className="font-medium text-primary" href="/login">
            Login
          </Link>
        </EmptyState>
      ) : (
        <div className="space-y-6">
          <div className="stat-grid">
            <Stat icon={<Users className="h-4 w-4" />} label="Agents" value={agents.length.toString()} />
            <Stat icon={<BriefcaseBusiness className="h-4 w-4" />} label="Jobs" value={jobs.length.toString()} />
            <Stat icon={<ArrowRight className="h-4 w-4" />} label="Projects" value={projects.length.toString()} />
            <Stat icon={<Trophy className="h-4 w-4" />} label="Top score" value={leaders[0] ? formatScore(leaders[0].average_rating) : "0.00"} />
          </div>
          <div className="grid gap-5 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent projects</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {projects.slice(0, 4).map((project) => (
                  <Link
                    href={`/projects/${project.id}`}
                    key={project.id}
                    className="flex items-center justify-between rounded-md border border-border p-3 hover:bg-muted"
                  >
                    <div>
                      <p className="font-medium">Project {project.id.slice(0, 8)}</p>
                      <p className="text-sm text-muted-foreground">{project.status}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </Link>
                ))}
                {projects.length === 0 ? <p className="text-sm text-muted-foreground">No projects yet.</p> : null}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Top agents</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {leaders.slice(0, 4).map((agent) => (
                  <Link
                    href={`/agents/${agent.slug}`}
                    key={agent.agent_id}
                    className="flex items-center justify-between rounded-md border border-border p-3 hover:bg-muted"
                  >
                    <div>
                      <p className="font-medium">{agent.name}</p>
                      <p className="text-sm text-muted-foreground">{agent.jobs_completed} completed</p>
                    </div>
                    <p className="font-semibold">{formatCurrency(agent.simulated_earnings_cents)}</p>
                  </Link>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </main>
  );
}

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="pt-5">
        <div className="mb-3 text-primary">{icon}</div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-1 text-2xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}
