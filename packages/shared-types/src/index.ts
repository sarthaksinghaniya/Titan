// ============================================================
// TITAN — Shared Types Package
// Mirrors backend Pydantic models for end-to-end type safety
// ============================================================

// ─── Enums ───────────────────────────────────────────────────

export type MinisterRole =
  | "prime_minister"
  | "economic_minister"
  | "technology_minister"
  | "infrastructure_minister"
  | "citizen_minister"
  | "environment_minister"
  | "opposition_minister"
  | "simulation_agent";

export type SessionStatus =
  | "pending"
  | "analyzing"
  | "debating"
  | "voting"
  | "simulating"
  | "synthesizing"
  | "completed"
  | "failed";

export type RiskLevel = "low" | "medium" | "high" | "critical";

// ─── Core Entities ───────────────────────────────────────────

export interface Session {
  id: string;
  problem: string;
  context?: string;
  status: SessionStatus;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface MinisterAnalysis {
  id: string;
  session_id: string;
  minister_role: MinisterRole;
  analysis_text: string;
  key_points: string[];
  proposed_solutions: string[];
  concerns: string[];
  created_at: string;
}

export interface DebateRound {
  id: string;
  session_id: string;
  round_number: number;
  minister_role: MinisterRole;
  argument_text: string;
  supporting_ministers: MinisterRole[];
  opposing_ministers: MinisterRole[];
  created_at: string;
}

export interface Vote {
  id: string;
  session_id: string;
  minister_role: MinisterRole;
  voted_option: string;
  confidence_score: number; // 0–100
  justification: string;
  created_at: string;
}

export interface SimulationResult {
  id: string;
  session_id: string;
  option_name: string;
  economic_score: number; // 0–100
  social_score: number; // 0–100
  environmental_score: number; // 0–100
  feasibility_score: number; // 0–100
  risk_level: RiskLevel;
  time_to_implement_months: number;
  cost_estimate_usd_millions: number;
  projected_population_impact: number; // in millions
  key_risks: string[];
  key_benefits: string[];
  created_at: string;
}

export interface PolicyStep {
  phase: string;
  duration: string;
  actions: string[];
  responsible_ministry: string;
  budget_allocation_percent: number;
}

export interface FinalPolicy {
  id: string;
  session_id: string;
  chosen_option: string;
  overall_rationale: string;
  implementation_steps: PolicyStep[];
  success_metrics: string[];
  risks_and_mitigations: Record<string, string>;
  expected_outcomes: string[];
  review_timeline: string;
  created_at: string;
}

// ─── Full Session Report ──────────────────────────────────────

export interface SessionReport {
  session: Session;
  analyses: MinisterAnalysis[];
  debate_rounds: DebateRound[];
  votes: Vote[];
  simulation_results: SimulationResult[];
  final_policy?: FinalPolicy;
}

// ─── API Request / Response Shapes ───────────────────────────

export interface CreateSessionRequest {
  problem: string;
  context?: string;
}

export interface CreateSessionResponse {
  session_id: string;
  status: SessionStatus;
  message: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

// ─── SSE Event Types ──────────────────────────────────────────

export type SSEEventType =
  | "session_started"
  | "analysis_started"
  | "analysis_complete"
  | "debate_started"
  | "debate_argument"
  | "debate_complete"
  | "voting_started"
  | "vote_cast"
  | "voting_complete"
  | "simulation_started"
  | "simulation_result"
  | "simulation_complete"
  | "synthesis_started"
  | "synthesis_complete"
  | "session_complete"
  | "error"
  | "heartbeat";

export interface SSEEvent<T = unknown> {
  event: SSEEventType;
  data: T;
  timestamp: string;
}

export interface AnalysisSSEData {
  minister_role: MinisterRole;
  chunk: string;
  is_complete: boolean;
  analysis?: MinisterAnalysis;
}

export interface DebateSSEData {
  round_number: number;
  minister_role: MinisterRole;
  chunk: string;
  is_complete: boolean;
  debate_round?: DebateRound;
}

export interface VoteSSEData {
  minister_role: MinisterRole;
  vote: Vote;
}

export interface SimulationSSEData {
  option_name: string;
  result: SimulationResult;
}

export interface SynthesisSSEData {
  chunk: string;
  is_complete: boolean;
  policy?: FinalPolicy;
}

// ─── Minister Metadata (UI Helpers) ──────────────────────────

export interface MinisterMeta {
  role: MinisterRole;
  title: string;
  description: string;
  color: string;
  gradient: string;
  icon: string;
  focus_areas: string[];
}

export const MINISTER_META: Record<MinisterRole, MinisterMeta> = {
  prime_minister: {
    role: "prime_minister",
    title: "Prime Minister",
    description: "Final decision-maker and policy synthesizer",
    color: "#f59e0b",
    gradient: "from-amber-500 to-orange-600",
    icon: "Crown",
    focus_areas: ["Strategic synthesis", "National interest", "Final policy"],
  },
  economic_minister: {
    role: "economic_minister",
    title: "Economic Minister",
    description: "GDP, employment, fiscal and monetary impact",
    color: "#10b981",
    gradient: "from-emerald-500 to-green-600",
    icon: "TrendingUp",
    focus_areas: ["GDP impact", "Employment", "Fiscal policy"],
  },
  technology_minister: {
    role: "technology_minister",
    title: "Technology Minister",
    description: "Digital infrastructure, innovation and R&D",
    color: "#6366f1",
    gradient: "from-indigo-500 to-violet-600",
    icon: "Cpu",
    focus_areas: ["Digital infrastructure", "Innovation", "Tech adoption"],
  },
  infrastructure_minister: {
    role: "infrastructure_minister",
    title: "Infrastructure Minister",
    description: "Roads, energy, water and logistics networks",
    color: "#f97316",
    gradient: "from-orange-500 to-red-600",
    icon: "Building2",
    focus_areas: ["Physical infrastructure", "Logistics", "Cost feasibility"],
  },
  citizen_minister: {
    role: "citizen_minister",
    title: "Citizen Minister",
    description: "Public welfare, equity and social cohesion",
    color: "#ec4899",
    gradient: "from-pink-500 to-rose-600",
    icon: "Users",
    focus_areas: ["Social equity", "Public welfare", "Community impact"],
  },
  environment_minister: {
    role: "environment_minister",
    title: "Environment Minister",
    description: "Climate, sustainability and ecological impact",
    color: "#22c55e",
    gradient: "from-green-500 to-teal-600",
    icon: "Leaf",
    focus_areas: ["Climate impact", "Sustainability", "Ecological balance"],
  },
  opposition_minister: {
    role: "opposition_minister",
    title: "Opposition Minister",
    description: "Critical challenger — questions all proposals",
    color: "#ef4444",
    gradient: "from-red-500 to-rose-600",
    icon: "ShieldAlert",
    focus_areas: ["Risk identification", "Critique", "Alternative views"],
  },
  simulation_agent: {
    role: "simulation_agent",
    title: "Simulation Agent",
    description: "Synthetic stress-testing of proposed solutions",
    color: "#0ea5e9",
    gradient: "from-sky-500 to-cyan-600",
    icon: "FlaskConical",
    focus_areas: ["Stress testing", "Scenario modeling", "Risk scoring"],
  },
};
