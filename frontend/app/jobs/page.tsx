"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Plus } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";
import type { JobPublic } from "@/types/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .jobs()
      .then(setJobs)
      .catch(() => setError("Unable to load jobs."))
      .finally(() => setLoading(false));
  }, []);

  const openJobs = useMemo(() => jobs.filter((job) => job.status !== "cancelled"), [jobs]);

  return (
    <main className="page-shell py-8">
      <PageHeader
        title="Job Marketplace"
        description="Browse client work and track active autonomous bidding."
        action={
          <Link href="/jobs/create">
            <Button>
              <Plus className="h-4 w-4" />
              Create job
            </Button>
          </Link>
        }
      />
      {loading ? <EmptyState title="Loading jobs..." /> : null}
      {error ? <EmptyState title={error} /> : null}
      {!loading && !error && openJobs.length === 0 ? (
        <EmptyState title="No jobs posted yet.">
          <Link className="font-medium text-primary" href="/jobs/create">
            Create the first job
          </Link>
        </EmptyState>
      ) : null}
      <div className="grid gap-4">
        {openJobs.map((job) => (
          <Link key={job.id} href={`/jobs/${job.id}`}>
            <Card className="transition-colors hover:bg-muted/40">
              <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
                <div>
                  <CardTitle>{job.title}</CardTitle>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge>{job.status}</Badge>
                    {job.category ? <Badge>{job.category}</Badge> : null}
                    <Badge>{formatCurrency(job.budget_cents)}</Badge>
                  </div>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <p className="line-clamp-2 text-sm text-muted-foreground">{job.description}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {job.required_skills.map((skill) => (
                    <span key={skill} className="rounded-sm bg-secondary px-2 py-1 text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
                <p className="mt-4 text-xs text-muted-foreground">Deadline: {formatDate(job.deadline_at)}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}

