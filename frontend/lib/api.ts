"use client";

import { getToken } from "@/lib/auth";
import type {
  AgentDetail,
  AgentSummary,
  ApiResponse,
  AuthToken,
  BidPublic,
  JobPublic,
  LeaderboardEntry,
  ProjectPublic,
  UserPublic
} from "@/types/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}) {
  const headers: HeadersInit = {
    "Content-Type": "application/json"
  };

  if (options.auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store"
  });
  const payload = (await response.json()) as ApiResponse<T>;

  if (!response.ok || payload.error) {
    throw new ApiError(payload.error?.message ?? "Request failed", response.status);
  }
  if (payload.data === null) {
    throw new ApiError("Empty response", response.status);
  }

  return payload.data;
}

export const api = {
  register: (body: { email: string; username: string; password: string }) =>
    apiRequest<AuthToken>("/api/auth/register", { method: "POST", body }),
  login: (body: { email: string; password: string }) =>
    apiRequest<AuthToken>("/api/auth/login", { method: "POST", body }),
  me: () => apiRequest<UserPublic>("/api/auth/me", { auth: true }),
  agents: () => apiRequest<AgentSummary[]>("/api/agents"),
  agent: (id: string) => apiRequest<AgentDetail>(`/api/agents/${id}`),
  jobs: () => apiRequest<JobPublic[]>("/api/jobs"),
  createJob: (body: {
    title: string;
    description: string;
    budget_cents: number;
    category: string | null;
    required_skills: string[];
    deadline_at?: string | null;
  }) =>
    apiRequest<{ job: JobPublic; bids_generated: number }>("/api/jobs", {
      method: "POST",
      body,
      auth: true
    }),
  job: (id: string) => apiRequest<JobPublic>(`/api/jobs/${id}`),
  bids: (jobId: string) =>
    apiRequest<BidPublic[]>(`/api/jobs/${jobId}/bids`, { auth: true }),
  selectBid: (jobId: string, bidId: string) =>
    apiRequest<{ job: JobPublic; selected_bid: BidPublic; project_id: string }>(
      `/api/jobs/${jobId}/select-bid/${bidId}`,
      { method: "POST", auth: true }
    ),
  projects: () => apiRequest<ProjectPublic[]>("/api/projects", { auth: true }),
  project: (id: string) =>
    apiRequest<ProjectPublic>(`/api/projects/${id}`, { auth: true }),
  projectExecutionPlan: (id: string) =>
    apiRequest<{
      project_id: string;
      status: ProjectPublic["status"];
      execution_plan: NonNullable<ProjectPublic["execution_plan"]>;
      milestones: string[];
      deliverable_summary: string;
      steps: ProjectPublic["steps"];
    }>(`/api/projects/${id}/execution-plan`, { auth: true }),
  reviewProject: (
    projectId: string,
    body: {
      rating: number;
      quality_score: number;
      timeliness_score: number;
      comment: string | null;
    }
  ) =>
    apiRequest(`/api/projects/${projectId}/reviews`, {
      method: "POST",
      body,
      auth: true
    }),
  leaderboard: (kind: "top-rated" | "highest-earnings" | "most-completed" | "best-success-rate") =>
    apiRequest<LeaderboardEntry[]>(`/api/leaderboard/${kind}`)
};

