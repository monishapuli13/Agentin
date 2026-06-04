"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { CheckCircle2, Clock, Send } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { ProjectPublic } from "@/types/api";

export default function ProjectWorkspacePage() {
  const params = useParams<{ id: string }>();
  const [project, setProject] = useState<ProjectPublic | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rating, setRating] = useState("5");
  const [quality, setQuality] = useState("5");
  const [timeliness, setTimeliness] = useState("5");
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function loadProject() {
    if (!params.id) return;
    setLoading(true);
    api
      .project(params.id)
      .then(setProject)
      .catch(() => setError("Unable to load project."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadProject();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.id]);

  async function submitReview(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!project) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.reviewProject(project.id, {
        rating: Number(rating),
        quality_score: Number(quality),
        timeliness_score: Number(timeliness),
        comment: comment || null
      });
      loadProject();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to submit review");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="page-shell py-8">
        <EmptyState title="Loading project..." />
      </main>
    );
  }

  if (!project) {
    return (
      <main className="page-shell py-8">
        <EmptyState title={error ?? "Project not found."} />
      </main>
    );
  }

  const milestones = project.execution_plan?.milestones ?? [];
  const deliverableSummary = project.execution_result?.deliverable_summary ?? "Not available";
  const transitions = project.execution_result?.status_transitions ?? [project.status];

  return (
    <main className="page-shell py-8">
      <PageHeader
        title="Project Workspace"
        description={`Project ${project.id.slice(0, 8)} is ${project.status}.`}
        action={
          <Link href={`/agents/${project.assigned_agent_id}`}>
            <Button variant="outline">Agent profile</Button>
          </Link>
        }
      />
      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="space-y-5">
          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Badge>{project.status}</Badge>
              <div className="space-y-2">
                {transitions.map((transition) => (
                  <div key={transition} className="flex items-center gap-2 rounded-md border border-border p-3">
                    <CheckCircle2 className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium">{transition}</span>
                  </div>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">Started: {formatDate(project.started_at)}</p>
              <p className="text-xs text-muted-foreground">Completed: {formatDate(project.completed_at)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Deliverable Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-6 text-muted-foreground">{deliverableSummary}</p>
            </CardContent>
          </Card>
          {project.status === "review" ? (
            <Card>
              <CardHeader>
                <CardTitle>Review</CardTitle>
              </CardHeader>
              <CardContent>
                <form className="space-y-4" onSubmit={submitReview}>
                  <div className="grid gap-3 md:grid-cols-3">
                    <ScoreInput label="Rating" value={rating} onChange={setRating} />
                    <ScoreInput label="Quality" value={quality} onChange={setQuality} />
                    <ScoreInput label="Timeliness" value={timeliness} onChange={setTimeliness} />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="comment">Comment</Label>
                    <Textarea id="comment" value={comment} onChange={(event) => setComment(event.target.value)} />
                  </div>
                  {error ? <p className="text-sm text-destructive">{error}</p> : null}
                  <Button disabled={submitting}>
                    <Send className="h-4 w-4" />
                    {submitting ? "Submitting..." : "Submit review"}
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : null}
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Execution Plan</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <p className="text-sm leading-6 text-muted-foreground">
              {project.execution_plan?.execution_plan ?? "No execution plan stored."}
            </p>
            <div>
              <p className="mb-2 text-sm font-medium">Milestones</p>
              <div className="space-y-2">
                {milestones.map((milestone) => (
                  <div key={milestone} className="flex items-center gap-2 rounded-md bg-muted p-3">
                    <Clock className="h-4 w-4 text-primary" />
                    <span className="text-sm">{milestone}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              {project.steps.map((step) => (
                <div key={step.id} className="rounded-md border border-border p-4">
                  <div className="mb-2 flex items-start justify-between gap-3">
                    <div>
                      <p className="font-medium">
                        {step.step_index}. {step.title}
                      </p>
                      <p className="mt-1 text-sm text-muted-foreground">{step.description}</p>
                    </div>
                    <Badge>{step.status}</Badge>
                  </div>
                  {step.output ? <p className="mt-3 text-sm">{step.output}</p> : null}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

function ScoreInput({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={label}>{label}</Label>
      <Input
        id={label}
        type="number"
        min="1"
        max="5"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

