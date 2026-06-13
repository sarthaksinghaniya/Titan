# TITAN — Developer Quick Reference

> **Quick lookup for common tasks and commands**

## 🚀 Quick Start

### Start Development Stack
```bash
# Terminal 1: Backend
cd apps/api
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd apps/web
pnpm dev

# Terminal 3: Database (Docker)
docker run --name titan-pg -e POSTGRES_PASSWORD=titanpass \
  -e POSTGRES_DB=titan_db -e POSTGRES_USER=titan_user \
  -p 5432:5432 -d postgres:16

# Access
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
```

## 📝 Common Commands

### Backend

```bash
cd apps/api

# Run migrations
alembic upgrade head
alembic downgrade -1  # Rollback one migration

# Run tests
pytest                    # All tests
pytest tests/test_validation.py  # Specific file
pytest -k test_name       # Specific test
pytest -v --cov=app      # Verbose with coverage

# Lint & Format
black .                   # Auto-format Python
pylint app/
isort .                   # Organize imports

# Add dependencies
pip install package_name
pip freeze > requirements.txt
```

### Frontend

```bash
cd apps/web

# Development
pnpm dev              # Start dev server
pnpm build            # Build for production
pnpm start            # Run production build
pnpm lint             # Check code style
pnpm typecheck        # TypeScript check

# Dependencies
pnpm add package_name      # Add to package.json
pnpm remove package_name
pnpm update              # Update all packages
```

## 🏗️ Architecture Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `app/agents/graph.py` | LangGraph state machine definition |
| `app/agents/nodes.py` | All node functions (11 total) |
| `app/agents/state.py` | GovernanceState TypedDict |
| `app/agents/ministers/` | Minister implementations |
| `app/api/v1/projects.py` | REST endpoints |
| `app/core/constants.py` | Single source of truth for enums |
| `app/core/validation.py` | Input sanitization |
| `app/core/cost_tracking.py` | LLM cost tracking |

### Debate Flow

```
input_validation (validates problem)
  ↓
node_minister_analysis (6 parallel LLM calls)
  ↓
aggregate_analyses (merge results)
  ↓
debate_round (5 sequential speakers)
  ↓
opposition_attack (dedicated attack)
  ↓
rebuttal_round (5 parallel defenses)
  ↓
minister_vote (6 parallel votes)
  ↓
tally_votes (count votes)
  ↓
simulation_phase (stress test)
  ↓
prime_minister_synthesis (final recommendation)
```

## 🧪 Testing Patterns

### Test Structure
```python
@pytest.mark.asyncio
async def test_feature():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = await function(input_data)
    
    # Assert
    assert result == expected
```

### Mock LLM
```python
from unittest.mock import AsyncMock

mock_llm = AsyncMock()
mock_llm.return_value = {"analysis": "..."}

with patch('app.agents.ministers.llm_call', mock_llm):
    result = await minister.analyze("problem")
```

### Run Async Tests
```bash
pytest --asyncio-mode=auto tests/
```

## 🐛 Debugging

### Enable Debug Logging
```python
# app/core/logging.py
logging.getLogger().setLevel(logging.DEBUG)
```

### Check Database State
```sql
-- Connect to TITAN database
psql -U titan_user titan_db

-- Check sessions
SELECT id, status, created_at FROM projects ORDER BY created_at DESC;

-- Check analyses
SELECT agent_role, created_at FROM agents WHERE project_id = 'UUID';

-- Check votes
SELECT agent_role, voted_option FROM votes WHERE project_id = 'UUID';
```

### Inspect API Response
```bash
# Session detail
curl http://localhost:8000/api/v1/sessions/{session_id}

# Stream debate events
curl -N http://localhost:8000/api/v1/sessions/{session_id}/stream
```

## 📚 Documentation

- **ARCHITECTURE.md** — System design and folder structure
- **DEBATE_ENGINE.md** — 5-phase debate flow
- **SIMULATION_ENGINE.md** — 4 futures and 5 metrics
- **DEPLOY.md** — Production deployment checklist
- **CONTRIBUTING.md** — How to add custom ministers
- **HACKATHON_REVIEW.md** — Judge review and scoring

## 🔑 Key Constants

### Use These Instead of Magic Strings

```python
from app.core.constants import (
    DebatePhase,         # "pending", "analyzing", etc.
    MinisterRole,        # "economic_minister", etc.
    SimulationFuture,    # "future_optimistic", etc.
    SimulationMetric,    # "economic_impact", etc.
    PHASE_DESCRIPTIONS,  # Display names for phases
    MINISTER_DISPLAY_NAMES,  # Display names for ministers
    ANALYZING_MINISTERS,  # List of analyzing ministers
)
```

## 🔐 Security Checklist

- [ ] Never commit `.env` files
- [ ] Use `ProblemInputRequest` for all user input
- [ ] Validate JSON from LLM before parsing
- [ ] Log sensitive operations (API calls, auth attempts)
- [ ] Use CORS whitelist in production
- [ ] Rotate API keys regularly
- [ ] Use connection pooling for database

## 🚨 Common Issues & Solutions

### Issue: LLM API Timeout
```python
# Increase timeout
AGENT_TIMEOUT_SECONDS = 300  # In .env

# Implement retry
from app.core.error_recovery import retry_with_backoff
result = await retry_with_backoff(llm_call, max_attempts=3)
```

### Issue: Database Connection Pool Exhausted
```bash
# Check connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'titan_db';

# Increase pool in .env
DATABASE_POOL_SIZE=40
DATABASE_MAX_OVERFLOW=20
```

### Issue: Frontend Can't Connect to API
```bash
# Check CORS in .env
ALLOWED_ORIGINS=http://localhost:3000

# Check Next.js rewrites in next.config.ts
async rewrites() {
  return [{
    source: "/api/v1/:path*",
    destination: "http://localhost:8000/api/v1/:path*"
  }]
}
```

## 📊 Performance Tips

### Database Queries
```python
# Use proper indexing
CREATE INDEX idx_projects_status ON projects(status);

# Use ORM efficiently
# ❌ Bad: N+1 queries
for project in projects:
    agents = get_agents(project.id)

# ✅ Good: Join or eager loading
projects = session.query(Project).options(
    selectinload(Project.agents)
).all()
```

### LLM Calls
```python
# Batch when possible
results = await asyncio.gather(
    minister1.analyze(problem),
    minister2.analyze(problem),
    minister3.analyze(problem),
)

# Cache results
from functools import lru_cache

@lru_cache(maxsize=100)
async def analyze_cached(problem_hash: str):
    return ...
```

### Frontend Optimization
```typescript
// Use Zustand selectors to prevent re-renders
const votes = useSessionStore((state) => state.votes);

// Memoize expensive components
const DebateTimeline = React.memo(({ debates }: Props) => {
  return ...
});
```

## 🔗 Useful Links

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

## 📞 Getting Help

1. Check this Quick Reference
2. Read relevant docs (ARCHITECTURE.md, etc.)
3. Search codebase for similar patterns
4. Check existing GitHub issues
5. Open new issue with:
   - Clear title
   - Minimal reproduction
   - Environment details
   - Error message

---

**Last Updated:** 2026-06-13  
**Keep this handy! 📌**
