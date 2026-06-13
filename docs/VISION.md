# TITAN — Refined Product Vision

> **Transparency Intelligence Technology Agent Network**
> *An autonomous AI civilization that deliberates, debates, and decides — transparently.*

---

## 1. Improved Product Vision

### The Problem

Real-world governance fails at scale. Human decision-makers are slow, biased, siloed, and opaque. Societal problems — urban unemployment, climate policy, healthcare allocation — demand multi-disciplinary reasoning across thousands of variables simultaneously. No single expert, committee, or model can do this alone.

### The TITAN Answer

TITAN is an **autonomous AI governance civilization** — not a chatbot, not a dashboard, not a single LLM prompt. It is a structured society of specialized AI agents that:

- **Analyse** problems independently through distinct domain lenses
- **Debate** in structured adversarial rounds where each minister defends and challenges
- **Vote** democratically with transparent confidence scores and justifications
- **Simulate** the top policy options against synthetic real-world scenarios
- **Synthesize** a final, stress-tested, rationale-backed policy recommendation

TITAN does not produce a single AI opinion. It produces **civilizational consensus** — the output of structured disagreement, resolved through democratic process, hardened by simulation, and signed off by a Prime Minister agent who is accountable to all other ministers.

### Core Promise

> Submit any complex societal problem. Receive a debate-tested, simulation-validated, multi-perspective policy recommendation — in minutes, not months.

### Design Principles

| Principle | What It Means |
|---|---|
| **Adversarial by design** | The Opposition Minister is not optional — it is structurally required |
| **No black boxes** | Every analysis, argument, vote, and simulation score is recorded and surfaced |
| **Role-bound cognition** | Each agent is constrained to its domain; no minister can speak outside its mandate |
| **Democratic resolution** | No single agent dominates; votes, confidence scores, and dissents are all visible |
| **Simulation before action** | No recommendation reaches the PM without being stress-tested first |

---

## 2. Core User Journey

### The Five Moments That Matter

```
┌─────────────────────────────────────────────────────────────────────┐
│  MOMENT 1 — SUBMIT                                                  │
│  User types a problem. TITAN parses intent, classifies domain,      │
│  and assigns context. Session is created. Cabinet convenes.         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  MOMENT 2 — WATCH THE CABINET THINK (Live Analysis Feed)            │
│  Six ministers analyse in parallel. The user sees each minister's   │
│  card light up, stream their findings in real-time. No waiting.     │
│  Each card shows: key findings, concerns, proposed solutions.       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  MOMENT 3 — THE DEBATE (Most Compelling Experience)                 │
│  Ministers argue in sequence. The Opposition attacks. Ministers      │
│  rebut. The user watches a structured political debate unfold in    │
│  real-time — disagreements, concessions, counter-proposals.         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  MOMENT 4 — THE VOTE + SIMULATION                                   │
│  Ministers vote with confidence scores. A radar chart shows         │
│  consensus vs. dissent. The Simulation Agent stress-tests the       │
│  top 3 options: economic score, social score, feasibility,          │
│  environmental impact, implementation cost, and timeline.           │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│  MOMENT 5 — THE FINAL REPORT                                        │
│  The Prime Minister synthesizes all inputs into a final policy:     │
│  chosen option, rationale, phased implementation plan, success      │
│  metrics, risks & mitigations, and a Black Swan resilience score.   │
│  User can export the full report as PDF or share a public link.     │
└─────────────────────────────────────────────────────────────────────┘
```

### Secondary Journeys

- **Browse Past Sessions** — Search, filter, and compare historical governance reports
- **Deep-Dive a Report** — Inspect any minister's full analysis, individual debate arguments, or vote justification
- **Replay Mode** — Replay a session step-by-step to understand how consensus was reached
- **Compare Policies** — Side-by-side comparison of two sessions on similar problems

---

## 3. Complete System Architecture

### 3.1 Layered Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│          Next.js 15 (App Router) · TypeScript · Tailwind            │
│   Pages: /  ·  /sessions  ·  /sessions/[id]  ·  /sessions/[id]/    │
│           report                                                    │
│   State: Zustand  ·  Streaming: SSE client  ·  Charts: Recharts     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP + SSE
┌──────────────────────────────▼──────────────────────────────────────┐
│                          API GATEWAY LAYER                          │
│                   FastAPI · Async · Pydantic v2                     │
│   /api/v1/sessions (CRUD)                                           │
│   /api/v1/sessions/{id}/stream (SSE)                                │
│   /api/v1/sessions/{id}/report (full export)                        │
│   /api/v1/health                                                    │
└──────────┬──────────────────────────────────────┬───────────────────┘
           │ SQLAlchemy (async)                    │ asyncio background task
┌──────────▼────────────┐              ┌───────────▼───────────────────┐
│    PERSISTENCE LAYER  │              │     AGENT ORCHESTRATION LAYER │
│   PostgreSQL 16        │              │     LangGraph StateGraph       │
│   Alembic migrations   │              │                               │
│                        │              │  ┌──── GovernanceState ──────┐ │
│   Tables:              │              │  │ project_id · problem      │ │
│   · projects           │◄─────────────┤  │ analyses · debates · votes│ │
│   · agents (analyses)  │              │  │ simulations · final_report│ │
│   · debates            │              │  └───────────────────────────┘ │
│   · votes              │              │                               │
│   · simulations        │              │  Nodes (execution units):     │
│   · final_reports      │              │  · input_validation           │
│                        │              │  · minister_analysis (×6)     │
└────────────────────────┘              │  · aggregate_analyses         │
                                        │  · debate_round               │
┌───────────────────────────────────────┤  · opposition_attack          │
│            EVENT BUS (SSE Pub/Sub)   │  · rebuttal_round             │
│   AsyncIO in-process channels         │  · minister_vote (×6)         │
│   project_id → subscriber queue       │  · tally_votes                │
│   Graceful cleanup on session close   │  · simulation_phase           │
└───────────────────────────────────────┤  · prime_minister_synthesis   │
                                        │  · black_swan_engine          │
                                        │  · error_handler              │
                                        └───────────────────────────────┘
```

### 3.2 Agent Cabinet — Roles & Mandate

| Agent | Role | Domain Mandate | Personality Constraint |
|---|---|---|---|
| 👑 **Prime Minister** | Synthesizer & final authority | Cross-domain integration, national interest | Must acknowledge all minister dissents |
| 📈 **Economic Minister** | Domain analyst | GDP, employment, fiscal/monetary policy | Growth-biased; flags job impacts first |
| 💻 **Technology Minister** | Domain analyst | Digital infra, innovation, R&D | Technology-optimist; advocates scalable solutions |
| 🏗️ **Infrastructure Minister** | Domain analyst | Roads, energy, water, logistics | Pragmatic; cost-conscious; opposes unfunded mandates |
| 👥 **Citizen Minister** | Domain analyst | Social equity, welfare, inclusion | People-first; rejects solutions that harm vulnerable groups |
| 🌿 **Environment Minister** | Domain analyst | Climate, sustainability, ecology | Conservation-focused; challenges carbon-heavy proposals |
| 🛡️ **Opposition Minister** | Structural challenger | Critique, risk identification, alternatives | Contrarian by design; cannot vote FOR the status quo |
| 🔬 **Simulation Agent** | Scenario modeller | Stress-testing, scoring, projection | Data-driven; no political affiliation |

### 3.3 Governance Pipeline (Phase-by-Phase)

```
Phase 0 — Validation
  └─ Input validated: topic, language, length, harm policy
  └─ Context enriched (optional user context attached)
  └─ Session created → status: PENDING → ANALYZING

Phase 1 — Parallel Analysis (6 simultaneous LLM calls)
  ├─ economic_minister     → MinisterOutput (JSON)
  ├─ technology_minister   → MinisterOutput (JSON)
  ├─ infrastructure_minister → MinisterOutput
  ├─ citizen_minister      → MinisterOutput
  ├─ environment_minister  → MinisterOutput
  └─ opposition_minister   → MinisterOutput
  → aggregate_analyses: collects all 6, extracts policy_options list

Phase 2 — Structured Debate (sequential, awareness of all analyses)
  ├─ debate_round: 5 ministers present initial positions
  ├─ opposition_attack: opposition systematically attacks each proposal
  └─ rebuttal_round: 5 ministers rebut in parallel

Phase 3 — Democratic Vote (6 simultaneous LLM calls)
  ├─ Each minister: voted_option + confidence_score + justification + veto_options
  └─ tally_votes: determines winning option, consensus level, vote distribution

Phase 4 — Simulation (Simulation Agent, sequential per option)
  ├─ Top 3 options stress-tested across 5 synthetic scenarios
  ├─ Scored: economic, social, environmental, feasibility, composite
  └─ Outputs: cost estimate, time-to-implement, key risks, key benefits

Phase 5 — Synthesis (Prime Minister, single LLM call, model: Pro)
  ├─ Reads all analyses, debate, vote tally, simulation scores
  ├─ Selects winning option with full rationale
  ├─ Produces phased implementation plan (steps, timelines, owners)
  └─ Flags dissents and unresolved tensions

Phase 6 — Black Swan Engine
  ├─ Identifies low-probability, high-impact crisis scenarios
  ├─ Scores the chosen policy's resilience against each black swan
  └─ Produces resilience_score and contingency guidance

→ Status: COMPLETED
→ SSE: session_complete event fired
→ DB: all outputs persisted
```

### 3.4 Data Flow

```
Browser
  │ POST /api/v1/sessions {problem, context}
  ▼
FastAPI
  │ create_project() → DB insert → returns session_id
  │ asyncio.create_task(run_agent_graph(session_id))
  ▼
Browser
  │ GET /api/v1/sessions/{id}/stream (SSE connection)
  ▼
EventBus (in-process pub/sub)
  ▲ publish(project_id, event_type, payload)
  │
LangGraph Graph
  ├─ node fires → publishes SSE event → browser receives → UI updates
  ├─ node fires → publishes SSE event → browser receives → UI updates
  └─ ... (every phase transition emits an event)
  │
  ▼ final_state
SessionService._persist_state()
  └─ bulk DB insert: agents, debates, votes, simulations, final_report
```

### 3.5 SSE Event Taxonomy

| Event | When Fired | Payload |
|---|---|---|
| `session_started` | Graph begins | `{project_id}` |
| `analysis_started` | Per minister analysis start | `{minister_role}` |
| `analysis_complete` | Per minister analysis done | `MinisterOutput` |
| `debate_started` | Debate phase begins | `{round: 1}` |
| `debate_argument` | Each debate output | `DebateArgument` |
| `debate_complete` | All debate rounds done | `{rounds_completed}` |
| `voting_started` | Vote phase begins | `{options: [...]}` |
| `vote_cast` | Per minister vote | `VoteRecord` |
| `voting_complete` | Tally done | `{winner, vote_tally}` |
| `simulation_started` | Simulation begins | `{options_to_test}` |
| `simulation_result` | Per option scored | `SimulationResult` |
| `simulation_complete` | All options scored | `{results: [...]}` |
| `synthesis_started` | PM synthesis begins | `{}` |
| `synthesis_complete` | Final report ready | `FinalPolicy` |
| `session_complete` | Everything done | `{final_report}` |
| `error` | Any failure | `{message}` |
| `heartbeat` | Every 15s | `{ts}` |

### 3.6 Database Schema

```sql
-- Core session (renamed from session → project for clarity)
projects
  id UUID PK · title TEXT · problem TEXT · context TEXT
  status ENUM(pending,analyzing,debating,voting,simulating,synthesizing,completed,failed)
  error_message TEXT · metadata JSONB · created_at · completed_at

-- Per-minister analysis output
agents
  id UUID PK · project_id FK · role ENUM · model_used TEXT
  analysis TEXT · key_points JSONB · proposed_solutions JSONB
  concerns JSONB · tokens_used INT · processing_ms INT · created_at

-- All debate phases (debate / opposition_attack / rebuttal)
debates
  id UUID PK · project_id FK · agent_id FK
  round_number INT · phase TEXT · argument TEXT
  supporting_agents JSONB · opposing_agents JSONB · word_count INT · created_at

-- Democratic votes
votes
  id UUID PK · project_id FK · agent_id FK
  voted_option TEXT · confidence_score FLOAT · justification TEXT · created_at

-- Simulation stress-test results
simulations
  id UUID PK · project_id FK · option_name TEXT · option_description TEXT
  economic_score FLOAT · social_score FLOAT · environmental_score FLOAT
  feasibility_score FLOAT · composite_score FLOAT · risk_level ENUM
  time_to_implement_months INT · cost_estimate_usd_millions FLOAT
  projected_population_impact FLOAT · key_risks JSONB · key_benefits JSONB
  scenario_data JSONB · created_at

-- Prime Minister final synthesis
final_reports
  id UUID PK · project_id FK · chosen_option TEXT · executive_summary TEXT
  overall_rationale TEXT · confidence_score FLOAT
  implementation_steps JSONB · success_metrics JSONB
  risks_and_mitigations JSONB · expected_outcomes JSONB
  review_timeline TEXT · total_votes INT · winning_votes INT
  vote_percentage FLOAT · consensus_level TEXT
  black_swan_crisis TEXT · black_swan_impact TEXT · resilience_score FLOAT
  model_used TEXT · created_at
```

### 3.7 Monorepo Structure

```
TITAN/
├── apps/
│   ├── web/                              # Next.js 15 Frontend
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (app)/
│   │       │   │   ├── page.tsx          # Landing + problem submission
│   │       │   │   ├── sessions/
│   │       │   │   │   └── page.tsx      # Session history & search
│   │       │   │   └── sessions/[id]/
│   │       │   │       ├── page.tsx      # Live session dashboard
│   │       │   │       └── report/
│   │       │   │           └── page.tsx  # Full exportable report
│   │       │   ├── layout.tsx
│   │       │   └── globals.css
│   │       ├── components/
│   │       │   ├── ui/                   # Base primitives (Button, Card, Badge…)
│   │       │   ├── layout/               # Sidebar, Header, Shell
│   │       │   └── session/              # Cabinet, DebateFeed, VotePanel,
│   │       │                             #   SimulationChart, FinalReport
│   │       ├── lib/
│   │       │   ├── api-client.ts         # Typed Axios wrapper
│   │       │   ├── sse-client.ts         # SSE connection manager + reconnect
│   │       │   └── utils.ts
│   │       ├── hooks/
│   │       │   ├── use-session-stream.ts # SSE → Zustand bridge
│   │       │   └── use-session.ts        # SWR data fetching hook
│   │       └── store/
│   │           └── session-store.ts      # Zustand: live session state
│   │
│   └── api/                              # FastAPI Backend
│       ├── app/
│       │   ├── agents/
│       │   │   ├── graph.py              # LangGraph StateGraph definition ⭐
│       │   │   ├── nodes.py              # All node implementations
│       │   │   ├── state.py              # GovernanceState TypedDict
│       │   │   ├── prompts.py            # System prompts per minister
│       │   │   └── ministers/            # Per-minister persona configs
│       │   ├── api/
│       │   │   └── v1/
│       │   │       ├── sessions.py       # REST + SSE endpoints
│       │   │       └── health.py         # Health endpoint
│       │   ├── core/
│       │   │   ├── config.py             # Pydantic Settings
│       │   │   ├── database.py           # Async SQLAlchemy engine
│       │   │   └── logging.py            # Structlog structured logging
│       │   ├── models/
│       │   │   └── session.py            # SQLAlchemy ORM models
│       │   ├── repositories/             # DB access layer (query logic)
│       │   │   └── session_repository.py
│       │   ├── schemas/
│       │   │   └── session.py            # Pydantic request/response schemas
│       │   └── services/
│       │       ├── event_bus.py          # Async SSE pub/sub channels
│       │       └── session_service.py    # Orchestration: create → run → persist
│       ├── alembic/                      # Database migrations
│       ├── main.py                       # FastAPI app factory
│       └── requirements.txt
│
├── packages/
│   └── shared-types/                     # Shared TypeScript types
│       └── src/index.ts                  # All interfaces + MINISTER_META
│
├── docs/                                 # Project documentation
│   ├── VISION.md                         # This document
│   ├── ARCHITECTURE.md                   # Deep technical reference
│   └── CONTRIBUTING.md                   # Developer guide
│
├── docker/
│   ├── docker-compose.yml                # Full stack (Postgres + API + Web)
│   ├── Dockerfile.api                    # Python 3.12 slim
│   └── Dockerfile.web                    # Node 20 multi-stage
│
├── turbo.json                            # Turborepo pipeline
├── pnpm-workspace.yaml                   # pnpm workspace config
├── titan.code-workspace                  # VS Code multi-root workspace
└── README.md
```

---

## 4. Key Differentiators

### What Makes TITAN Unique

| Differentiator | Description | Why It Matters |
|---|---|---|
| **Adversarial Architecture** | Opposition Minister is structurally forced to challenge every proposal | Prevents groupthink; identifies blind spots that agreeable agents miss |
| **Democratic Resolution** | Votes with confidence scores, veto options, and second choices | Not a winner-take-all system; consensus level is tracked and surfaced |
| **Black Swan Engine** | Final resilience stress-test against low-probability, high-impact crises | Policies are not just optimised for expected scenarios; they survive shocks |
| **Full Audit Trail** | Every analysis, argument, vote, and score is persisted and queryable | Radical transparency — users can trace exactly why a policy was chosen |
| **Parallelised Analysis** | All 6 ministers analyse simultaneously via LangGraph Send fan-out | Speed without sacrificing depth; minutes instead of sequential hours |
| **Simulation Before Synthesis** | PM cannot synthesise until simulation scores are available | Removes the "sounds good in theory" failure mode |
| **Role-Bounded Cognition** | Each minister's system prompt constrains them to their mandate | Prevents an economic minister from making environmental arguments |
| **Real-Time Experience** | SSE streaming brings every agent action to the UI the moment it happens | Users feel like observers in a live government session, not waiting for a batch job |

### vs. Existing Alternatives

| Capability | ChatGPT/Claude (single prompt) | Multi-agent frameworks (raw) | TITAN |
|---|---|---|---|
| Multi-perspective deliberation | ❌ Single voice | ⚠️ Requires custom build | ✅ Built-in, role-bounded |
| Adversarial challenge | ❌ | ⚠️ Manual | ✅ Opposition agent required |
| Democratic voting | ❌ | ❌ | ✅ With confidence + veto |
| Scenario simulation | ❌ | ❌ | ✅ Per policy option |
| Black swan resilience | ❌ | ❌ | ✅ Dedicated phase |
| Full audit trail | ❌ | ❌ | ✅ DB-persisted, queryable |
| Real-time streaming UI | ❌ | ❌ | ✅ SSE per agent event |
| Export / share report | ❌ | ❌ | ✅ PDF + public link (roadmap) |

---

## 5. Final Refined Scope for MVP

### MVP Goal

> A user can submit a societal problem, watch the AI cabinet debate it live, see votes and simulation scores, and receive a final policy recommendation — end-to-end, in a single session, with full persistence and a shareable report.

### MVP Scope — What's IN

#### Backend (API + Agents)
- [x] FastAPI with async architecture
- [x] LangGraph governance graph (all 8 agents)
- [x] GovernanceState with proper Annotated reducers for fan-out
- [x] All 6 phases: Analysis → Debate → Vote → Simulation → Synthesis → Black Swan
- [x] PostgreSQL persistence (projects, agents, debates, votes, simulations, final_reports)
- [x] Alembic migrations
- [x] SSE EventBus with per-session channels
- [x] Structured logging (Structlog)
- [ ] Repository layer: extract all DB queries from services into `repositories/`
- [ ] Retry logic on LLM calls (exponential backoff, max 3 retries)
- [ ] Input validation: min/max length, topic classification, harm filter
- [ ] `/api/v1/sessions/{id}/report` full export endpoint

#### Frontend (Web)
- [x] Next.js 15 App Router skeleton
- [x] Shared TypeScript types with MINISTER_META
- [ ] Landing page: problem submission form (clear, focused, premium design)
- [ ] Live session dashboard `/sessions/[id]`:
  - Minister cards with streaming analysis
  - Debate feed (argument → attack → rebuttal timeline)
  - Vote panel (bar chart + confidence scores)
  - Simulation comparison table/chart
  - Final report reveal (PM synthesis + black swan score)
- [ ] Sessions list page `/sessions` (history, status badges, search)
- [ ] Full report page `/sessions/[id]/report`
- [ ] SSE client with auto-reconnect and heartbeat handling
- [ ] Zustand store wired to SSE events
- [ ] Error states and loading skeletons

#### Infrastructure
- [x] Docker Compose (Postgres + API + Web)
- [x] Turborepo monorepo pipeline
- [ ] Health checks on all three services
- [ ] Environment variable validation on startup (fail fast if GEMINI_API_KEY missing)

### MVP Scope — What's OUT (Post-MVP Roadmap)

| Feature | Reason Deferred |
|---|---|
| Authentication / user accounts | Not required to demonstrate core value |
| PDF export | Nice-to-have; core UX works without it |
| Public sharing links | Requires auth infrastructure first |
| Multi-language support | Scope creep for MVP |
| Configurable agent personas | Advanced; default personas sufficient for demo |
| Custom debate round count | Env-var configurable; no UI needed in MVP |
| Comparative session analysis | Requires at least N sessions first |
| Webhooks / async notifications | No use case established yet |
| Rate limiting / quota management | Deploy concern, not MVP concern |
| Multi-tenant / org support | Enterprise feature |

### MVP Success Criteria

| Criterion | Measure |
|---|---|
| **End-to-end completion** | A session submitted completes without error in < 5 minutes |
| **Full persistence** | All 6 phases' outputs are queryable in the DB after completion |
| **Live streaming** | Every phase transition reaches the browser via SSE within 2s of firing |
| **Transparent rationale** | Final report includes chosen option, rationale, vote breakdown, and simulation scores |
| **Resilience** | Black Swan score is surfaced on the final report |
| **Reproducibility** | Any past session report is retrievable from `/sessions/[id]/report` |

---

## Appendix — Naming Conventions

| Concept | Internal Name | Notes |
|---|---|---|
| A governance run | `project` / `session` (both valid) | `project_id` in backend; `session_id` in API responses for backwards compatibility |
| A minister's AI output | `agent` | Stored in `agents` table |
| A debate contribution | `debate` | Covers all phases: debate, attack, rebuttal |
| The stress-test | `simulation` | Per policy option |
| The final output | `final_report` | PM synthesis + black swan combined |

---

*TITAN — Where AI Governs, Transparently.*
