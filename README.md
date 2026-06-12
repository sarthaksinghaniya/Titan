# TITAN — Autonomous Governance Intelligence Platform

<div align="center">

![TITAN](https://img.shields.io/badge/TITAN-Governance_AI-6366f1?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js_15-black?style=for-the-badge&logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain)
![Gemini](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_16-336791?style=for-the-badge&logo=postgresql)

**A production-grade multi-agent AI platform where 8 AI ministers independently analyze, debate, vote, simulate, and deliver governance policy for real-world societal problems.**

</div>

---

## What is TITAN?

TITAN (**T**ransparency **I**ntelligence **T**echnology **A**gent **N**etwork) is an autonomous governance intelligence platform. You submit a societal problem, and a full AI cabinet convenes:

1. **6 Ministers** independently analyze the problem from their domain
2. **Debate** — 2 rounds of cross-ministerial argument
3. **Vote** — each minister votes for the best policy option with justification
4. **Simulation** — AI stress-tests top policy options with synthetic data
5. **Prime Minister** synthesizes everything into a final binding policy

---

## Architecture

```
TITAN/
├── apps/
│   ├── web/                    # Next.js 15 + TypeScript + Tailwind + shadcn/ui
│   └── api/                    # FastAPI + Python 3.12 + LangGraph + Gemini
├── packages/
│   └── shared-types/           # Shared TypeScript types (mirrors Pydantic models)
├── docker/
│   ├── docker-compose.yml      # Full stack orchestration
│   ├── Dockerfile.api
│   └── Dockerfile.web
├── turbo.json                  # Turborepo pipeline
└── package.json                # Root workspace
```

## AI Cabinet

| Minister | Domain | AI Model |
|---|---|---|
| 👑 Prime Minister | Final synthesis & decision | Gemini 1.5 Pro |
| 📈 Economic Minister | GDP, employment, fiscal policy | Gemini 1.5 Flash |
| 💻 Technology Minister | Innovation, digital infrastructure | Gemini 1.5 Flash |
| 🏗️ Infrastructure Minister | Roads, energy, water, logistics | Gemini 1.5 Flash |
| 👥 Citizen Minister | Social equity, welfare, community | Gemini 1.5 Flash |
| 🌿 Environment Minister | Climate, sustainability, ecology | Gemini 1.5 Flash |
| 🛡️ Opposition Minister | Critical challenger, risk identifier | Gemini 1.5 Flash |
| 🔬 Simulation Agent | Synthetic policy stress-testing | Gemini 1.5 Flash |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS v4, shadcn/ui |
| Backend | FastAPI, Python 3.12, async SQLAlchemy |
| AI Agents | LangGraph, LangChain, Google Gemini AI |
| Database | PostgreSQL 16 |
| Realtime | Server-Sent Events (SSE) |
| Container | Docker + Docker Compose |
| Monorepo | Turborepo + pnpm |

---

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+ (or Docker)
- pnpm 9+
- A Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Clone and Install

```bash
git clone <repo-url>
cd TITAN
pnpm install
```

### 2. Configure Environment

```bash
# Frontend
cp apps/web/.env.local apps/web/.env.local
# Edit NEXT_PUBLIC_API_URL if needed

# Backend
cp apps/api/.env.example apps/api/.env
# Edit apps/api/.env and set your GEMINI_API_KEY
```

### 3. Start with Docker (Recommended)

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 3. Or Start Manually

```bash
# Terminal 1: Start the database (if using Docker for just Postgres)
docker run -d -p 5432:5432 -e POSTGRES_USER=titan -e POSTGRES_PASSWORD=titanpass -e POSTGRES_DB=titan_db postgres:16-alpine

# Terminal 2: Start the API
cd apps/api
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 3: Start the web app
pnpm --filter web dev
```

### 4. Open the App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/sessions` | Create a new governance session |
| `GET` | `/api/v1/sessions` | List all sessions (paginated) |
| `GET` | `/api/v1/sessions/{id}` | Get session details |
| `GET` | `/api/v1/sessions/{id}/stream` | SSE stream of agent activity |
| `GET` | `/api/v1/sessions/{id}/report` | Full policy report |
| `GET` | `/api/v1/health` | System health check |

---

## Milestones

- [x] **Milestone 1**: Project Foundation & Monorepo Setup
- [ ] **Milestone 2**: Database Layer & Seeding
- [ ] **Milestone 3**: Agent Graph (Backend Core)
- [ ] **Milestone 4**: Frontend Core
- [ ] **Milestone 5**: Live Dashboard
- [ ] **Milestone 6**: Production Polish

---

## Environment Variables

### Backend (`apps/api/.env`)

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | **Required** — Your Gemini API key | — |
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://titan:titanpass@localhost:5432/titan_db` |
| `GEMINI_FLASH_MODEL` | Model for minister agents | `gemini-1.5-flash` |
| `GEMINI_PRO_MODEL` | Model for Prime Minister synthesis | `gemini-1.5-pro` |
| `DEBATE_ROUNDS` | Number of debate rounds | `2` |
| `MAX_SIMULATION_OPTIONS` | Options to simulate | `3` |

### Frontend (`apps/web/.env.local`)

| Variable | Description | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |

---

## License

MIT — Built for educational and research purposes.
