# TITAN — Future Simulation Engine

> **4 futures. 5 metrics. 1 winning policy.**
> The simulation engine stress-tests the democratically chosen policy option
> across four structurally distinct world-states before the Prime Minister synthesises.

---

## Engine Overview

```
After vote tally resolves a winning option:

  winning_option  ──────────────────────────────────────────────────┐
                                                                     │
              ┌──────────────────────────────────────────────────────┤
              │          SIMULATION ENGINE (asyncio.gather)          │
              │                                                      │
              │   ┌───────────────┐   ┌───────────────┐             │
              │   │  Future A     │   │  Future B     │             │
              │   │  OPTIMISTIC   │   │  PESSIMISTIC  │             │
              │   │               │   │               │             │
              │   │ ● Economy  87 │   │ ● Economy  42 │             │
              │   │ ● Sustain  78 │   │ ● Sustain  55 │             │
              │   │ ● Satisf.  83 │   │ ● Satisf.  38 │             │
              │   │ ● Cost     72 │   │ ● Cost     31 │             │
              │   │ ● Risk     85 │   │ ● Risk     44 │             │
              │   │               │   │               │             │
              │   │ Composite: 81 │   │ Composite: 42 │             │
              │   └───────────────┘   └───────────────┘             │
              │                                                      │
              │   ┌───────────────┐   ┌───────────────┐             │
              │   │  Future C     │   │  Future D     │             │
              │   │  TECH-DRIVEN  │   │  CONSTRAINED  │             │
              │   │               │   │               │             │
              │   │ ● Economy  91 │   │ ● Economy  58 │             │
              │   │ ● Sustain  66 │   │ ● Sustain  72 │             │
              │   │ ● Satisf.  74 │   │ ● Satisf.  61 │             │
              │   │ ● Cost     88 │   │ ● Cost     49 │             │
              │   │ ● Risk     79 │   │ ● Risk     63 │             │
              │   │               │   │               │             │
              │   │ Composite: 80 │   │ Composite: 61 │             │
              │   └───────────────┘   └───────────────┘             │
              │                                                      │
              └──────────────────────────────────────────────────────┘
                                      │
                         4 × SimulationResult
                                      │
                         Prime Minister Synthesis
                         (reads all 4 futures to calibrate confidence)
                                      │
                         Black Swan Resilience Engine
```

---

## 1. The Four Futures

Each future defines a distinct **world-state** that alters how the policy performs. The LLM is instructed to hold the future's assumptions constant and score the policy against them — not to invent the future, but to evaluate the policy within it.

### Future A — Optimistic

```
World-State Assumptions:
  ✓ Strong political will and cross-party support
  ✓ Stable macroeconomic environment (GDP growth 3–4%)
  ✓ High citizen trust and public cooperation
  ✓ Technology adoption proceeds as planned
  ✓ International partnerships support the policy
  ✓ No major external shocks during implementation

Simulation Bias:
  → Scores reflect best achievable outcomes under ideal conditions
  → Identifies the policy's ceiling potential
  → Flags what must go right for the policy to succeed fully

Purpose for PM:
  "This is the best case. If we cannot achieve these scores even optimistically,
   the policy is fundamentally flawed."

Visual Identity:
  label: "Future A — Optimistic"
  color: "emerald"
  icon:  "TrendingUp"
  badge: "BEST CASE"
```

### Future B — Pessimistic

```
World-State Assumptions:
  ✗ Weak political will, frequent leadership changes
  ✗ Economic headwinds (GDP growth 0.5–1%)
  ✗ Low citizen trust, moderate public resistance
  ✗ Technology delays and cost overruns (25% above estimate)
  ✗ International pressure against key policy elements
  ✗ Budget freezes reduce implementation capacity by 30%

Simulation Bias:
  → Scores reflect outcomes under realistic adverse conditions
  → Identifies the policy's floor — minimum guaranteed impact
  → Exposes which metrics are most sensitive to adverse conditions

Purpose for PM:
  "This is the floor. If these scores are acceptable, the policy is resilient.
   If not, the downside risk is too great."

Visual Identity:
  label: "Future B — Pessimistic"
  color: "rose"
  icon:  "TrendingDown"
  badge: "WORST CASE"
```

### Future C — Technology-Driven

```
World-State Assumptions:
  ✓ Accelerated AI and automation deployment (2× faster than baseline)
  ✓ Digital infrastructure fully available (100% broadband coverage)
  ✓ High-skilled tech workforce available
  ✓ Data governance frameworks enacted rapidly
  ~ Some equity gaps widen due to digital divide
  ~ Environmental cost of data center energy growth is significant
  ✗ Physical infrastructure investment reduced in favour of digital

Simulation Bias:
  → Scores reflect outcomes when technology is the primary lever
  → Economy and cost metrics likely high; sustainability and satisfaction mixed
  → Tests whether the policy holds when digitisation outpaces human adaptation

Purpose for PM:
  "This future tests the policy's tech assumptions.
   A policy that only works with perfect tech adoption is fragile."

Visual Identity:
  label: "Future C — Technology-Driven"
  color: "indigo"
  icon:  "Cpu"
  badge: "TECH SURGE"
```

### Future D — Resource-Constrained

```
World-State Assumptions:
  ✗ Budget reduced by 40% due to fiscal pressure
  ✗ Key raw materials scarce (supply chain disruptions)
  ✗ Workforce availability reduced (emigration, demographics)
  ✗ Energy costs +60% (inflationary pressure on implementation)
  ~ Political will present but execution capacity is limited
  ✓ Community-led initiatives partially compensate for government capacity gaps

Simulation Bias:
  → Scores reflect outcomes when resources are severely constrained
  → Tests phasing: what happens if only Phase 1 is ever funded?
  → High sustainability scores expected if policy is resource-efficient
  → Identifies which parts of the policy are non-negotiable vs. optional

Purpose for PM:
  "This future tests the policy's minimum viable form.
   What survives budget cuts? What must be protected at all costs?"

Visual Identity:
  label: "Future D — Resource-Constrained"
  color: "amber"
  icon:  "AlertTriangle"
  badge: "CONSTRAINED"
```

---

## 2. The Five Metrics

Every future scores the policy on the same five dimensions. Each metric maps directly to a ministerial domain and feeds the PM synthesis.

### Metric 1 — Economy Score (0–100)

```
Maps to:   Economic Minister
Measures:  Economic output, employment, fiscal impact, investment return

Components:
  GDP impact          → Does the policy grow or shrink economic output?
  Employment delta    → Net jobs created vs. displaced over 10 years
  Fiscal return       → ROI on public investment over the policy horizon
  Investment signal   → Does the policy attract or repel private capital?
  Inflation risk      → Does implementation create inflationary pressure?

Scoring Guide:
  90–100  → Net GDP growth >3%, employment +>5M, ROI >200% in 10yr
  70–89   → Net GDP growth 1–3%, employment positive, ROI 100–200%
  50–69   → Neutral GDP, employment roughly stable, ROI 50–100%
  30–49   → GDP drag, employment loss <2M, ROI <50%
  0–29    → GDP contraction, employment loss >2M, negative fiscal return

Database column:  simulations.economic_score
PM weight:        25%  (in composite score)
```

### Metric 2 — Sustainability Score (0–100)

```
Maps to:   Environment Minister
Measures:  Carbon impact, ecological footprint, long-term resource viability

Components:
  Carbon delta        → Net change in CO₂ equivalent emissions per year
  Ecosystem impact    → Reversible vs. irreversible ecological damage
  Resource efficiency → Does the policy use or conserve finite resources?
  Climate alignment   → Consistency with Paris Agreement trajectory
  Circular economy    → Does the policy embed circular principles?

Scoring Guide:
  90–100  → Carbon negative, zero irreversible damage, Paris-aligned
  70–89   → Carbon neutral or mild reduction, no protected area damage
  50–69   → Carbon-positive but improving trajectory; some reversible damage
  30–49   → Significant emissions, some ecological damage, poor alignment
  0–29    → High emissions, irreversible damage, violates climate agreements

Database column:  simulations.environmental_score
PM weight:        20%  (in composite score)
```

### Metric 3 — Public Satisfaction Score (0–100)

```
Maps to:   Citizen Minister
Measures:  Citizen welfare, equity, quality of life, trust in government

Components:
  Equity reach        → Does the bottom quintile benefit proportionally?
  Quality of life     → Measurable improvement in daily life for ordinary citizens
  Community cohesion  → Does the policy bring communities together or divide?
  Trust signal        → Does implementation increase or decrease govt trust?
  Accessibility       → Are services accessible to non-digital, non-literate citizens?

Scoring Guide:
  90–100  → Bottom quintile benefits most, trust increases, accessibility universal
  70–89   → Most citizens benefit, some equity gaps, net positive welfare
  50–69   → Middle-class gains; vulnerable groups partially served
  30–49   → Significant equity gaps, trust eroding, accessibility poor
  0–29    → Most vulnerable excluded, civil unrest risk, trust collapse

Database column:  simulations.social_score
PM weight:        25%  (in composite score)
```

### Metric 4 — Implementation Cost Score (0–100)

```
Maps to:   Infrastructure Minister
Measures:  Value for money, delivery feasibility, cost efficiency

NOTE: Higher score = better value / lower effective cost.
      A score of 100 = extremely cost-efficient, on-time, on-budget.
      A score of 0   = massively over-budget, no return on spend.

Components:
  Cost per outcome unit → $ per citizen served, $ per job created, etc.
  Timeline adherence    → On-time delivery probability
  Budget certainty      → Variance risk (cost overrun likelihood)
  Maintenance burden    → 20-year total cost of ownership
  Opportunity cost      → What else could this budget have achieved?

Scoring Guide:
  90–100  → Best-in-class cost efficiency, <10% overrun risk, low maintenance
  70–89   → Good value, 10–25% overrun risk, manageable maintenance
  50–69   → Average value, 25–40% overrun risk, medium maintenance burden
  30–49   → Poor value, >40% overrun risk, heavy maintenance commitment
  0–29    → Extremely poor value, likely to fail on budget, unsustainable

Database column:  simulations.feasibility_score
PM weight:        15%  (in composite score)
```

### Metric 5 — Risk Score (0–100)

```
Maps to:   Opposition Minister
Measures:  Implementation risk, political risk, systemic fragility

NOTE: Higher score = lower risk (better outcome).
      A score of 100 = near-zero risk, resilient plan.
      A score of 0   = near-certain failure or catastrophic unintended consequences.

Components:
  Implementation risk  → Probability of execution failure
  Political risk       → Susceptibility to policy reversal or defunding
  Corruption risk      → Vulnerability to capture by vested interests
  Systemic risk        → Second-order effects that could destabilise adjacent systems
  Reversibility        → Can the policy be unwound if it fails without lasting harm?

Scoring Guide:
  90–100  → Low implementation risk, politically durable, easily reversible
  70–89   → Manageable risk, moderate political durability, partially reversible
  50–69   → Moderate risk, some political fragility, difficult to reverse
  30–49   → High risk, politically vulnerable, hard to reverse
  0–29    → Very high risk, near-certain political reversal, irreversible if it fails

Database column:  simulations.feasibility_score (inverse of risk_score)
                  feasibility_score = 100 - risk_score
PM weight:        15%  (in composite score)
```

---

## 3. Composite Score Formula

```
composite_score = (
    economy_score       × 0.25 +
    sustainability_score × 0.20 +
    satisfaction_score  × 0.25 +
    cost_score          × 0.15 +
    risk_score          × 0.15
)

All weights sum to 1.0.
Score range: 0–100.

Interpretation bands:
  85–100  EXCEPTIONAL     Strong mandate for implementation
  70–84   STRONG          Proceed with targeted mitigations
  55–69   MODERATE        Proceed with significant safeguards
  40–54   WEAK            Reconsider — major redesign needed
  0–39    POOR            Do not proceed — fundamental flaws

The composite_score is the single number the PM uses to rank futures
and calibrate their confidence score.
```

---

## 4. Data Models

### 4.1 Backend — SimulationResult (Python TypedDict)

```python
class FutureScenario(TypedDict):
    """Per-variable narrative impact within a future."""
    budget_impact:         str    # qualitative + quantitative budget narrative
    population_impact:     str    # how many people affected, in what way
    resources_impact:      str    # material/energy/water resource impact
    education_impact:      str    # workforce skill/education dimension
    infrastructure_impact: str    # physical + digital infrastructure change


class SimulationResult(TypedDict):
    # Identity
    future_name:      str         # "Future A (Optimistic)" | B | C | D
    future_code:      str         # "A" | "B" | "C" | "D"
    option_name:      str         # exact winning option name

    # Core variable breakdown
    scenario_data:    FutureScenario

    # Five metric scores (0–100 each, higher = better)
    economic_score:      float    # Economy
    environment_score:   float    # Sustainability
    citizen_score:       float    # Public Satisfaction  [raw from LLM]
    social_score:        float    # Public Satisfaction  [alias, stored in DB]
    risk_score:          float    # Risk (raw: higher = more risk)
    feasibility_score:   float    # Risk (inverted: 100 - risk_score, stored in DB)

    # Composite
    composite_score:     float    # weighted formula result

    # Logistics
    risk_level:                 str    # "low" | "medium" | "high" | "critical"
    time_to_implement_months:   int
    cost_estimate_usd_millions: float
    projected_population_impact: float  # millions of people (positive impact)

    # Narrative
    key_risks:    List[str]       # 2–3 risks specific to this future
    key_benefits: List[str]       # 2–3 benefits specific to this future

    # Metadata
    _timestamp:   str             # ISO 8601
    _elapsed_ms:  int             # LLM latency
```

### 4.2 Backend — SQLAlchemy ORM (`simulations` table)

```python
class Simulation(Base):
    __tablename__ = "simulations"

    # Identity
    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    option_name         = Column(String(500), nullable=False)
    option_description  = Column(Text, nullable=True)

    # Future identifier
    future_code = Column(String(1), nullable=False)      # "A" | "B" | "C" | "D"
    future_name = Column(String(100), nullable=False)    # full label

    # Five metric scores (0–100)
    economic_score      = Column(Float, nullable=False)
    social_score        = Column(Float, nullable=False)  # public satisfaction
    environmental_score = Column(Float, nullable=False)  # sustainability
    feasibility_score   = Column(Float, nullable=False)  # 100 - risk_score
    composite_score     = Column(Float, nullable=False)  # weighted average (indexed)

    # Risk classification
    risk_level          = Column(SAEnum(RiskLevel), nullable=False)

    # Logistics
    time_to_implement_months    = Column(Integer, nullable=False)
    cost_estimate_usd_millions  = Column(Float, nullable=False)
    projected_population_impact = Column(Float, nullable=False)  # millions

    # Narrative (JSONB)
    key_risks       = Column(JSONB, nullable=False, default=list)   # List[str]
    key_benefits    = Column(JSONB, nullable=False, default=list)   # List[str]
    scenario_data   = Column(JSONB, nullable=False, default=dict)   # FutureScenario

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_simulations_project_composite", "project_id", "composite_score"),
        Index("ix_simulations_project_future",    "project_id", "future_code"),
        UniqueConstraint("project_id", "future_code", name="uq_simulation_project_future"),
    )
```

### 4.3 Frontend TypeScript Interface

```typescript
// packages/shared-types/src/index.ts

export type FutureCode = "A" | "B" | "C" | "D";

export type FutureLabel =
  | "Future A (Optimistic)"
  | "Future B (Pessimistic)"
  | "Future C (Technology-Driven)"
  | "Future D (Resource-Constrained)";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type SimulationBand =
  | "exceptional"   // 85–100
  | "strong"        // 70–84
  | "moderate"      // 55–69
  | "weak"          // 40–54
  | "poor";         // 0–39

export interface FutureScenario {
  budget_impact:         string;
  population_impact:     string;
  resources_impact:      string;
  education_impact:      string;
  infrastructure_impact: string;
}

export interface SimulationResult {
  id:          string;
  project_id:  string;

  // Future identity
  future_code: FutureCode;
  future_name: FutureLabel;
  option_name: string;

  // Five core metric scores (0–100, higher = better for all)
  economic_score:      number;   // Economy
  environmental_score: number;   // Sustainability
  social_score:        number;   // Public Satisfaction
  feasibility_score:   number;   // Implementation Cost (inverted risk)
  risk_score_raw?:     number;   // Raw risk (0–100, higher = more risk) — optional, UI derived

  // Composite
  composite_score:     number;
  band:                SimulationBand;  // derived from composite_score

  // Risk classification
  risk_level: RiskLevel;

  // Logistics
  time_to_implement_months:    number;
  cost_estimate_usd_millions:  number;
  projected_population_impact: number;  // millions

  // Narrative
  key_risks:     string[];
  key_benefits:  string[];
  scenario_data: FutureScenario;

  created_at: string;
}

// Aggregate across all 4 futures for a single option
export interface SimulationSummary {
  option_name:     string;
  futures:         Record<FutureCode, SimulationResult>;

  // Cross-future analytics
  avg_composite:   number;
  best_future:     FutureCode;   // highest composite score
  worst_future:    FutureCode;   // lowest composite score
  score_range:     number;       // best - worst (higher = more uncertain)
  volatility:      "stable" | "moderate" | "volatile";  // score_range < 15 | 15–30 | >30

  // Per-metric cross-future averages
  avg_economy:          number;
  avg_sustainability:   number;
  avg_satisfaction:     number;
  avg_cost_efficiency:  number;
  avg_risk:             number;
}
```

### 4.4 LLM Output Schema (injected into every simulation prompt)

```json
{
  "future_name": "<Future A (Optimistic)|Future B (Pessimistic)|Future C (Technology-Driven)|Future D (Resource-Constrained)>",
  "future_code": "<A|B|C|D>",
  "option_name": "<exact policy option name being simulated>",

  "scenario_data": {
    "budget_impact":         "<1–2 sentence narrative: how this future's conditions affect the budget required>",
    "population_impact":     "<1–2 sentence narrative: how many people are affected, in what way>",
    "resources_impact":      "<1–2 sentence narrative: material, energy, and resource implications>",
    "education_impact":      "<1–2 sentence narrative: workforce skills and education implications>",
    "infrastructure_impact": "<1–2 sentence narrative: physical and digital infrastructure changes needed>"
  },

  "economic_score":      "<0–100 integer: economy outcome in this future>",
  "environment_score":   "<0–100 integer: sustainability outcome in this future>",
  "citizen_score":       "<0–100 integer: public satisfaction in this future>",
  "risk_score":          "<0–100 integer: risk level in this future — higher = MORE risk>",

  "risk_level":                    "<low|medium|high|critical>",
  "time_to_implement_months":      "<integer: realistic delivery timeline in this future>",
  "cost_estimate_usd_millions":    "<float: total implementation cost in this future>",
  "projected_population_impact":   "<float: millions of people who benefit positively>",

  "key_risks":    ["<risk specific to this future>", "<risk 2>"],
  "key_benefits": ["<benefit specific to this future>", "<benefit 2>"]
}
```

---

## 5. Simulation Architecture

### 5.1 Execution Flow

```
node_simulation_phase(state: GovernanceState)
         │
         │  winning_option = state.metadata.winning_option
         │                   OR state.policy_options[0]
         │
         ├── asyncio.gather(
         │       run_sim("Future A (Optimistic)"),
         │       run_sim("Future B (Pessimistic)"),
         │       run_sim("Future C (Technology-Driven)"),
         │       run_sim("Future D (Resource-Constrained)")
         │   )
         │
         │   Each run_sim():
         │     SimulationAgent.simulate(problem, option_name, future_designation)
         │       → build prompt with future-specific world-state context
         │       → ChatGoogleGenerativeAI(model=flash, temperature=0.7)
         │       → ainvoke([SystemMessage, HumanMessage])
         │       → extract_json(response)
         │       → normalize: social_score, feasibility_score, composite_score
         │       → return SimulationResult dict
         │
         ├── GovernanceState.simulation_results: Annotated[List, operator.add]
         │   → 4 results appended
         │
         └── current_phase → "synthesizing"
```

### 5.2 System Prompt Structure

```
SYSTEM PROMPT (SimulationAgent.SYSTEM_PROMPT):
  Role:          TITAN Future Simulation Engine
  Task:          Evaluate a policy option inside a fixed world-state
  Metrics:       5 (economy, sustainability, satisfaction, cost, risk)
  Variables:     5 (budget, population, resources, education, infrastructure)
  Output:        JSON only, no commentary outside schema

USER PROMPT (per future):
  PROBLEM:           {problem}
  POLICY OPTION:     {option_name}
  FUTURE:            {future_designation}
  WORLD-STATE:       {future-specific assumption block}
  SCORING RULES:     {metric definitions and scoring guides}
  SCHEMA:            {output JSON schema}
```

### 5.3 World-State Injection (per future)

Each future's prompt includes a **world-state block** that constrains the LLM's assumptions:

```python
FUTURE_WORLD_STATES = {
    "A": """
WORLD-STATE: OPTIMISTIC
Assume the following conditions hold throughout implementation:
- Strong political will and stable government (no elections disrupting policy)
- Macroeconomic growth of 3–4% GDP annually
- High citizen cooperation and trust in government institutions
- Technology adoption proceeds on schedule with no major setbacks
- International support and funding partnerships are active
- No major external shocks (no pandemic, natural disaster, or financial crisis)
Score this policy at its CEILING POTENTIAL under ideal conditions.
""",
    "B": """
WORLD-STATE: PESSIMISTIC
Assume the following adverse conditions hold:
- Weak political will, government changes every 2 years resetting priorities
- Economic stagnation (GDP growth 0.5–1%, possible mild recession)
- Low citizen trust, moderate public resistance to the policy
- Technology delays and cost overruns (25% above initial estimates)
- International partners withdraw support halfway through
- Budget freezes reduce implementation capacity by 30% in Years 2–3
Score this policy at its FLOOR — minimum guaranteed impact under adversity.
""",
    "C": """
WORLD-STATE: TECHNOLOGY-DRIVEN
Assume the following technology-accelerated conditions:
- AI and automation deployment is 2× faster than baseline projections
- 100% broadband coverage achieved in Year 1 of implementation
- High-skilled tech workforce is abundantly available
- Digital governance frameworks enacted rapidly with cross-party support
- However: digital divide widens — 20% of population lacks device access
- Physical infrastructure investment is deprioritised in favour of digital
- Data center energy consumption increases significantly (sustainability trade-off)
Score this policy assuming technology is the PRIMARY lever but human equity gaps widen.
""",
    "D": """
WORLD-STATE: RESOURCE-CONSTRAINED
Assume the following scarcity conditions:
- Budget reduced by 40% due to fiscal emergency (tax revenue shortfall)
- Key raw materials scarce due to global supply chain disruptions
- Skilled workforce 25% below requirement (emigration and demographic shift)
- Energy costs +60% (inflationary, affects all physical implementation)
- Political will is present but execution capacity is severely limited
- Community-led initiatives partially compensate for government delivery gaps
Score this policy assuming only 60% of the planned budget is ever available.
"""
}
```

### 5.4 Score Normalization (post-LLM)

```python
def normalize_simulation_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize raw LLM output to match DB schema and frontend expectations.
    Called immediately after extract_json().
    """
    # risk_score from LLM: 0 = no risk, 100 = catastrophic risk
    # feasibility_score in DB: 0 = impossible, 100 = fully feasible
    # → invert
    risk_raw = raw.get("risk_score", 50)
    raw["feasibility_score"] = 100.0 - float(risk_raw)

    # citizen_score → social_score (DB column name)
    raw["social_score"] = float(raw.get("citizen_score", 50))

    # Composite: weighted formula
    e  = float(raw.get("economic_score",   50))
    su = float(raw.get("environment_score",50))
    sa = float(raw.get("citizen_score",    50))
    c  = float(raw.get("feasibility_score",50))
    r  = float(raw.get("feasibility_score",50))  # already inverted

    raw["composite_score"] = round(
        e  * 0.25 +
        su * 0.20 +
        sa * 0.25 +
        c  * 0.15 +
        r  * 0.15,
        2
    )

    # future_code extraction
    name = raw.get("future_name", "")
    raw["future_code"] = (
        "A" if "Optimistic"   in name else
        "B" if "Pessimistic"  in name else
        "C" if "Tech"         in name else
        "D" if "Constrained"  in name else
        "A"
    )

    return raw
```

### 5.5 Fallback Behaviour

```python
def _fallback_simulation(self, option_name: str, future_designation: str) -> SimulationResult:
    """
    Returns a neutral 50/50 result on any LLM failure.
    The pipeline continues — report is generated with fallback data flagged.
    """
    code = "A" if "Optimistic" in future_designation else \
           "B" if "Pessimistic" in future_designation else \
           "C" if "Tech" in future_designation else "D"

    return {
        "future_name":  future_designation,
        "future_code":  code,
        "option_name":  option_name,
        "scenario_data": {
            "budget_impact":         "Simulation data unavailable.",
            "population_impact":     "Simulation data unavailable.",
            "resources_impact":      "Simulation data unavailable.",
            "education_impact":      "Simulation data unavailable.",
            "infrastructure_impact": "Simulation data unavailable.",
        },
        "economic_score":      50.0,
        "environment_score":   50.0,
        "citizen_score":       50.0,
        "social_score":        50.0,
        "risk_score":          50.0,
        "feasibility_score":   50.0,
        "composite_score":     50.0,
        "risk_level":          "medium",
        "time_to_implement_months":    12,
        "cost_estimate_usd_millions":  0.0,
        "projected_population_impact": 0.0,
        "key_risks":    ["Simulation engine error — data not available"],
        "key_benefits": [],
        "_fallback":    True,   # flag for UI to show warning
    }
```

---

## 6. Cross-Future Analytics

These are computed after all 4 results arrive — either in the backend during PM synthesis or on the frontend for display.

### 6.1 Volatility Score

```
score_range = max(composites) - min(composites)

if score_range < 15:  volatility = "stable"
   → Policy performs consistently across all world-states
   → Low uncertainty — PM can commit with high confidence

if 15 ≤ score_range < 30: volatility = "moderate"
   → Some world-state sensitivity, but within acceptable bounds
   → PM should note which conditions are prerequisite

if score_range >= 30: volatility = "volatile"
   → Policy outcomes vary wildly depending on external conditions
   → PM must flag this — success is heavily context-dependent
```

### 6.2 Metric Sensitivity (per metric across futures)

```python
def metric_sensitivity(results: List[SimulationResult], metric: str) -> Dict:
    scores = [r[metric] for r in results]
    return {
        "min":    min(scores),
        "max":    max(scores),
        "avg":    sum(scores) / len(scores),
        "range":  max(scores) - min(scores),
        "most_sensitive_future": results[scores.index(min(scores))]["future_code"],
    }
```

### 6.3 Future Ranking Table (UI)

```
┌────────────────────────────────────────────────────────────────────┐
│  SIMULATION RESULTS              Technology-Led Transformation     │
├──────────────────┬────────┬────────┬────────┬────────┬────────────┤
│  Metric          │ Fut A  │ Fut B  │ Fut C  │ Fut D  │  Average   │
├──────────────────┼────────┼────────┼────────┼────────┼────────────┤
│  📈 Economy      │  87    │  42    │  91    │  58    │   69.5     │
│  🌿 Sustainability│  78    │  55    │  66    │  72    │   67.8     │
│  👥 Satisfaction │  83    │  38    │  74    │  61    │   64.0     │
│  💰 Cost Effic.  │  72    │  31    │  88    │  49    │   60.0     │
│  🛡️ Risk         │  85    │  44    │  79    │  63    │   67.8     │
├──────────────────┼────────┼────────┼────────┼────────┼────────────┤
│  COMPOSITE       │  81.3  │  42.1  │  80.0  │  60.7  │   66.0     │
│  BAND            │STRONG  │ POOR   │STRONG  │MODERATE│  MODERATE  │
├──────────────────┼────────┼────────┼────────┼────────┼────────────┤
│  Risk Level      │  Low   │  High  │  Low   │ Medium │            │
│  Timeline        │ 18mo   │ 36mo   │ 14mo   │ 28mo   │   24mo     │
│  Cost ($M)       │ 2,800  │ 4,100  │ 2,200  │ 3,600  │  3,175     │
│  People (M)      │  45    │  21    │  52    │  31    │   37.3     │
└──────────────────┴────────┴────────┴────────┴────────┴────────────┘

Volatility: VOLATILE  (range: 81.3 – 42.1 = 39.2)
Best Future: A (Optimistic)
Worst Future: B (Pessimistic)
Most Sensitive Metric: Public Satisfaction (range: 83 – 38 = 45)
```

---

## 7. Visual Presentation Spec

### 7.1 Radar Chart (per future)

```
Each future renders a pentagon/radar chart with 5 axes:

        Economy (0–100)
             ▲
             │
Sustainability ─┼─ Risk
             │
Public Satis ─┼─ Cost Efficiency

Each axis:  0 (centre) → 100 (edge)
Fill color: future-specific semi-transparent gradient
Stroke:     future-specific solid color

Overlaid view (all 4 futures):
  Future A  → emerald fill,  solid stroke
  Future B  → rose fill,     solid stroke
  Future C  → indigo fill,   solid stroke
  Future D  → amber fill,    solid stroke

Library: Recharts <RadarChart> with <PolarGrid>, <PolarAngleAxis>, <Radar × 4>
```

### 7.2 Future Card Design

```
┌──────────────────────────────────────────────────────┐
│  [A]  Future A — Optimistic              STRONG  81  │
│  gradient: from-emerald-900/40 to-emerald-800/20     │
│  border:   border-emerald-500/40                     │
│─────────────────────────────────────────────────────│
│  Economy        ████████████████████  87             │
│  Sustainability ████████████████░░░░  78             │
│  Satisfaction   █████████████████░░░  83             │
│  Cost Effic.    ██████████████░░░░░░  72             │
│  Risk Score     █████████████████░░░  85             │
│─────────────────────────────────────────────────────│
│  📅 18 months   💵 $2.8B   👥 45M people            │
│─────────────────────────────────────────────────────│
│  ✓ Strong economic multiplier effect                 │
│  ✓ Citizens report high satisfaction at 12mo mark    │
│  ⚠ Assumes stable political mandate for 5 years     │
└──────────────────────────────────────────────────────┘

Colors per future:
  A → emerald  (#10b981)
  B → rose     (#f43f5e)
  C → indigo   (#6366f1)
  D → amber    (#f59e0b)

Badge band colors:
  exceptional → green
  strong      → emerald
  moderate    → yellow
  weak        → orange
  poor        → red
```

### 7.3 Composite Bar Comparison

```
COMPOSITE SCORES                      Winning: Future A

  Future A ████████████████████████  81.3   ← BEST
  Future C ████████████████████████  80.0
  Future D ████████████████░░░░░░░░  60.7
  Future B ████████████░░░░░░░░░░░░  42.1   ← WORST

  ─────────────────────────────────────────────────
  Average  ████████████████░░░░░░░░  66.0
  Volatility: VOLATILE  ▲──────────────▼  Δ39.2
```

### 7.4 Animation Sequence

```
On simulation_result SSE event arrives per future:

  1. Future card slides in from right (staggered 150ms per card)
  2. Metric bars fill from 0 to value — 800ms ease-out
  3. Composite score counts up from 0 — 600ms
  4. Band badge fades in — 200ms
  5. Radar chart draws each axis arm — 400ms staggered

On all 4 complete:
  6. Overlay radar chart assembles with all 4 futures — 600ms
  7. Composite comparison bar fills — 400ms staggered
  8. Volatility badge fades in with colour
  9. "Best Future" winner glow pulses × 1
```

### 7.5 SSE Events for Simulation

```
SSE event: "simulation_started"
  payload: { option_name: string, futures_to_run: string[] }
  UI: show 4 empty skeleton cards with loading state

SSE event: "simulation_result"
  payload: SimulationResult
  UI: reveal corresponding future card with animation

SSE event: "simulation_complete"
  payload: { results: SimulationResult[], summary: SimulationSummary }
  UI: show overlay radar + comparison bar + volatility badge
```

---

## 8. Black Swan Engine

The Black Swan engine runs **after** the Prime Minister synthesis on the **chosen policy**. It selects a random catastrophic crisis and scores the policy's resilience against it.

### 8.1 Crisis Pool

```python
BLACK_SWAN_CRISES = [
    {
        "id": "recession",
        "name": "Global Economic Recession",
        "description": "GDP contracts 15% over 18 months; tax revenues collapse; budget cuts mandatory",
        "severity": "critical",
        "domain": "economic",
    },
    {
        "id": "pandemic",
        "name": "Global Pandemic",
        "description": "Lockdowns enforced; 30% workforce impact; supply chains disrupted for 24 months",
        "severity": "critical",
        "domain": "social",
    },
    {
        "id": "flood",
        "name": "Catastrophic 500-Year Flood",
        "description": "Core infrastructure destroyed in key regions; displacement of 5M+ citizens",
        "severity": "high",
        "domain": "infrastructure",
    },
    {
        "id": "supply_chain",
        "name": "Severe Supply Chain Shortage",
        "description": "Critical materials unavailable for 18+ months; construction halted",
        "severity": "high",
        "domain": "infrastructure",
    },
    {
        "id": "unrest",
        "name": "Massive Political Unrest",
        "description": "Nationwide protests; 40% drop in government approval; implementation paused",
        "severity": "high",
        "domain": "political",
    },
]
```

### 8.2 Black Swan Result Schema

```python
class BlackSwanResult(TypedDict):
    black_swan_crisis:  str     # Name of the crisis
    black_swan_impact:  str     # 3-sentence narrative of how the policy survives or fails
    resilience_score:   float   # 0–100 (higher = more resilient)
    crisis_severity:    str     # "low" | "medium" | "high" | "critical"
    crisis_domain:      str     # "economic" | "social" | "infrastructure" | "political"
```

### 8.3 Resilience Score Interpretation

```
90–100  FORTRESS     Policy survives intact; crisis may even accelerate adoption
70–89   RESILIENT    Policy survives with managed adjustments; core outcomes preserved
50–69   FRAGILE      Policy partially survives; some components fail or are suspended
30–49   VULNERABLE   Policy significantly damaged; major redesign required post-crisis
0–29    CATASTROPHIC Policy fails entirely under this crisis; must be abandoned or rebuilt
```

### 8.4 Visual — Black Swan Card

```
┌──────────────────────────────────────────────────────────┐
│  ☠ BLACK SWAN EVENT                     RESILIENCE: 71  │
│  border: border-zinc-500/40                               │
│  background: bg-zinc-950/60                               │
│─────────────────────────────────────────────────────────│
│  Crisis: Global Pandemic                                 │
│  Severity: CRITICAL   Domain: Social                     │
│─────────────────────────────────────────────────────────│
│  "The Technology-Led Transformation shows moderate       │
│   resilience against a global pandemic. The digital      │
│   infrastructure components continue functioning as      │
│   remote service delivery scales. However, the physical  │
│   infrastructure phase (Phase 2) would stall for 18–24   │
│   months, requiring a revised timeline..."               │
│─────────────────────────────────────────────────────────│
│  Resilience   ██████████████░░░░░░  71 / 100             │
│  Band:  RESILIENT                                        │
│  Policy survives with managed adjustments                │
└──────────────────────────────────────────────────────────┘
```

---

## 9. PM Synthesis Integration

The Prime Minister reads all simulation data through this structured context block:

```
SIMULATION RESULTS:
[Future A (Optimistic)]:     Option 'Technology-Led Transformation'
  Composite: 81.3 (STRONG)
  Economy: 87 | Sustainability: 78 | Satisfaction: 83 | Cost: 72 | Risk: 85
  Risk Level: Low | Timeline: 18mo | Cost: $2.8B | Impact: 45M people

[Future B (Pessimistic)]:    Option 'Technology-Led Transformation'
  Composite: 42.1 (POOR)
  Economy: 42 | Sustainability: 55 | Satisfaction: 38 | Cost: 31 | Risk: 44
  Risk Level: High | Timeline: 36mo | Cost: $4.1B | Impact: 21M people

[Future C (Technology-Driven)]: ...
[Future D (Resource-Constrained)]: ...

VOLATILITY: VOLATILE (Δ39.2) — outcomes vary significantly by world-state
MOST SENSITIVE METRIC: Public Satisfaction (range: 83 → 38)
RECOMMENDATION CONTEXT: This policy's success is heavily conditional on
maintaining political mandate and adequate budget. Failure modes concentrate
in the pessimistic scenario where public trust collapses.
```

The PM uses this to:
1. Set `confidence_score` (lower if volatility is HIGH)
2. Write targeted `risks_and_mitigations` for the worst-performing future
3. Acknowledge which world-state the implementation plan assumes
4. Design contingency triggers in `implementation_steps`

---

*TITAN Simulation Engine — policy tested across every possible tomorrow.*
