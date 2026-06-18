# TITAN — Contributing Guide

> **Build on TITAN: Add ministers, extend debates, improve governance simulation**

---

## 📋 Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Adding a Custom Minister](#adding-a-custom-minister)
4. [Extending the Debate Engine](#extending-the-debate-engine)
5. [Running Tests](#running-tests)
6. [Code Style & Standards](#code-style--standards)
7. [Submitting Changes](#submitting-changes)

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:pass@localhost/titan_db

# Run migrations
alembic upgrade head

# Start API (from apps/api)
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd apps/web

# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Open http://localhost:3000
```

### Database Setup

```bash
# If using local Postgres
psql -U postgres

# In psql:
CREATE DATABASE titan_db;
CREATE USER titan_user WITH PASSWORD 'titanpass';
ALTER ROLE titan_user SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE titan_db TO titan_user;

# Then run migrations from apps/api:
alembic upgrade head
```

---

## 📁 Project Structure

```
TITAN/
├── apps/
│   ├── api/                           # FastAPI backend
│   │   ├── app/
│   │   │   ├── agents/               # LangGraph + Ministers
│   │   │   │   ├── graph.py          # State machine
│   │   │   │   ├── nodes.py          # Node functions
│   │   │   │   ├── state.py          # State TypedDict
│   │   │   │   ├── prompts.py        # Shared prompts
│   │   │   │   └── ministers/        # Minister implementations
│   │   │   │       ├── base.py       # BaseMinister class
│   │   │   │       └── ministers.py  # Minister instantiations
│   │   │   ├── api/v1/               # REST endpoints
│   │   │   ├── core/                 # Config, DB, logging
│   │   │   ├── models/               # ORM models
│   │   │   ├── services/             # Business logic
│   │   │   └── repositories/         # Data access
│   │   └── main.py                   # FastAPI app
│   │
│   └── web/                           # Next.js frontend
│       ├── src/
│       │   ├── app/                  # App Router pages
│       │   ├── components/           # React components
│       │   ├── hooks/                # Custom hooks
│       │   └── store/                # Zustand stores
│       └── next.config.ts
│
└── docs/                              # Documentation
    ├── ARCHITECTURE.md
    ├── DEBATE_ENGINE.md
    └── SIMULATION_ENGINE.md
```

---

## 👨‍💼 Adding a Custom Minister

### Step 1: Create Minister Class

Create a new file in `apps/api/app/agents/ministers/custom_ministers.py`:

```python
"""
Custom Minister Example: Education Minister
"""
from typing import Dict, Any
from app.agents.ministers.base import BaseMinister


class EducationMinister(BaseMinister):
    """
    Analyzes policy impact on education systems and human capital.
    """
    
    role = "education_minister"
    display_name = "🎓 Education Minister"
    
    domain_focus = """
    - Educational access and equity
    - Curriculum and skill development
    - Teacher recruitment and retention
    - Educational infrastructure
    - Literacy and vocational training
    """
    
    personality_traits = [
        "equity-focused",
        "long-term thinker",
        "data-driven",
        "student-advocate",
    ]
    
    red_lines = [
        "Policies that reduce educational access for disadvantaged communities",
        "Cutting education budget below 6% of GDP",
        "Privatization without equal access guarantees",
        "Reduction in vocational training programs",
    ]
    
    async def analyze(self, problem: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze policy through education lens.
        
        Should return:
        {
            "situation_assessment": str,
            "key_findings": List[str],
            "proposed_solutions": List[str],
            "concerns": List[str],
            "confidence": float (0.0-1.0),
        }
        """
        prompt = f"""
You are the {self.display_name}.

Your domain expertise: {self.domain_focus}

Analyze this policy problem through an EDUCATION lens:

PROBLEM: {problem}

{f'CONTEXT: {context}' if context else ''}

Provide:
1. Situation Assessment (how education is affected)
2. Key Findings (3-5 critical points)
3. Proposed Solutions (2-3 concrete steps)
4. Concerns (risks to education sector)
5. Confidence Score (0-100)

Format as JSON:
{{
    "situation_assessment": "...",
    "key_findings": ["...", "..."],
    "proposed_solutions": ["...", "..."],
    "concerns": ["...", "..."],
    "confidence": 75
}}
"""
        
        result = await self.llm_call(prompt)
        return result
```

### Step 2: Register Minister

In `apps/api/app/agents/ministers/ministers.py`, add to CABINET:

```python
from custom_ministers import EducationMinister

CABINET = [
    EconomicMinister(),
    TechnologyMinister(),
    # ... other ministers ...
    EducationMinister(),  # Add here
]

MINISTER_REGISTRY = {minister.role: minister for minister in CABINET}
```

### Step 3: Update Constants

In `apps/api/app/core/constants.py`:

```python
class MinisterRole(str, Enum):
    # ... existing roles ...
    EDUCATION_MINISTER = "education_minister"

MINISTER_DISPLAY_NAMES[MinisterRole.EDUCATION_MINISTER] = "🎓 Education Minister"
MINISTER_DESCRIPTIONS[MinisterRole.EDUCATION_MINISTER] = "..."
ANALYZING_MINISTERS.append(MinisterRole.EDUCATION_MINISTER)
```

### Step 4: Test Your Minister

```python
# apps/api/test_custom_minister.py
import asyncio
from app.agents.ministers.custom_ministers import EducationMinister

async def test_education_minister():
    minister = EducationMinister()
    
    result = await minister.analyze(
        problem="Increase STEM education to boost tech sector growth",
        context="Current STEM enrollment is 30% of students"
    )
    
    print(result)
    assert "situation_assessment" in result
    assert "key_findings" in result
    assert result["confidence"] >= 0

if __name__ == "__main__":
    asyncio.run(test_education_minister())
```

Run it:
```bash
cd apps/api
python test_custom_minister.py
```

### Step 5: Update Frontend (Optional)

Add custom styling in `apps/web/src/components/parliament/AgentCards.tsx`:

```tsx
const MINISTER_COLORS = {
  education_minister: "from-blue-600 to-blue-400",
  // ... other colors ...
};

const MINISTER_EMOJIS = {
  education_minister: "🎓",
  // ... other emojis ...
};
```

---

## 🗣️ Extending the Debate Engine

### Modify Debate Phases

Edit `apps/api/app/agents/nodes.py`:

```python
async def node_custom_debate_phase(state: GovernanceState) -> Dict[str, Any]:
    """
    Add new debate phase between existing phases.
    
    Example: Fact-checking phase before voting
    """
    problem = state["problem"]
    debate_arguments = state.get("debate_arguments", [])
    
    # Create a fact-checker agent
    prompt = f"""
You are a fact-checker in a policy debate.

Policy proposals so far:
{format_debate_arguments(debate_arguments)}

Identify any false claims, unsupported assertions, or misleading statistics.
Rate the factual accuracy of each proposal (0-100).

Return JSON with fact-check results.
"""
    
    fact_check_results = await llm_call(prompt)
    
    return {
        "debate_arguments": state["debate_arguments"] + [fact_check_results],
        "current_phase": "fact_checking",
    }
```

### Add Custom Voting Logic

Edit `apps/api/app/agents/nodes.py`:

```python
async def node_weighted_vote(state: GovernanceState) -> Dict[str, Any]:
    """
    Instead of 1 vote per minister, weight votes by expertise relevance.
    """
    votes = state.get("votes", [])
    problem = state["problem"]
    
    # For each vote, calculate relevance weight
    weighted_votes = []
    for vote in votes:
        relevance = calculate_relevance(vote["agent_role"], problem)
        vote["weight"] = relevance
        weighted_votes.append(vote)
    
    return {
        "votes": weighted_votes,
        "voting_method": "weighted_consensus"
    }
```

### Add Simulation Scenarios

Edit `apps/api/app/agents/ministers/simulation.py`:

```python
class SimulationAgent(BaseMinister):
    FUTURES = [
        "future_optimistic",
        "future_pessimistic",
        # Add custom scenarios:
        "future_political_upheaval",
        "future_pandemic_recession",
        "future_ai_disruption",
    ]
    
    async def simulate_future(self, future: str, policy: str) -> Dict[str, float]:
        """Evaluate policy in specific future scenario."""
        # Custom simulation logic
        ...
```

---

## ✅ Running Tests

### Backend Tests

```bash
cd apps/api

# Run all tests
pytest

# Run specific test file
pytest tests/test_ministers.py

# Run with coverage
pytest --cov=app tests/

# Run async tests
pytest --asyncio-mode=auto tests/
```

### Write a Test

```python
# apps/api/tests/test_ministers.py
import pytest
from app.agents.ministers.base import BaseMinister
from app.core.validation import ProblemInputRequest


@pytest.mark.asyncio
async def test_minister_analysis():
    """Test that minister returns valid analysis."""
    minister = YourCustomMinister()
    
    result = await minister.analyze(
        problem="Test policy question about education",
        context="Test context"
    )
    
    assert "situation_assessment" in result
    assert "key_findings" in result
    assert isinstance(result["confidence"], (int, float))
    assert 0 <= result["confidence"] <= 100


def test_input_validation():
    """Test that invalid input is rejected."""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        ProblemInputRequest(problem="too short")
    
    with pytest.raises(ValidationError):
        ProblemInputRequest(problem="<script>alert('xss')</script>")


@pytest.mark.asyncio
async def test_full_debate_flow():
    """Test end-to-end debate session."""
    from app.services.session_service import SessionService
    
    service = SessionService()
    session = await service.create_session(
        problem="Test policy question",
        context="Test context"
    )
    
    assert session.status == "pending"
    assert session.project_id is not None
    
    result = await service.run_session(session.project_id)
    
    assert result.status == "completed"
    assert len(result.votes) > 0
```

### Frontend Tests

```bash
cd apps/web

# Run tests
pnpm test

# Run with coverage
pnpm test:coverage

# Run E2E tests (if set up)
pnpm test:e2e
```

---

## 📝 Code Style & Standards

### Python

```python
# Use type hints everywhere
async def analyze(self, problem: str, context: str = "") -> Dict[str, Any]:
    pass

# Use docstrings
def method_name(arg: str) -> bool:
    """
    Brief description.
    
    Args:
        arg: Description
        
    Returns:
        Description of return value
    """

# Follow PEP 8
# Line length: 100 characters max
# Use Black formatter: black apps/api
```

### TypeScript/React

```typescript
// Use strict TypeScript
// Enable strict mode in tsconfig.json

// Use proper typing
interface Props {
  sessionId: string;
  onVote: (option: string) => Promise<void>;
}

export const VotingPanel: React.FC<Props> = ({ sessionId, onVote }) => {
  return <div>...</div>;
};

// Use functional components
// Use React Hooks for state
```

### Formatting

```bash
# Python - Auto-format
black apps/api

# Python - Lint
pylint apps/api

# TypeScript - Format
prettier --write apps/web/src

# TypeScript - Lint
eslint apps/web/src
```

---

## 🚀 Submitting Changes

### 1. Fork & Branch

```bash
git checkout -b feature/add-education-minister
```

### 2. Make Changes

- Add your feature
- Write tests
- Update documentation
- Format code

### 3. Test Locally

```bash
# Backend
cd apps/api
pytest

# Frontend
cd apps/web
pnpm lint
pnpm build

# Full integration
docker-compose -f docker/docker-compose.yml up
# Test manually
```

### 4. Commit

```bash
git add .
git commit -m "feat: add Education Minister to TITAN cabinet"
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>

# Type: feat, fix, docs, style, refactor, test, chore
# Scope: agents, api, web, database, etc.
# Subject: imperative, 50 chars max
# Body: detailed explanation (optional)
# Footer: references, breaking changes (optional)

Example:
feat(agents): add Education Minister to TITAN cabinet

Added new Education Minister agent to analyze policy impact
on educational systems. Includes domain expertise in:
- Educational access and equity
- Curriculum development
- Teacher retention

The minister analyzes problems through an education lens and
votes based on impact to human capital development.

Closes #123
```

### 5. Submit Pull Request

- Link to issue (if applicable)
- Describe changes clearly
- Include test evidence
- Update changelog

---

## 🎯 What We're Looking For

### New Minister Ideas

We want ministers covering:
- Healthcare & Medical Innovation
- Labor & Workforce Development
- Justice & Legal Reform
- Digital Privacy & Security
- International Relations
- Energy & Climate (specialized)

### Debate Engine Improvements

- Better consensus detection
- Multi-round debate enhancements
- Alternative voting schemes
- Simulation scenario generation
- Dissent tracking & analysis

### UI/UX Enhancements

- Real-time collaboration features
- Comparison tools for past debates
- Export/sharing capabilities
- Analytics dashboard
- Accessibility improvements

---

## ❓ Questions?

- Check [ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- Review existing minister implementations
- Open a GitHub Discussion
- Contact maintainers

---

**Happy contributing! 🚀**

**Last Updated:** 2026-06-18
