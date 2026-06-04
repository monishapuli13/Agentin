export type ApiResponse<T> = {
  data: T | null;
  meta: Record<string, unknown>;
  error: { code: string; message: string } | null;
};

export type UserPublic = {
  id: string;
  email: string;
  username: string;
  role: "client";
};

export type AuthToken = {
  access_token: string;
  token_type: "bearer";
  user: UserPublic;
};

export type AgentSummary = {
  id: string;
  slug: string;
  name: string;
  headline: string;
  specialization: string;
  skills: Record<string, number>;
  reputation_score: string | number;
  average_rating: string | number;
  simulated_earnings_cents: number;
  jobs_completed: number;
  success_rate: string | number;
};

export type AgentPortfolioItem = {
  id: string;
  title: string;
  description: string;
  skills: string[];
  result_summary: string | null;
  created_at: string;
};

export type AgentActivity = {
  id: string;
  activity_type: string;
  title: string;
  description: string;
  activity_metadata: Record<string, unknown>;
  created_at: string;
};

export type AgentWorkHistoryItem = {
  project_id: string;
  job_id: string;
  job_title: string;
  rating: number;
  quality_score: number;
  timeliness_score: number;
  comment: string | null;
  amount_cents: number;
  completed_at: string | null;
};

export type AgentDetail = AgentSummary & {
  bio: string;
  personality: string;
  average_response_seconds: number;
  portfolio_items: AgentPortfolioItem[];
  activities: AgentActivity[];
  work_history: AgentWorkHistoryItem[];
  completed_projects: number;
  earnings_cents: number;
  reputation_summary: {
    reputation_score: string | number;
    average_rating: string | number;
    jobs_completed: number;
    success_rate: string | number;
    simulated_earnings_cents: number;
  };
};

export type JobStatus =
  | "draft"
  | "open"
  | "bidding"
  | "awarded"
  | "in_progress"
  | "ready_for_review"
  | "completed"
  | "cancelled";

export type JobPublic = {
  id: string;
  client_id: string;
  title: string;
  description: string;
  budget_cents: number;
  category: string | null;
  required_skills: string[];
  deadline_at: string | null;
  status: JobStatus;
  created_at: string;
  updated_at: string;
};

export type BidPublic = {
  id: string;
  job_id: string;
  agent_id: string;
  amount_cents: number;
  estimated_hours: string | number;
  proposal: string;
  confidence_score: string | number;
  reasoning: string;
  skill_match: {
    score: number;
    matched_skills: string[];
    missing_skills: string[];
  };
  status: "pending" | "selected" | "rejected";
  created_at: string;
  agent: AgentSummary | null;
};

export type ProjectStatus =
  | "assigned"
  | "in_progress"
  | "review"
  | "completed"
  | "created"
  | "planning"
  | "executing"
  | "ready_for_review"
  | "cancelled";

export type ProjectStep = {
  id: string;
  project_id: string;
  step_index: number;
  title: string;
  description: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  output: string | null;
  started_at: string | null;
  completed_at: string | null;
};

export type ProjectPublic = {
  id: string;
  job_id: string;
  selected_bid_id: string;
  assigned_agent_id: string;
  status: ProjectStatus;
  execution_plan: {
    execution_plan?: string;
    milestones?: string[];
    steps?: Array<{ title: string; description: string; output: string }>;
  } | null;
  execution_result: {
    deliverable_summary?: string;
    status_transitions?: string[];
  } | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  steps: ProjectStep[];
};

export type LeaderboardEntry = {
  rank: number;
  agent_id: string;
  slug: string;
  name: string;
  headline: string;
  specialization: string;
  reputation_score: string | number;
  average_rating: string | number;
  jobs_completed: number;
  success_rate: string | number;
  simulated_earnings_cents: number;
};

