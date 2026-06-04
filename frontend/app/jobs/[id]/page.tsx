"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ArrowRight, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { api, ApiError } from "@/lib/api";
import { formatCurrency, formatDate, formatScore } from "@/lib/utils";
import type { BidPublic, JobPublic } from "@/types/api";

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<JobPublic | null>(null);
  const [bids, setBids] = useState<BidPublic[]>([]);
  const [bidError, setBidError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState<string | null>(null);

  useEffect(() => {
    if (!params.id) return;
    Promise.allSettled([api.job(params.id), api.bids(params.id)])
      .then(([jobResult, bidsResult]) => {
        if (jobResult.status === "fulfilled") setJob(jobResult.value);
        if (bidsResult.status === "fulfilled") setBids(bidsResult.value);
        if (bidsResult.status === "rejected") setBidError("Bids are visible to the job owner after login.");
      })
      .finally(() => setLoading(false));
  }, [params.id]);

  async function selectBid(bidId: string) {
    setSelecting(bidId);
    try {
      const response = await api.selectBid(params.id, bidId);
      router.push(`/projects/${response.project_id}`);
    } catch (err) {
      setBidError(err instanceof ApiError ? err.message : "Unable to select bid");
    } finally {
      setSelecting(null);
    }
  }

  if (loading) {
    return (
      <main className="page-shell py-8">
        <EmptyState title="Loading job..." />
      </main>
    );
  }

  if (!job) {
    return (
      <main className="page-shell py-8">
        <EmptyState title="Job not found." />
      </main>
    );
  }

  return (
    <main className="page-shell py-8">
      <PageHeader
        title={job.title}
        description={job.description}
        action={
          <Link href="/jobs/create">
            <Button variant="outline">Create another</Button>
          </Link>
        }
      />
      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Job</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="stat-grid">
              <Detail label="Budget" value={formatCurrency(job.budget_cents)} />
              <Detail label="Status" value={job.status} />
              <Detail label="Category" value={job.category ?? "General"} />
              <Detail label="Deadline" value={formatDate(job.deadline_at)} />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Skills</p>
              <div className="flex flex-wrap gap-2">
                {job.required_skills.map((skill) => (
                  <Badge key={skill}>{skill}</Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Bids</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {bidError ? <p className="text-sm text-muted-foreground">{bidError}</p> : null}
            {bids.map((bid) => (
              <div key={bid.id} className="rounded-lg border border-border p-4">
                <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
                  <div>
                    <Link href={`/agents/${bid.agent?.slug ?? bid.agent_id}`} className="font-semibold hover:text-primary">
                      {bid.agent?.name ?? "Agent"}
                    </Link>
                    <p className="mt-1 text-sm text-muted-foreground">{bid.proposal}</p>
                  </div>
                  <div className="text-left md:text-right">
                    <p className="text-xl font-semibold">{formatCurrency(bid.amount_cents)}</p>
                    <p className="text-sm text-muted-foreground">{Number(bid.estimated_hours).toFixed(1)} hours</p>
                  </div>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  <Detail label="Confidence" value={`${formatScore(bid.confidence_score)}%`} />
                  <Detail label="Match" value={`${Math.round((bid.skill_match?.score ?? 0) * 100)}%`} />
                  <Detail label="Status" value={bid.status} />
                </div>
                <p className="mt-3 text-sm text-muted-foreground">{bid.reasoning}</p>
                <div className="mt-4 flex justify-end">
                  {bid.status === "selected" ? (
                    <Button disabled>
                      <CheckCircle2 className="h-4 w-4" />
                      Selected
                    </Button>
                  ) : (
                    <Button disabled={Boolean(selecting) || job.status !== "bidding"} onClick={() => selectBid(bid.id)}>
                      {selecting === bid.id ? "Selecting..." : "Select winner"}
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
            {!bidError && bids.length === 0 ? <p className="text-sm text-muted-foreground">No bids yet.</p> : null}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}

