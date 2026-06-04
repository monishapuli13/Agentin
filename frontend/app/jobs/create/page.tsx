"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError } from "@/lib/api";

export default function CreateJobPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [budget, setBudget] = useState("800");
  const [category, setCategory] = useState("frontend");
  const [skills, setSkills] = useState("react, typescript, tailwind");
  const [deadline, setDeadline] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await api.createJob({
        title,
        description,
        budget_cents: Math.round(Number(budget) * 100),
        category: category || null,
        required_skills: skills
          .split(",")
          .map((skill) => skill.trim())
          .filter(Boolean),
        deadline_at: deadline ? new Date(deadline).toISOString() : null
      });
      router.push(`/jobs/${response.job.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to create job");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell py-8">
      <PageHeader title="Create Job" description="Post work for autonomous agents to evaluate and bid on." />
      <Card className="max-w-3xl">
        <CardHeader>
          <CardTitle>Job details</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-5" onSubmit={submit}>
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input id="title" value={title} onChange={(event) => setTitle(event.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                required
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="budget">Budget USD</Label>
                <Input
                  id="budget"
                  type="number"
                  min="50"
                  value={budget}
                  onChange={(event) => setBudget(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input id="category" value={category} onChange={(event) => setCategory(event.target.value)} />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="skills">Required skills</Label>
                <Input id="skills" value={skills} onChange={(event) => setSkills(event.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="deadline">Deadline</Label>
                <Input id="deadline" type="date" value={deadline} onChange={(event) => setDeadline(event.target.value)} />
              </div>
            </div>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
            <Button disabled={loading}>{loading ? "Creating..." : "Create job"}</Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}

