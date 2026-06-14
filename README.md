<div align="center">

<br />

```
████████╗██╗████████╗ █████╗ ███╗   ██╗
╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║
   ██║   ██║   ██║   ███████║██╔██╗ ██║
   ██║   ██║   ██║   ██╔══██║██║╚██╗██║
   ██║   ██║   ██║   ██║  ██║██║ ╚████║
   ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝
```

### Autonomous Governance Intelligence Platform

*Where AI Ministers Debate, Vote, and Govern*

<br />

[![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/Gemini_AI-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-336791?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript_5-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com/)

<br />

[**Live Demo**](#) · [**API Docs**](http://localhost:8000/docs) · [**Report Bug**](#) · [**Request Feature**](#)

</div>

---

## 📖 Overview

**TITAN V3** (*Transparency Intelligence Technology Agent Network*) is a production-grade autonomous evidence-driven governance intelligence platform. Submit any societal problem — water scarcity, unemployment, pollution — and a full AI Cabinet convenes to deliver a comprehensive, debate-tested policy recommendation backed by real-world RAG evidence, semantic contradiction detection, and scenario impact forecasting.

```
You: "India's urban unemployment has hit 35% due to AI automation"
                              │
               ┌──────────────▼──────────────┐
               │   TITAN Governance Cabinet   │
               └──────────────┬──────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
    📈 Economic         💻 Technology       🏗️ Infrastructure
    Minister            Minister            Minister
    (Analysis)          (Analysis)          (Analysis)
          │                   │                   │
     👥 Citizen         🌿 Environment      🛡️ Opposition
     Minister           Minister            Minister
     (Analysis)         (Analysis)          (Critique)
          │
          └────────────── DEBATE (2 rounds) ──────────────┐
                                                           │
                              VOTE (6 ministers) ──────────┤
                                                           │
                          SIMULATION (stress test) ────────┤
                                                           │
                         👑 PRIME MINISTER synthesis ──────┘
                                    │
                           📋 Final Policy Report
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **8 AI Agents** | Each minister has a unique persona, expertise, and decision bias |
| ⚡ **Parallel Analysis** | All 6 ministers analyze simultaneously — no waiting in queues |
| 🗣️ **Multi-Round Debate** | Ministers argue, counter-argue, and refine positions |
| 🗳️ **Democratic Voting** | Each minister votes with confidence score and justification |
| 🔬 **Synthetic Simulation** | AI stress-tests top policy options across 5 scenarios |
| 📡 **Live Streaming** | Watch the debate unfold in real-time via Server-Sent Events |
| 💾 **Full Persistence** | Every analysis, argument, vote, and simulation is stored |
| 🐳 **Docker Ready** | One command to start the entire stack |

---

## 🏛️ The AI Cabinet

| Minister | Domain | Model | Personality |
|---|---|---|---|
| 👑 **Prime Minister** | Final synthesis | Gemini 1.5 Pro | Strategic, balanced, decisive |
| 📈 **Economic Minister** | GDP, employment, fiscal policy | Gemini Flash | Growth-oriented, data-driven |
| 💻 **Technology Minister** | Innovation, digital infrastructure | Gemini Flash | Tech-optimist, future-focused |
| 🏗️ **Infrastructure Minister** | Roads, energy, water | Gemini Flash | Pragmatic, cost-conscious |
| 👥 **Citizen Minister** | Social equity, welfare | Gemini Flash | People-first, equity-driven |
| 🌿 **Environment Minister** | Climate, sustainability | Gemini Flash | Conservation-focused |
| 🛡️ **Opposition Minister** | Critical challenger | Gemini Flash | Contrarian, risk-focused |
| 🔬 **Simulation Agent** | Synthetic stress testing | Gemini Flash | Data-driven, analytical |

---

## 🗂️ Project Structure

```
TITAN/
├── apps/
│   ├── web/                          # Next.js 15 Frontend
│   │   ├── src/
│   │   │   ├── app/                  # App Router pages
│   │   │   │   ├── (app)/            # Main app layout group
│   │   │   │   │   ├── page.tsx      # Landing + problem submission
│   │   │   │   │   ├── sessions/     # Session history
│   │   │   │   │   └── sessions/[id] # Live session dashboard
│   │   │   │   ├── layout.tsx        # Root layout
│   │   │   │   └── globals.css       # Design system
│   │   │   ├── components/
│   │   │   │   ├── ui/               # Base UI primitives
│   │   │   │   ├── layout/           # Sidebar, Header
│   │   │   │   └── session/          # Session-specific components
│   │   │   ├── lib/
│   │   │   │   ├── api-client.ts     # Typed Axios client
│   │   │   │   ├── sse-client.ts     # SSE connection manager
│   │   │   │   └── utils.ts          # Utilities
│   │   │   └── store/
│   │   │       └── session-store.ts  # Zustand state
│   │   ├── components.json           # shadcn/ui config
│   │   └── package.json
│   │
│   └── api/                          # FastAPI Backend
│       ├── app/
│       │   ├── agents/
│       │   │   ├── graph.py          # LangGraph governance graph ⭐
│       │   │   ├── prompts.py        # Minister system prompts
│       │   │   └── state.py          # Shared state TypedDict
│       │   ├── api/v1/
│       │   │   └── sessions.py       # REST + SSE endpoints
│       │   ├── core/
│       │   │   ├── config.py         # Pydantic Settings
│       │   │   ├── database.py       # Async SQLAlchemy
│       │   │   └── logging.py        # Structlog
│       │   ├── models/
│       │   │   └── session.py        # SQLAlchemy ORM models
│       │   ├── schemas/
│       │   │   └── session.py        # Pydantic schemas
│       │   └── services/
│       │       ├── event_bus.py      # Async SSE pub/sub
│       │       └── session_service.py# Session orchestration
│       ├── alembic/                  # Database migrations
│       ├── main.py                   # FastAPI app factory
│       └── requirements.txt
│
├── packages/
│   └── shared-types/                 # Shared TypeScript types
│       └── src/index.ts              # All interfaces + MINISTER_META
│
├── docker/
│   ├── docker-compose.yml            # Full stack (Postgres + API + Web)
│   ├── Dockerfile.api                # Python 3.12 slim
│   └── Dockerfile.web                # Node 20 multi-stage
│
├── turbo.json                        # Turborepo pipeline
├── pnpm-workspace.yaml               # pnpm workspace config
├── titan.code-workspace              # VS Code multi-root workspace
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Install |
|---|---|---|
| Node.js | ≥ 20.0 | [nodejs.org](https://nodejs.org/) |
| pnpm | ≥ 9.0 | `npm install -g pnpm` |
| Python | 3.12 | [python.org](https://python.org/) |
| Docker | Latest | [docker.com](https://docker.com/) |
| Gemini API Key | — | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

### Option A — Docker (Recommended)

```bash
# 1. Clone
git clone https://github.com/your-org/titan.git
cd TITAN

# 2. Configure environment
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env — set GEMINI_API_KEY

# 3. Start everything
docker compose -f docker/docker-compose.yml up -d

# 4. Open
open http://localhost:3000          # Frontend
open http://localhost:8000/docs     # API Docs
```

### Option B — Manual Setup

```bash
# 1. Clone and install frontend dependencies
git clone https://github.com/your-org/titan.git
cd TITAN
pnpm install

# 2. Set up Python backend
cd apps/api
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set GEMINI_API_KEY

# 4. Start PostgreSQL
docker run -d \
  --name titan-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=titan \
  -e POSTGRES_PASSWORD=titanpass \
  -e POSTGRES_DB=titan_db \
  postgres:16-alpine

# 5. Start the API (from apps/api)
uvicorn main:app --reload --port 8000

# 6. Start the web (from project root, new terminal)
pnpm --filter web dev
```

### Access

| Service | URL |
|---|---|
| 🌐 Frontend | http://localhost:3000 |
| 📡 API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |
| 🔍 Health | http://localhost:8000/api/v1/health |

---

## 🔌 API Reference

### Sessions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/sessions` | Create session & start agent pipeline |
| `GET` | `/api/v1/sessions` | List sessions (paginated) |
| `GET` | `/api/v1/sessions/{id}` | Get session status |
| `GET` | `/api/v1/sessions/{id}/stream` | **SSE** — live agent stream |
| `GET` | `/api/v1/sessions/{id}/report` | Full policy report |

### Example

```bash
# Create a session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"problem": "Urban flooding affects 10 million residents annually"}'

# Stream live updates
curl -N http://localhost:8000/api/v1/sessions/{id}/stream
```

---

## ⚙️ Environment Variables

### Backend (`apps/api/.env`)

```env
# Required
GEMINI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql+asyncpg://titan:titanpass@localhost:5432/titan_db

# Models
GEMINI_FLASH_MODEL=gemini-1.5-flash    # Ministers
GEMINI_PRO_MODEL=gemini-1.5-pro        # Prime Minister

# Agent Behavior
DEBATE_ROUNDS=2
MAX_SIMULATION_OPTIONS=3
AGENT_TIMEOUT_SECONDS=120
```

### Frontend (`apps/web/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🛠️ Development Commands

```bash
# ─── Root (Turborepo) ─────────────────────────────────────────
pnpm dev              # Start all apps in dev mode
pnpm build            # Build all apps
pnpm lint             # Lint all apps
pnpm typecheck        # TypeScript check all apps

# ─── Frontend only ────────────────────────────────────────────
pnpm --filter web dev
pnpm --filter web build
pnpm --filter web lint

# ─── Backend only ─────────────────────────────────────────────
cd apps/api
uvicorn main:app --reload --port 8000
pytest tests/                    # Run tests
alembic revision --autogenerate -m "description"  # New migration
alembic upgrade head              # Apply migrations

# ─── Docker ───────────────────────────────────────────────────
docker compose -f docker/docker-compose.yml up -d     # Start all
docker compose -f docker/docker-compose.yml down      # Stop all
docker compose -f docker/docker-compose.yml logs -f   # Logs
```

---

## 🗄️ Database Schema

```sql
sessions               — Governance sessions (problem → status → completion)
minister_analyses      — Each minister's independent analysis
debate_rounds          — Structured arguments per round per minister
votes                  — Minister votes with confidence scores
simulation_results     — Synthetic stress-test scores per policy option
final_policies         — Prime Minister's final policy recommendation
```

---

## 📊 Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 15 | React framework with App Router |
| TypeScript 5 | Type safety |
| Tailwind CSS v4 | Utility-first styling |
| shadcn/ui | Accessible UI primitives |
| Zustand | Client state management |
| Framer Motion | Animations |
| Recharts | Data visualization |
| Lucide Icons | Icon system |
| Sonner | Toast notifications |

### Backend
| Technology | Purpose |
|---|---|
| FastAPI | Async REST API |
| LangGraph | Multi-agent state graph |
| LangChain | LLM orchestration |
| Google Gemini | AI models (Flash + Pro) |
| SQLAlchemy (async) | ORM |
| Alembic | Database migrations |
| PostgreSQL 16 | Primary database |
| Pydantic v2 | Data validation |
| Structlog | Structured logging |

### Infrastructure
| Technology | Purpose |
|---|---|
| Docker + Compose | Container orchestration |
| Turborepo | Monorepo build system |
| pnpm | Package management |
| Server-Sent Events | Real-time streaming |

---

## 🗺️ Roadmap

- [x] **Milestone 1** — Project Foundation & Monorepo Setup
- [ ] **Milestone 2** — Database migrations + 10 sample problem datasets
- [ ] **Milestone 3** — Full agent graph execution + SSE streaming
- [ ] **Milestone 4** — Frontend core (live session dashboard)
- [ ] **Milestone 5** — Real-time debate visualization + charts
- [ ] **Milestone 6** — Production hardening + Docker optimization

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit with conventional commits: `git commit -m "feat: add my feature"`
4. Push: `git push origin feat/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using **Gemini AI** · **LangGraph** · **Next.js** · **FastAPI**

*TITAN — Where AI Governs, Transparently.*

</div>
