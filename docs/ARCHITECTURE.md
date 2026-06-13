# TITAN — Production Architecture Blueprint

> **Stack:** Next.js · Tailwind · shadcn/ui · FastAPI · LangGraph · PostgreSQL · Gemini AI
> **Pattern:** Monorepo · Event-driven · Async-first · Modular by domain

---

## 1. Folder Structure

```
TITAN/
│
├── apps/
│   │
│   ├── web/                                   # ── FRONTEND (Next.js 15)
│   │   ├── public/
│   │   │   └── fonts/
│   │   └── src/
│   │       ├── app/                           # App Router pages
│   │       │   ├── layout.tsx                 # Root layout (fonts, metadata, providers)
│   │       │   ├── globals.css                # Design tokens, Tailwind base
│   │       │   ├── (app)/                     # Authenticated app shell
│   │       │   │   ├── layout.tsx             # Sidebar + header shell
│   │       │   │   ├── page.tsx               # Landing — problem submission
│   │       │   │   ├── sessions/
│   │       │   │   │   └── page.tsx           # Session history list
│   │       │   │   └── sessions/
│   │       │   │       └── [id]/
│   │       │   │           ├── page.tsx       # Live session dashboard
│   │       │   │           └── report/
│   │       │   │               └── page.tsx   # Full exportable report
│   │       │   └── api/                       # Next.js API Routes (proxies only)
│   │       │       └── health/
│   │       │           └── route.ts
│   │       │
│   │       ├── components/
│   │       │   ├── ui/                        # shadcn/ui primitives (Button, Card, Badge…)
│   │       │   ├── layout/
│   │       │   │   ├── Sidebar.tsx
│   │       │   │   ├── Header.tsx
│   │       │   │   └── AppShell.tsx
│   │       │   └── session/
│   │       │       ├── ProblemForm.tsx        # Submission form
│   │       │       ├── CabinetGrid.tsx        # 6 minister cards (live analysis)
│   │       │       ├── MinisterCard.tsx       # Single minister — streaming text
│   │       │       ├── DebateFeed.tsx         # Chronological debate timeline
│   │       │       ├── DebateEntry.tsx        # Single argument bubble
│   │       │       ├── VotePanel.tsx          # Vote tally + confidence bars
│   │       │       ├── SimulationChart.tsx    # Radar/bar chart per option
│   │       │       ├── FinalReport.tsx        # PM synthesis reveal
│   │       │       ├── BlackSwanBadge.tsx     # Resilience score display
│   │       │       ├── PhaseTimeline.tsx      # Progress bar across phases
│   │       │       └── SessionCard.tsx        # History list item
│   │       │
│   │       ├── hooks/
│   │       │   ├── use-session-stream.ts      # SSE → Zustand bridge
│   │       │   ├── use-session.ts             # SWR fetch hook for session data
│   │       │   └── use-sessions-list.ts       # SWR fetch hook for history
│   │       │
│   │       ├── lib/
│   │       │   ├── api-client.ts              # Typed Axios wrapper
│   │       │   ├── sse-client.ts              # SSE manager with auto-reconnect
│   │       │   └── utils.ts                   # cn(), formatters, etc.
│   │       │
│   │       ├── store/
│   │       │   └── session-store.ts           # Zustand: live session + SSE state
│   │       │
│   │       └── types/
│   │           └── index.ts                   # Re-exports from @titan/shared-types
│   │
│   └── api/                                   # ── BACKEND (FastAPI + LangGraph)
│       ├── main.py                            # FastAPI app factory + middleware
│       ├── requirements.txt
│       ├── .env / .env.example
│       ├── alembic.ini
│       ├── alembic/
│       │   ├── env.py
│       │   └── versions/                      # Migration files (auto-generated)
│       │
│       └── app/
│           ├── __init__.py
│           │
│           ├── agents/                        # ── LANGGRAPH LAYER
│           │   ├── __init__.py
│           │   ├── graph.py                   # StateGraph definition + compilation
│           │   ├── nodes.py                   # All node functions (11 nodes)
│           │   ├── state.py                   # GovernanceState TypedDict
│           │   ├── prompts.py                 # Shared prompt templates
│           │   └── ministers/
│           │       ├── __init__.py            # CABINET list + MINISTER_REGISTRY
│           │       ├── base.py                # BaseMinister ABC + extract_json()
│           │       ├── ministers.py           # All 7 minister instantiations
│           │       └── simulation.py          # SimulationAgent
│           │
│           ├── api/                           # ── ROUTE LAYER
│           │   ├── __init__.py
│           │   └── v1/
│           │       ├── __init__.py
│           │       ├── router.py              # APIRouter aggregator
│           │       └── projects.py            # All endpoints (REST + SSE)
│           │
│           ├── core/                          # ── INFRASTRUCTURE
│           │   ├── config.py                  # Pydantic Settings (env vars)
│           │   ├── database.py                # Async SQLAlchemy engine + session
│           │   └── logging.py                 # Structlog configuration
│           │
│           ├── models/                        # ── ORM MODELS
│           │   └── session.py                 # Project, Agent, Debate, Vote, Simulation, FinalReport
│           │
│           ├── repositories/                  # ── DATA ACCESS LAYER
│           │   ├── __init__.py
│           │   └── project.py                 # project_repo (CRUD + report queries)
│           │
│           ├── schemas/                       # ── PYDANTIC SCHEMAS
│           │   └── session.py                 # Request/Response models for API
│           │
│           └── services/                      # ── BUSINESS LOGIC
│               ├── event_bus.py               # Async SSE pub/sub channels
│               └── session_service.py         # Orchestration: create → run → persist
│
├── packages/
│   └── shared-types/                          # ── SHARED TYPESCRIPT TYPES
│       ├── package.json
│       └── src/
│           └── index.ts                       # All interfaces + MINISTER_META
│
├── docs/
│   ├── VISION.md                              # Product vision + user journey
│   ├── ARCHITECTURE.md                        # This file
│   └── CONTRIBUTING.md
│
├── docker/
│   ├── docker-compose.yml                     # Postgres + API + Web
│   ├── Dockerfile.api                         # Python 3.12-slim multi-stage
│   └── Dockerfile.web                         # Node 20 multi-stage
│
├── turbo.json                                 # Turborepo pipeline
├── pnpm-workspace.yaml
├── package.json                               # Root: scripts + devDependencies
├── tsconfig.base.json
└── titan.code-workspace
```

---

## 2. Frontend Architecture

### 2.1 Technology Decisions

| Layer | Choice | Reason |
|---|---|---|
| Framework | Next.js 15 (App Router) | RSC + streaming, layouts, file-based routing |
| Styling | Tailwind CSS v4 | Utility-first; zero runtime CSS |
| Components | shadcn/ui | Accessible, unstyled, composable primitives |
| Animation | Framer Motion | Smooth phase transitions, card animations |
| Charts | Recharts | Radar charts (simulation), bar charts (votes) |
| State | Zustand | Minimal, async-safe client state |
| Data Fetching | SWR | Auto-revalidation for history and reports |
| Realtime | Custom SSE client | Native browser EventSource + reconnect logic |
| Icons | Lucide React | Consistent icon set |
| Notifications | Sonner | Toast system |
| HTTP | Axios | Typed API client |

### 2.2 Page Map

```
/                           Landing page + problem submission form
/sessions                   History list (paginated, searchable)
/sessions/[id]              Live session dashboard (SSE-driven)
/sessions/[id]/report       Full exportable policy report
```

### 2.3 Component Hierarchy

```
AppShell
├── Sidebar
│   ├── Logo (TITAN wordmark)
│   ├── NavItem: Home (/)
│   ├── NavItem: Sessions (/sessions)
│   └── NewSessionButton
│
├── Header
│   └── SessionStatusBadge (phase indicator)
│
└── Page Content
    │
    ├── [/] ProblemForm
    │   ├── Textarea (problem input)
    │   ├── Textarea (context, optional)
    │   └── SubmitButton → POST /api/v1/sessions → redirect to /sessions/[id]
    │
    ├── [/sessions] SessionList
    │   └── SessionCard × N
    │       ├── StatusBadge (pending | analyzing | … | completed | failed)
    │       ├── ProblemPreview (truncated)
    │       ├── CreatedAt
    │       └── Link → /sessions/[id]
    │
    ├── [/sessions/[id]] LiveDashboard
    │   ├── PhaseTimeline (0–6 phase progress bar)
    │   ├── CabinetGrid
    │   │   └── MinisterCard × 6
    │   │       ├── MinisterAvatar (icon + color)
    │   │       ├── StreamingText (analysis text, streams via SSE)
    │   │       ├── KeyFindings (pill list)
    │   │       └── ProposedSolutions (pill list)
    │   ├── DebateFeed (appears after Phase 1 complete)
    │   │   └── DebateEntry × N
    │   │       ├── MinisterTag + phase label
    │   │       └── ArgumentText
    │   ├── VotePanel (appears after Phase 3 complete)
    │   │   ├── WinnerBanner
    │   │   ├── VoteBar × 6 (minister → option → confidence)
    │   │   └── ConsensusBadge (low / moderate / high)
    │   ├── SimulationChart (appears after Phase 4 complete)
    │   │   ├── RadarChart (economic / social / env / feasibility per option)
    │   │   └── SimulationCard × 4 (future A/B/C/D scores)
    │   └── FinalReport (appears after Phase 5 complete)
    │       ├── ExecutiveSummary
    │       ├── ChosenOption + Rationale
    │       ├── ImplementationTimeline (phase steps)
    │       ├── SuccessMetrics table
    │       ├── RisksAndMitigations table
    │       └── BlackSwanBadge (crisis + resilience score)
    │
    └── [/sessions/[id]/report] FullReport
        └── (Same components as above, but static — no SSE)
            + PrintButton / ExportButton
```

### 2.4 State Management

```
Zustand Session Store (session-store.ts)
│
├── sessionId: string
├── status: SessionStatus
├── analyses: MinisterAnalysis[]       ← populated by analysis_complete events
├── debateArguments: DebateArgument[]  ← populated by debate_argument events
├── votes: Vote[]                      ← populated by vote_cast events
├── voteTally: Record<string, number>  ← populated by voting_complete event
├── simulationResults: SimulationResult[] ← populated by simulation_result events
├── finalPolicy: FinalPolicy | null    ← populated by synthesis_complete event
├── blackSwan: BlackSwanResult | null  ← populated by session_complete event
├── currentPhase: SessionStatus
└── error: string | null

Actions:
  setSession()
  handleSSEEvent(event: SSEEvent)  ← single dispatcher for all SSE events
  reset()
```

### 2.5 SSE Client Architecture

```typescript
// sse-client.ts
class SSEClient {
  private source: EventSource | null = null
  private reconnectDelay = 1000
  private maxReconnects = 5

  connect(projectId: string, onEvent: (e: SSEEvent) => void): void
  disconnect(): void
  private reconnect(): void  // exponential backoff
}

// use-session-stream.ts (React hook)
function useSessionStream(projectId: string) {
  // 1. Creates SSEClient instance
  // 2. On each event → calls store.handleSSEEvent(event)
  // 3. On session_complete or error → disconnects
  // 4. Cleans up on unmount
}
```

### 2.6 API Client

```typescript
// api-client.ts
const api = axios.create({ baseURL: process.env.NEXT_PUBLIC_API_URL })

export const titanAPI = {
  createSession: (req: CreateSessionRequest) => api.post<CreateProjectResponse>('/api/v1/sessions', req),
  listSessions:  (page: number)              => api.get<PaginatedResponse<Session>>('/api/v1/sessions', { params: { page } }),
  getSession:    (id: string)                => api.get<Session>(`/api/v1/sessions/${id}`),
  getReport:     (id: string)                => api.get<SessionReport>(`/api/v1/sessions/${id}/report`),
  getDebateHistory: (id: string)            => api.get<DebateArgument[]>(`/api/v1/sessions/${id}/debate-history`),
  streamUrl:     (id: string)               => `${process.env.NEXT_PUBLIC_API_URL}/api/v1/sessions/${id}/stream`,
}
```

---

## 3. Backend Architecture

### 3.1 Technology Decisions

| Layer | Choice | Reason |
|---|---|---|
| Framework | FastAPI | Async-native, auto OpenAPI docs, Pydantic v2 |
| Agent Orchestration | LangGraph | StateGraph with typed state, parallel Send fan-out |
| LLM Client | LangChain Google GenAI | Official Gemini integration with async support |
| ORM | SQLAlchemy 2.x (async) | Fully async, typed, Alembic-compatible |
| Migrations | Alembic | Auto-generate from ORM, versioned |
| Validation | Pydantic v2 | Request/response schemas + settings |
| Logging | Structlog | Structured JSON logs, per-request context |
| Realtime | Server-Sent Events | Native HTTP; no WebSocket infrastructure |

### 3.2 Layer Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│  API Layer  (app/api/v1/projects.py)                        │
│  • Route definitions (REST + SSE)                           │
│  • Request validation (Pydantic)                            │
│  • Response serialisation                                   │
│  • Background task dispatch                                 │
└────────────────────────┬────────────────────────────────────┘
                         │ calls
┌────────────────────────▼────────────────────────────────────┐
│  Service Layer  (app/services/session_service.py)           │
│  • Business orchestration: create → run → persist           │
│  • Coordinates: graph execution + DB writes + event publish │
│  • Does NOT contain query logic (that's repositories)       │
└──────────┬───────────────────────────────────┬──────────────┘
           │ calls                             │ calls
┌──────────▼──────────────┐       ┌────────────▼─────────────┐
│  Repository Layer        │       │  Agent Layer             │
│  (app/repositories/)     │       │  (app/agents/)           │
│  • All SQL queries        │       │  • LangGraph graph       │
│  • Typed return values    │       │  • Minister nodes        │
│  • No business logic      │       │  • State management      │
└──────────┬──────────────┘       └────────────┬─────────────┘
           │                                    │
┌──────────▼──────────────────────────────────▼───────────────┐
│  Infrastructure Layer                                        │
│  • core/database.py    — Async engine, session factory       │
│  • core/config.py      — Pydantic Settings (env vars)        │
│  • core/logging.py     — Structlog setup                     │
│  • services/event_bus.py — In-process SSE pub/sub           │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 FastAPI Application Factory (`main.py`)

```
FastAPI app
├── CORSMiddleware (allow frontend origin)
├── Lifespan context manager
│   ├── on startup: create DB tables (or run Alembic)
│   └── on shutdown: close engine
├── /api/v1 router (projects.py)
└── /docs, /redoc (auto-generated)
```

### 3.4 Async Request Lifecycle

```
POST /api/v1/sessions
       │
       ▼
  FastAPI route handler
       │
       ├── validate request (Pydantic)
       ├── SessionService.create_project() → INSERT projects row → return project.id
       ├── background_tasks.add_task(service.run_agent_graph, project_id)
       └── return 201 { project_id, status: "pending", message }

  [Background Task — asyncio coroutine]
       │
       ├── update status → ANALYZING
       ├── publish SSE: session_started
       ├── graph.ainvoke(initial_state)
       │       │
       │       └── [LangGraph runs all nodes...]
       │
       ├── _persist_state() → bulk INSERT agents, debates, votes, simulations, final_report
       ├── update status → COMPLETED
       └── publish SSE: session_complete

GET /api/v1/sessions/{id}/stream
       │
       ▼
  StreamingResponse(event_generator())
       │
       └── event_bus.subscribe(project_id)
               │
               └── yields SSE lines as graph publishes events
```

### 3.5 EventBus Architecture

```python
class EventBus:
    # project_id → asyncio.Queue[dict]
    _queues: Dict[str, asyncio.Queue]

    async def publish(project_id, event_type, data) → None
        # Puts event onto queue; non-blocking

    async def subscribe(project_id) → AsyncGenerator[dict, None]
        # Yields events from queue; drives SSE response

    async def close_session(project_id) → None
        # Signals end sentinel; cleans up queue
```

**Key property:** In-process pub/sub — zero external dependencies. Sufficient for single-process deployment (hackathon + MVP). Scale path: swap for Redis Streams.

### 3.6 Configuration (`core/config.py`)

```python
class Settings(BaseSettings):
    # Required
    GEMINI_API_KEY: str

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://titan:titanpass@localhost:5432/titan_db"

    # Models
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"   # Ministers + Simulation
    GEMINI_PRO_MODEL:   str = "gemini-1.5-pro"     # Prime Minister synthesis

    # Agent Behaviour
    DEBATE_ROUNDS:           int   = 2
    MAX_SIMULATION_OPTIONS:  int   = 3
    AGENT_TIMEOUT_SECONDS:   int   = 120

    # API
    API_VERSION:   str  = "1.0.0"
    ENVIRONMENT:   str  = "development"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY)
```

---

## 4. Database Design

### 4.1 Entity Relationship Diagram

```
┌─────────────────┐
│    projects     │  1 governance run
│─────────────────│
│ id        UUID PK│────────────────────────────────────┐
│ title     TEXT   │                                    │
│ problem   TEXT   │                                    │
│ context   TEXT   │                                    │
│ status    ENUM   │ (pending→analyzing→…→completed)    │
│ error_msg TEXT   │                                    │
│ metadata  JSONB  │                                    │
│ created_at TS    │                                    │
│ completed_at TS  │                                    │
└────────┬────────┘                                    │
         │ 1                                            │
         │                                             │
    ┌────▼────────────────────────────────────────┐    │
    │  agents (minister analyses)                  │    │
    │  1 row per minister × project (6 rows)       │    │
    │─────────────────────────────────────────────│    │
    │  id           UUID PK                        │    │
    │  project_id   UUID FK → projects.id          │    │
    │  role         ENUM (7 minister roles)         │    │
    │  model_used   TEXT                           │    │
    │  analysis     TEXT (situation assessment)     │    │
    │  key_points   JSONB  List[str]               │    │
    │  proposed_solutions JSONB List[str]           │    │
    │  concerns     JSONB  List[str]               │    │
    │  tokens_used  INT                            │    │
    │  processing_ms INT                           │    │
    │  created_at   TS                             │    │
    │  UNIQUE(project_id, role)                    │    │
    └──┬──────────────────────────────────────────┘    │
       │ 1                                              │
       │                                               │
  ┌────▼────────────────────────────────────┐          │
  │  debates (all debate phases)             │          │
  │  phase: presentation|debate|            │          │
  │         opposition_attack|rebuttal      │          │
  │─────────────────────────────────────────│          │
  │  id               UUID PK               │          │
  │  project_id       UUID FK → projects    │          │
  │  agent_id         UUID FK → agents      │          │
  │  round_number     INT                   │          │
  │  phase            TEXT                  │          │
  │  argument         TEXT                  │          │
  │  supporting_agents JSONB List[str]      │          │
  │  opposing_agents  JSONB List[str]       │          │
  │  word_count       INT                   │          │
  │  created_at       TS                    │          │
  └─────────────────────────────────────────┘          │
                                                        │
  ┌─────────────────────────────────────────┐          │
  │  votes (democratic votes)               │          │
  │  1 vote per minister per project        │          │
  │─────────────────────────────────────────│          │
  │  id               UUID PK               │          │
  │  project_id       UUID FK → projects    │◄─────────┤
  │  agent_id         UUID FK → agents      │          │
  │  voted_option     TEXT                  │          │
  │  confidence_score FLOAT (0–100)         │          │
  │  justification    TEXT                  │          │
  │  created_at       TS                    │          │
  │  UNIQUE(project_id, agent_id)           │          │
  └─────────────────────────────────────────┘          │
                                                        │
  ┌─────────────────────────────────────────┐          │
  │  simulations (stress-test results)      │          │
  │  1 row per simulated future per project │          │
  │─────────────────────────────────────────│          │
  │  id                    UUID PK          │          │
  │  project_id            UUID FK          │◄─────────┤
  │  option_name           TEXT             │          │
  │  option_description    TEXT             │          │
  │  economic_score        FLOAT            │          │
  │  social_score          FLOAT            │          │
  │  environmental_score   FLOAT            │          │
  │  feasibility_score     FLOAT            │          │
  │  composite_score       FLOAT            │          │
  │  risk_level            ENUM             │          │
  │  time_to_implement_months INT           │          │
  │  cost_estimate_usd_millions FLOAT       │          │
  │  projected_population_impact FLOAT      │          │
  │  key_risks             JSONB List[str]  │          │
  │  key_benefits          JSONB List[str]  │          │
  │  scenario_data         JSONB            │          │
  │  created_at            TS               │          │
  └─────────────────────────────────────────┘          │
                                                        │
  ┌─────────────────────────────────────────┐          │
  │  final_reports (PM synthesis, 1:1)      │          │
  │─────────────────────────────────────────│          │
  │  id                    UUID PK          │          │
  │  project_id            UUID FK UNIQUE   │◄─────────┘
  │  chosen_option         TEXT             │
  │  executive_summary     TEXT             │
  │  overall_rationale     TEXT             │
  │  confidence_score      FLOAT            │
  │  implementation_steps  JSONB            │
  │  success_metrics       JSONB            │
  │  risks_and_mitigations JSONB            │
  │  expected_outcomes     JSONB            │
  │  review_timeline       TEXT             │
  │  total_votes           INT              │
  │  winning_votes         INT              │
  │  vote_percentage       FLOAT            │
  │  consensus_level       TEXT             │
  │  best_simulation_score FLOAT            │
  │  black_swan_crisis     TEXT             │
  │  black_swan_impact     TEXT             │
  │  resilience_score      FLOAT            │
  │  model_used            TEXT             │
  │  created_at            TS               │
  └─────────────────────────────────────────┘
```

### 4.2 Indexes

```sql
-- projects
CREATE INDEX ix_projects_status_created   ON projects(status, created_at);

-- agents
CREATE INDEX ix_agents_project_role        ON agents(project_id, role);
CREATE UNIQUE INDEX uq_agents_project_role ON agents(project_id, role);

-- debates
CREATE INDEX ix_debates_project_round      ON debates(project_id, round_number);

-- votes
CREATE INDEX ix_votes_project_option       ON votes(project_id, voted_option);
CREATE UNIQUE INDEX uq_votes_project_agent ON votes(project_id, agent_id);

-- simulations
CREATE INDEX ix_simulations_project_comp   ON simulations(project_id, composite_score);

-- final_reports
CREATE UNIQUE INDEX uq_final_reports_project ON final_reports(project_id);
```

### 4.3 Cascade Strategy

All child tables use `ON DELETE CASCADE` from `projects.id`. Deleting a project removes all of its analyses, debates, votes, simulations, and the final report atomically.

### 4.4 JSONB Fields (Schema Contracts)

| Table | Column | Shape |
|---|---|---|
| `agents` | `key_points` | `string[]` |
| `agents` | `proposed_solutions` | `string[]` |
| `agents` | `concerns` | `string[]` |
| `simulations` | `key_risks` | `string[]` |
| `simulations` | `key_benefits` | `string[]` |
| `simulations` | `scenario_data` | `{ future: string, score: number, narrative: string }[]` |
| `final_reports` | `implementation_steps` | `PolicyStep[]` |
| `final_reports` | `success_metrics` | `{ metric: string, target: string, deadline: string }[]` |
| `final_reports` | `risks_and_mitigations` | `Record<string, string>` |
| `final_reports` | `expected_outcomes` | `string[]` |
| `projects` | `metadata_` | `{ started_at, completed_at, cabinet_size, ... }` |

---

## 5. Agent Workflow

### 5.1 LangGraph StateGraph

```
GovernanceState flows through 11 nodes:

input_validation
     │
     ├─[failed]──────────────────────────── error_handler ──► END
     │
     └─[analyzing]── route_to_ministers ──► Send × 6 (parallel fan-out)
                                              │
                     ┌────────────────────────┤
                     │  minister_analysis     │ (×6 parallel)
                     │  economic_minister     │
                     │  technology_minister   │
                     │  infrastructure_minister│
                     │  citizen_minister      │
                     │  environment_minister  │
                     │  opposition_minister   │
                     └────────────────────────┤
                                              │ Annotated[List, operator.add]
                     aggregate_analyses ◄─────┘
                          │
                          │ (extracts policy_options list)
                          │
                     debate_round ◄── 5 ministers sequential (can see prior args)
                          │
                     opposition_attack ◄── dedicated attack on all proposals
                          │
                     rebuttal_round ◄── 5 ministers parallel (independent rebuttals)
                          │
                     route_to_voting ──► Send × 6 (parallel fan-out)
                                              │
                     ┌────────────────────────┤
                     │  minister_vote × 6     │ (parallel)
                     └────────────────────────┤
                                              │ Annotated[List, operator.add]
                     tally_votes ◄────────────┘
                          │
                     simulation_phase ◄── 4 futures in parallel (asyncio.gather)
                          │
                     prime_minister_synthesis ◄── Gemini Pro single call
                          │
                     black_swan_engine ◄── random crisis + resilience score
                          │
                          ├─[failed]──────── error_handler ──► END
                          └─[__end__]──────────────────────► END
```

### 5.2 GovernanceState Schema

```python
class GovernanceState(TypedDict):
    # Identity
    project_id:  str
    problem:     str
    context:     str

    # Phase 1 — Parallel analyses (Annotated: append-safe for fan-out)
    analyses:            Annotated[List[MinisterOutput], operator.add]

    # Phase 2 — Debate (all debate phases combined via same reducer)
    debate_arguments:    Annotated[List[DebateArgument], operator.add]
    opposition_attacks:  Annotated[List[DebateArgument], operator.add]
    rebuttals:           Annotated[List[DebateArgument], operator.add]

    # Phase 3 — Votes
    votes:               Annotated[List[VoteRecord], operator.add]

    # Derived
    policy_options:      List[str]          # extracted in aggregate_analyses
    vote_tally:          Dict[str, int]     # option → count

    # Phase 4 — Simulations (appended by simulation_phase node)
    simulation_results:  Annotated[List[Dict], operator.add]

    # Phase 5 — Final report
    final_report:        Optional[Dict[str, Any]]

    # Phase 6 — Black Swan
    black_swan_results:  Optional[Dict[str, Any]]

    # Control
    current_phase:       str
    error:               Optional[str]
    metadata:            Dict[str, Any]     # timing, token counts, etc.
```

### 5.3 Minister Base Class

```python
class BaseMinister(ABC):
    role:          str          # e.g. "economic_minister"
    role_title:    str          # e.g. "Economic Minister"
    system_prompt: str          # injected at LLM call
    llm:           ChatGoogleGenerativeAI  # Gemini Flash

    async def analyze(problem, context) -> MinisterOutput
        # Calls LLM with analysis prompt schema
        # Returns structured MinisterOutput dict

    async def debate(problem, all_analyses, round_number, phase, prior_arguments) -> DebateArgument
        # Calls LLM with debate prompt schema
        # Returns structured DebateArgument dict

    async def vote(problem, policy_options, all_analyses, all_debates) -> VoteRecord
        # Calls LLM with vote prompt schema
        # Returns structured VoteRecord dict
```

### 5.4 Minister Personas & Constraints

| Minister | system_prompt Core Constraint | Red Lines |
|---|---|---|
| Economic | "Maximise GDP, employment, and fiscal sustainability" | Never approves policies that increase deficit > 3% GDP |
| Technology | "Advocate for digital solutions and innovation ecosystems" | Never accepts fully manual, non-digital implementations |
| Infrastructure | "Assess physical feasibility and cost-effectiveness" | Never supports unfunded infrastructure mandates |
| Citizen | "Centre every decision on human welfare and equity" | Never accepts solutions that disproportionately harm vulnerable groups |
| Environment | "Reject any proposal that worsens ecological outcomes" | Never endorses carbon-positive strategies |
| Opposition | "Challenge every proposal. Find every flaw." | Cannot vote FOR the status quo or the leading proposal without strong evidence |
| Prime Minister | "Synthesise all perspectives into a nationally defensible policy" | Must acknowledge all minister dissents in final report |
| Simulation | "Generate numerical scores based on evidence, not politics" | No political affiliation; scores only |

### 5.5 Simulation Engine (4 Futures)

```
For the winning policy option, the Simulation Agent runs 4 parallel scenarios:

Future A — Optimistic      (best-case: high adoption, stable economy, political will)
Future B — Pessimistic     (worst-case: low adoption, economic downturn, resistance)
Future C — Tech-Driven     (accelerated technology deployment, high automation)
Future D — Resource-Constrained (budget cuts, supply chain issues, reduced capacity)

Each future scores:
  economic_score        0–100
  social_score          0–100
  environmental_score   0–100
  feasibility_score     0–100
  composite_score       weighted average (equal weights, MVP)
  risk_level            low | medium | high | critical
  time_to_implement_months
  cost_estimate_usd_millions
  projected_population_impact  (millions)
  key_risks             List[str]
  key_benefits          List[str]
```

### 5.6 Black Swan Engine

```
After PM synthesis, a random catastrophic crisis is selected:

  • Global Economic Recession (-15% GDP)
  • Global Pandemic (30% workforce impact)
  • Catastrophic 500-Year Flood
  • Severe Supply Chain Shortage
  • Massive Political Unrest

The Simulation Agent evaluates:
  • How does the chosen strategy survive this crisis?
  • What breaks first?
  • resilience_score: 0–100
  • black_swan_impact: 3-sentence narrative

Output stored in final_reports (black_swan_crisis, black_swan_impact, resilience_score).
```

---

## 6. API Structure

### 6.1 Base URL

```
http://localhost:8000   (development)
https://api.titan.app   (production)
```

### 6.2 All Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | None | Health check (DB + Gemini status) |
| `POST` | `/api/v1/sessions` | None | Create session + start agent graph |
| `GET` | `/api/v1/sessions` | None | List sessions (paginated) |
| `GET` | `/api/v1/sessions/{id}` | None | Get session status |
| `GET` | `/api/v1/sessions/{id}/stream` | None | **SSE** — real-time event stream |
| `GET` | `/api/v1/sessions/{id}/report` | None | Full policy report (all phases) |
| `GET` | `/api/v1/sessions/{id}/debate-history` | None | Chronological debate for replay |

### 6.3 Request / Response Contracts

#### `POST /api/v1/sessions`

```json
// Request
{
  "problem": "India's urban unemployment has hit 35% due to AI automation",
  "context": "Focus on Tier-2 cities. Budget ceiling: $5B over 5 years."  // optional
}

// Response 201
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Cabinet session initiated. Ministers are assembling..."
}
```

#### `GET /api/v1/sessions`

```json
// Response 200
{
  "items": [
    {
      "id": "550e8400...",
      "title": "India's urban unemployment has hit 35%…",
      "problem": "India's urban unemployment...",
      "status": "completed",
      "created_at": "2026-06-13T06:00:00Z",
      "completed_at": "2026-06-13T06:04:30Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "has_next": true
}
```

#### `GET /api/v1/sessions/{id}/stream` — SSE Events

```
Content-Type: text/event-stream

data: {"event":"session_started","data":{"project_id":"..."},"timestamp":"..."}

data: {"event":"analysis_complete","data":{"minister_role":"economic_minister","situation_assessment":"...","key_findings":[...],...},"timestamp":"..."}

data: {"event":"debate_argument","data":{"agent_role":"technology_minister","phase":"debate","round_number":1,"argument":"..."},"timestamp":"..."}

data: {"event":"vote_cast","data":{"agent_role":"citizen_minister","voted_option":"Option A","confidence_score":78,"justification":"..."},"timestamp":"..."}

data: {"event":"simulation_result","data":{"option_name":"Option A","future_name":"Future A (Optimistic)","composite_score":82,...},"timestamp":"..."}

data: {"event":"session_complete","data":{"project_id":"...","final_report":{...}},"timestamp":"..."}
```

#### `GET /api/v1/sessions/{id}/report`

```json
// Response 200
{
  "project": { "id": "...", "status": "completed", ... },
  "agents": [
    {
      "role": "economic_minister",
      "analysis": "...",
      "key_points": ["..."],
      "proposed_solutions": ["..."],
      "concerns": ["..."]
    }
  ],
  "debates": [
    { "round_number": 1, "phase": "debate", "agent_id": "...", "argument": "..." }
  ],
  "votes": [
    { "agent_id": "...", "voted_option": "Option A", "confidence_score": 82, "justification": "..." }
  ],
  "simulations": [
    {
      "option_name": "Option A",
      "economic_score": 78,
      "social_score": 85,
      "environmental_score": 70,
      "feasibility_score": 65,
      "composite_score": 74.5,
      "risk_level": "medium"
    }
  ],
  "final_report": {
    "chosen_option": "Option A",
    "executive_summary": "...",
    "overall_rationale": "...",
    "confidence_score": 84,
    "implementation_steps": [...],
    "success_metrics": [...],
    "risks_and_mitigations": {...},
    "expected_outcomes": [...],
    "review_timeline": "Quarterly for 2 years, then annual",
    "total_votes": 6,
    "vote_percentage": 83.3,
    "consensus_level": "high",
    "black_swan_crisis": "Global Pandemic (Lockdowns, 30% workforce impact)",
    "black_swan_impact": "...",
    "resilience_score": 71.5
  }
}
```

#### `GET /api/v1/health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected",
  "gemini_configured": true
}
```

### 6.4 Error Responses

```json
// 404
{ "detail": "Project 550e8400... not found" }

// 422 — Pydantic validation failure
{
  "detail": [
    { "loc": ["body", "problem"], "msg": "field required", "type": "missing" }
  ]
}

// 500
{ "detail": "Internal server error" }
```

### 6.5 API Versioning Strategy

- Current: `/api/v1/`
- All endpoints are versioned at the prefix level
- Breaking changes → `/api/v2/` alongside v1 (deprecation window: 60 days)
- Backwards-compatible changes are made in-place within the current version

---

## Appendix — Hackathon-Friendly Shortcuts

These decisions reduce setup complexity while preserving production patterns:

| Decision | Hackathon Choice | Production Scale Path |
|---|---|---|
| Real-time | In-process SSE EventBus | Redis Streams / Kafka |
| Auth | None (open) | Clerk / Supabase Auth |
| Database | Single PostgreSQL | Read replicas + connection pooling |
| LLM Concurrency | asyncio fan-out, no rate limiting | Token bucket rate limiter |
| Deployments | Docker Compose | Kubernetes / Cloud Run |
| Monitoring | Structlog to stdout | OpenTelemetry + Grafana |
| File exports | Not implemented | S3 + pre-signed URLs |
| Multi-tenant | Single tenant | Row-level security on all tables |

---

*TITAN — Where AI Governs, Transparently.*
