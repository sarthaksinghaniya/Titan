# TITAN — Black Swan Resilience Engine

> **1 random crisis. 3 measurements. 1 resilience score.**
> The Black Swan Engine is the final stress-test before the session completes.
> It exposes how the chosen policy holds up against the impossible-to-predict.

---

## Engine Overview

```
Prime Minister Synthesis completes
          │
          ▼
  ┌───────────────────────────────────────────────────────┐
  │            BLACK SWAN ENGINE                          │
  │                                                       │
  │  Step 1: Random crisis selected from pool of 5        │
  │                                                       │
  │  ☔ Flood          💸 Recession       🦠 Pandemic     │
  │  🏗️ Infra Collapse  📦 Supply Shortage               │
  │                    ↓                                  │
  │  Step 2: Evaluate policy against 3 dimensions         │
  │                                                       │
  │  🛡️ Resilience Score   (0–100)                       │
  │  ⚡ Recovery Speed     (0–100)                       │
  │  💀 Failure Points     (identified weak links)        │
  │                    ↓                                  │
  │  Step 3: Compute final resilience_score               │
  │                                                       │
  │  resilience_score = (resilience × 0.50)               │
  │                   + (recovery   × 0.30)               │
  │                   + (failure_penalty × 0.20)          │
  └───────────────────────────────────────────────────────┘
          │
          ▼
  Appended to FinalReport + SSE event published
  Session → COMPLETED
```

---

## 1. Crisis Pool — 5 Events

### Crisis 1 — Catastrophic Flood

```
id:          "flood"
name:        "Catastrophic 500-Year Flood"
severity:    CRITICAL
domain:      infrastructure
probability: rare (but escalating under climate change)

Shock Parameters:
  Physical damage:       Core transport and water infrastructure destroyed in key regions
  Displacement:          3–8 million citizens displaced; temporary housing required
  Economic loss:         Immediate GDP contraction of 4–8% in affected regions
  Timeline compression:  Physical implementation stalled 18–36 months
  Resource diversion:    30–50% of policy budget redirected to emergency relief

Stress Questions the LLM must answer:
  → Which parts of the policy are geographically vulnerable to flooding?
  → Does the policy's infrastructure have climate-resilient design?
  → Can digital/non-physical components continue operating independently?
  → Is there a disaster recovery clause in the implementation plan?
  → How does citizen trust change when the government is managing both crisis and policy?

Impact Profile (typical policy effect):
  Economy score:          −25 to −40 points
  Sustainability score:   −10 to −20 points (unless policy was green/resilient)
  Satisfaction score:     −15 to −30 points (displacement, disruption)
  Cost efficiency:        −30 to −50 points (budget diverted)
  Risk score:             −20 to −35 points (implementation at risk)

Visual Identity:
  icon:    "Waves"
  color:   "sky"
  badge:   "FLOOD EVENT"
  emoji:   "🌊"
```

### Crisis 2 — Global Economic Recession

```
id:          "recession"
name:        "Global Economic Recession"
severity:    CRITICAL
domain:      economic
probability: periodic (historical: every 10–15 years)

Shock Parameters:
  GDP contraction:       −12 to −18% over 18 months
  Unemployment spike:    +8–15 percentage points nationally
  Budget cuts mandatory: Government forced to reduce all non-essential spending 25–40%
  Credit markets:        Foreign investment withdraws; borrowing costs spike
  Political pressure:    Austerity demands compete with policy implementation

Stress Questions the LLM must answer:
  → Is the policy funded from recurrent budget or ring-fenced capital?
  → Do the policy's economic components accelerate recovery or deepen the recession?
  → Which ministerial owners can maintain delivery under a hiring freeze?
  → Are the implementation contracts cancellable or do they lock in costs?
  → Does the policy create countercyclical stimulus or consume resources during downturn?

Impact Profile (typical policy effect):
  Economy score:          −30 to −50 points
  Satisfaction score:     −20 to −35 points (unemployment, welfare strain)
  Cost efficiency:        −35 to −55 points (overruns, frozen budgets)
  Sustainability score:   −5 to −15 points (green investment cut first)
  Risk score:             −25 to −40 points (political reversal risk high)

Visual Identity:
  icon:    "TrendingDown"
  color:   "red"
  badge:   "RECESSION EVENT"
  emoji:   "💸"
```

### Crisis 3 — Global Pandemic

```
id:          "pandemic"
name:        "Global Pandemic"
severity:    CRITICAL
domain:      social
probability: rare (historical: once per generation)

Shock Parameters:
  Workforce impact:      30% of delivery workforce unavailable (illness, caregiving)
  Lockdowns:             Physical implementation halted 6–18 months
  Supply chains:         Construction materials delayed 12–24 months
  Public attention:      Policy overshadowed by crisis; political capital diverted
  Healthcare burden:     15–25% of social welfare budget diverted to health response

Stress Questions the LLM must answer:
  → Can digital components of the policy continue operating under lockdown?
  → Are the physical construction phases defensible or do they collapse?
  → Does the policy have community delivery mechanisms that bypass government bottlenecks?
  → Is the citizen welfare component of the policy resilient to healthcare system strain?
  → Does the policy itself help or hinder pandemic response?

Impact Profile (typical policy effect):
  Satisfaction score:     −20 to −40 points (service disruption, grief)
  Economy score:          −20 to −35 points (workforce loss, lockdown)
  Cost efficiency:        −25 to −40 points (delay costs, force majeure)
  Sustainability score:   −5 to +10 points (pollution drops during lockdown — mixed)
  Risk score:             −20 to −35 points (implementation delayed, momentum lost)

Visual Identity:
  icon:    "Biohazard"
  color:   "purple"
  badge:   "PANDEMIC EVENT"
  emoji:   "🦠"
```

### Crisis 4 — Infrastructure Collapse

```
id:          "infra_collapse"
name:        "Critical Infrastructure Collapse"
severity:    HIGH
domain:      infrastructure
probability: moderate (aging infrastructure globally)

Shock Parameters:
  Power grid failure:    Major blackouts covering 30–60% of the country for 2–6 weeks
  Telecoms disruption:   Internet and mobile connectivity degraded 40–70%
  Transport failure:     Highway and railway networks disrupted 3–9 months
  Water system failure:  Safe water access disrupted for 5–15M people
  Cascading effects:     Health, economic, and social systems all impacted simultaneously

Stress Questions the LLM must answer:
  → Is the policy's digital infrastructure vulnerable to power grid failure?
  → Does the policy have redundant delivery channels (offline, community, paper)?
  → Which policy components depend on transport networks that have just collapsed?
  → Does the policy's infrastructure investment actually help restore national infrastructure?
  → Can the physical implementation be reprioritised to repair collapsed systems first?

Impact Profile (typical policy effect):
  Cost efficiency:        −40 to −60 points (cascading implementation failure)
  Economy score:          −20 to −35 points (productivity collapse)
  Satisfaction score:     −25 to −40 points (basic services lost)
  Sustainability score:   −10 to −20 points (emergency fossil fuel use)
  Risk score:             −30 to −45 points (systemic implementation risk)

Visual Identity:
  icon:    "Building2"
  color:   "orange"
  badge:   "INFRA COLLAPSE"
  emoji:   "🏗️"
```

### Crisis 5 — Supply Chain Shortage

```
id:          "supply_shortage"
name:        "Severe Global Supply Chain Shortage"
severity:    HIGH
domain:      logistics
probability: moderate (geopolitical, climate, pandemic-triggered)

Shock Parameters:
  Critical materials:    Steel, cement, semiconductors, rare earths unavailable for 18–30 months
  Cost escalation:       Construction costs +60–120% due to scarcity
  Technology delays:     Hardware and device procurement delayed 12–24 months
  Energy costs:          +80–150% (fuel and electricity price spike)
  Contractor capacity:   Skilled contractors unavailable — committed to crisis response globally

Stress Questions the LLM must answer:
  → Which physical components of the policy are most materials-intensive?
  → Is the technology component dependent on semiconductors or imported hardware?
  → Can the policy be redesigned to use locally available materials at higher cost?
  → Does the policy have escalation clauses that protect against cost overruns?
  → Can Phase 1 be completed with domestic materials while waiting for supply chain recovery?

Impact Profile (typical policy effect):
  Cost efficiency:        −35 to −55 points (massive cost overruns)
  Economy score:          −10 to −25 points (inflationary, private sector also starved)
  Satisfaction score:     −10 to −20 points (delays, cost passed to citizens)
  Sustainability score:   0 to −15 points (alternatives may be less green)
  Risk score:             −20 to −35 points (delays create political pressure to cancel)

Visual Identity:
  icon:    "Package"
  color:   "amber"
  badge:   "SUPPLY CRISIS"
  emoji:   "📦"
```

---

## 2. The Three Measurements

### Measurement 1 — Resilience Score (0–100)

```
Definition: How much of the policy's core value is preserved when the crisis hits.
           Measures the DEFENSIVE strength of the policy design.

Key questions:
  1. What percentage of implementation steps can continue despite the crisis?
  2. Are the policy's critical dependencies (budget, workforce, infrastructure) protected?
  3. Does the policy's design have redundancy or single-points-of-failure?
  4. Does the chosen policy option have explicit crisis provisions?
  5. Were the crisis-domain minister's concerns addressed in the final policy?

Scoring rubric:
  90–100  FORTRESS       90%+ of policy components survive intact
  75–89   RESILIENT      75–89% survive; some delays but core outcomes preserved
  55–74   STABLE         55–74% survive; significant delays; some redesign needed
  35–54   FRAGILE        35–54% survive; major components fail; core outcomes at risk
  15–34   VULNERABLE     15–34% survive; most components fail; fundamental rethink needed
  0–14    CATASTROPHIC   <15% survive; policy effectively destroyed by crisis

Weight in composite: 50% (dominant factor — does the policy survive at all?)
```

### Measurement 2 — Recovery Speed (0–100)

```
Definition: How quickly can the policy resume and reach its original targets after the crisis.
           Measures the ADAPTIVE strength of the policy design.

Key questions:
  1. How many months does full recovery take (shorter = higher score)?
  2. Are there pre-built contingency mechanisms in the implementation plan?
  3. Does the policy have modular phases that can be paused and restarted?
  4. Is the political mandate durable enough to survive the crisis setback?
  5. Do the policy's success metrics have crisis-adjusted variants?

Recovery timeline → score mapping:
  0–6 months       → 90–100  (lightning recovery — policy barely disrupted)
  6–12 months      → 75–89   (fast recovery — back on track within a year)
  12–24 months     → 55–74   (moderate recovery — 1–2 years to resume)
  24–48 months     → 35–54   (slow recovery — 2–4 years of disruption)
  48–72 months     → 15–34   (very slow — effectively a generational setback)
  72+ months       → 0–14    (no recovery — policy abandoned after crisis)

Weight in composite: 30% (critical but secondary — survival first, speed second)
```

### Measurement 3 — Failure Points (qualitative + penalty score)

```
Definition: Specific structural weaknesses in the policy that the crisis would exploit.
           Produces a list of named failure points AND a penalty multiplier.

Failure point categories:
  SINGLE_POINT_OF_FAILURE  → One component whose loss kills the whole policy
  FUNDING_DEPENDENCY       → Policy budget that would be cut in this crisis type
  GEOGRAPHIC_CONCENTRATION → Policy delivery concentrated in crisis-hit area
  TECHNOLOGY_DEPENDENCY    → Critical tech that fails or becomes unavailable
  WORKFORCE_DEPENDENCY     → Key personnel who become unavailable in this crisis
  POLITICAL_FRAGILITY      → Components requiring political capital now consumed by crisis
  SUPPLY_DEPENDENCY        → Physical materials or services interrupted by this crisis

Failure point count → penalty score:
  0 failure points   → penalty = 0    (no structural weakness)
  1 failure point    → penalty = −5
  2 failure points   → penalty = −10
  3 failure points   → penalty = −18
  4 failure points   → penalty = −28
  5+ failure points  → penalty = −40  (cap — avoid crushing zero scores)

failure_penalty_score = max(0, 100 - |penalty|)
Weight in composite: 20%
```

---

## 3. Composite Resilience Score Formula

```
resilience_score = (
    resilience_dimension × 0.50 +
    recovery_speed       × 0.30 +
    failure_penalty      × 0.20
)

Range: 0–100
All sub-scores capped to [0, 100] before weighting.

Example:
  Crisis: Global Pandemic
  Policy: Technology-Led Urban Transformation

  resilience_dimension  = 71   (most digital components continue remotely)
  recovery_speed        = 62   (resumption estimated at 18 months → score 62)
  failure_points        = 3    → penalty score = 100 - 18 = 82

  resilience_score = (71 × 0.50) + (62 × 0.30) + (82 × 0.20)
                   = 35.5 + 18.6 + 16.4
                   = 70.5

  Band: RESILIENT — "Policy survives with managed adjustments."
```

### Resilience Score Bands

| Range | Band | Badge | Meaning |
|---|---|---|---|
| 90–100 | **FORTRESS** | `🏰 FORTRESS` | Crisis cannot derail this policy — may even accelerate it |
| 75–89 | **RESILIENT** | `🛡️ RESILIENT` | Policy survives intact with managed timeline adjustments |
| 55–74 | **STABLE** | `⚖️ STABLE` | Core survives; implementation significantly disrupted but recoverable |
| 35–54 | **FRAGILE** | `⚠️ FRAGILE` | Major components fail; policy requires fundamental crisis redesign |
| 15–34 | **VULNERABLE** | `🚨 VULNERABLE` | Policy mostly collapses; salvage of select components only |
| 0–14 | **CATASTROPHIC** | `💀 CATASTROPHIC` | Policy destroyed by this crisis; must be abandoned |

---

## 4. Data Models

### 4.1 Backend — Crisis Definition

```python
from dataclasses import dataclass
from typing import List
from enum import Enum

class CrisisDomain(str, Enum):
    ECONOMIC       = "economic"
    SOCIAL         = "social"
    INFRASTRUCTURE = "infrastructure"
    LOGISTICS      = "logistics"
    POLITICAL      = "political"

class CrisisSeverity(str, Enum):
    HIGH     = "high"
    CRITICAL = "critical"

@dataclass(frozen=True)
class CrisisEvent:
    id:          str
    name:        str
    severity:    CrisisSeverity
    domain:      CrisisDomain
    description: str                # 1–2 sentence summary
    shock_params: List[str]         # 5 concrete shock parameters
    stress_questions: List[str]     # 5 questions the LLM must answer
    typical_score_impacts: dict     # per-metric typical impact deltas
    icon:  str                      # Lucide icon name
    color: str                      # Tailwind color name
    badge: str                      # display label
    emoji: str
```

### 4.2 Backend — Crisis Pool

```python
BLACK_SWAN_POOL: List[CrisisEvent] = [
    CrisisEvent(
        id="flood",
        name="Catastrophic 500-Year Flood",
        severity=CrisisSeverity.CRITICAL,
        domain=CrisisDomain.INFRASTRUCTURE,
        description="Catastrophic flooding destroys core transport and water infrastructure. 3–8 million citizens displaced.",
        shock_params=[
            "Core transport and water infrastructure destroyed in key regions",
            "3–8 million citizens displaced; emergency housing required",
            "Immediate GDP contraction of 4–8% in affected regions",
            "Physical implementation stalled 18–36 months",
            "30–50% of policy budget diverted to emergency relief",
        ],
        stress_questions=[
            "Which parts of the policy are geographically concentrated in flood-risk zones?",
            "Does the policy infrastructure incorporate climate-resilient design standards?",
            "Can digital and non-physical components continue operating independently?",
            "Does the implementation plan include disaster recovery provisions?",
            "How does the policy's citizen welfare component handle mass displacement?",
        ],
        typical_score_impacts={
            "economy": (-25, -40), "sustainability": (-10, -20),
            "satisfaction": (-15, -30), "cost_efficiency": (-30, -50), "risk": (-20, -35),
        },
        icon="Waves", color="sky", badge="FLOOD EVENT", emoji="🌊",
    ),
    CrisisEvent(
        id="recession",
        name="Global Economic Recession",
        severity=CrisisSeverity.CRITICAL,
        domain=CrisisDomain.ECONOMIC,
        description="GDP contracts 12–18% over 18 months. Government forced into austerity; all non-essential spending cut.",
        shock_params=[
            "GDP contraction of 12–18% over 18 months",
            "Unemployment spikes +8–15 percentage points nationally",
            "Government forced to cut all non-essential spending 25–40%",
            "Foreign investment withdraws; borrowing costs spike significantly",
            "Austerity demands compete directly with policy implementation budgets",
        ],
        stress_questions=[
            "Is the policy funded from recurrent budget or ring-fenced capital?",
            "Do the policy's economic components accelerate recovery or deepen recession?",
            "Which implementation owners can maintain delivery under a hiring freeze?",
            "Are implementation contracts cancellable or do they lock in costs?",
            "Does the policy create countercyclical stimulus or consume scarce resources?",
        ],
        typical_score_impacts={
            "economy": (-30, -50), "satisfaction": (-20, -35),
            "cost_efficiency": (-35, -55), "sustainability": (-5, -15), "risk": (-25, -40),
        },
        icon="TrendingDown", color="red", badge="RECESSION EVENT", emoji="💸",
    ),
    CrisisEvent(
        id="pandemic",
        name="Global Pandemic",
        severity=CrisisSeverity.CRITICAL,
        domain=CrisisDomain.SOCIAL,
        description="Global pandemic triggers lockdowns for 6–18 months. 30% of delivery workforce unavailable.",
        shock_params=[
            "30% of delivery workforce unavailable due to illness and caregiving",
            "Physical implementation halted under lockdown for 6–18 months",
            "Construction materials delayed 12–24 months from supply chain shock",
            "Political capital diverted entirely to health crisis management",
            "15–25% of social welfare budget redirected to emergency health response",
        ],
        stress_questions=[
            "Can digital components continue operating entirely under lockdown?",
            "Are the physical construction phases defensible or do they collapse entirely?",
            "Does the policy have community delivery mechanisms bypassing government bottlenecks?",
            "Is the citizen welfare component resilient to healthcare system overload?",
            "Does the policy itself assist or impede the pandemic response?",
        ],
        typical_score_impacts={
            "satisfaction": (-20, -40), "economy": (-20, -35),
            "cost_efficiency": (-25, -40), "sustainability": (-5, +10), "risk": (-20, -35),
        },
        icon="Biohazard", color="purple", badge="PANDEMIC EVENT", emoji="🦠",
    ),
    CrisisEvent(
        id="infra_collapse",
        name="Critical Infrastructure Collapse",
        severity=CrisisSeverity.HIGH,
        domain=CrisisDomain.INFRASTRUCTURE,
        description="Power grid and telecoms fail across 30–60% of the country. Transport and water systems disrupted simultaneously.",
        shock_params=[
            "Major blackouts covering 30–60% of the country for 2–6 weeks",
            "Internet and mobile connectivity degraded 40–70% nationally",
            "Highway and railway networks disrupted for 3–9 months",
            "Safe water access disrupted for 5–15 million people",
            "Cascading failures across health, economic, and social systems simultaneously",
        ],
        stress_questions=[
            "Is the policy's digital infrastructure vulnerable to power grid failure?",
            "Does the policy have redundant delivery channels (offline, community, paper-based)?",
            "Which policy components depend on transport networks now collapsed?",
            "Does the policy's infrastructure investment help restore national systems?",
            "Can physical implementation be reprioritised to repair collapsed infrastructure first?",
        ],
        typical_score_impacts={
            "cost_efficiency": (-40, -60), "economy": (-20, -35),
            "satisfaction": (-25, -40), "sustainability": (-10, -20), "risk": (-30, -45),
        },
        icon="Building2", color="orange", badge="INFRA COLLAPSE", emoji="🏗️",
    ),
    CrisisEvent(
        id="supply_shortage",
        name="Severe Global Supply Chain Shortage",
        severity=CrisisSeverity.HIGH,
        domain=CrisisDomain.LOGISTICS,
        description="Steel, cement, semiconductors, and rare earths unavailable for 18–30 months. Construction costs +60–120%.",
        shock_params=[
            "Steel, cement, semiconductors, rare earths unavailable for 18–30 months",
            "Construction costs increase 60–120% due to material scarcity",
            "Technology hardware procurement delayed 12–24 months globally",
            "Energy costs spike 80–150% due to fuel and electricity price shock",
            "Skilled contractors unavailable — committed to global crisis response",
        ],
        stress_questions=[
            "Which physical components of the policy are most materials-intensive?",
            "Is the technology component dependent on imported semiconductors or hardware?",
            "Can the policy be redesigned using locally available materials at higher cost?",
            "Does the implementation plan have cost escalation protection clauses?",
            "Can Phase 1 complete with domestic materials while awaiting supply recovery?",
        ],
        typical_score_impacts={
            "cost_efficiency": (-35, -55), "economy": (-10, -25),
            "satisfaction": (-10, -20), "sustainability": (0, -15), "risk": (-20, -35),
        },
        icon="Package", color="amber", badge="SUPPLY CRISIS", emoji="📦",
    ),
]
```

### 4.3 Backend — BlackSwanResult TypedDict

```python
class FailurePoint(TypedDict):
    category:    str        # one of the 7 FailurePoint categories
    description: str        # specific named weakness in this policy
    severity:    str        # "minor" | "moderate" | "severe" | "fatal"

class BlackSwanResult(TypedDict):
    # Crisis identity
    crisis_id:          str             # "flood" | "recession" | "pandemic" | ...
    crisis_name:        str             # full display name
    crisis_domain:      str             # CrisisDomain value
    crisis_severity:    str             # "high" | "critical"

    # Three measurement outputs
    resilience_narrative:   str         # 2–3 sentences: what survives?
    resilience_raw:         float       # 0–100

    recovery_narrative:     str         # 2–3 sentences: how does recovery unfold?
    recovery_months:        int         # estimated months to full recovery
    recovery_speed:         float       # 0–100 (derived from months)

    failure_points:         List[FailurePoint]  # named structural weaknesses
    failure_count:          int
    failure_penalty_score:  float       # 0–100 (penalised by failure count)

    # Composite output
    resilience_score:       float       # final weighted composite (0–100)
    resilience_band:        str         # fortress|resilient|stable|fragile|vulnerable|catastrophic

    # Narrative summary
    impact_summary:         str         # 3-sentence overall impact narrative
    survival_probability:   str         # "high" | "moderate" | "low" | "near-zero"

    # Metadata
    _elapsed_ms:  int
    _timestamp:   str
```

### 4.4 LLM Output Schema

```json
{
  "crisis_id":   "<flood|recession|pandemic|infra_collapse|supply_shortage>",
  "crisis_name": "<full crisis name>",

  "resilience_narrative": "<2–3 sentence analysis: what percentage of policy components survive and why>",
  "resilience_raw": "<0–100 integer: how much of the policy's core value is preserved>",

  "recovery_narrative": "<2–3 sentences: how and when does the policy resume after the crisis passes>",
  "recovery_months":    "<integer: estimated months to return to original implementation trajectory>",

  "failure_points": [
    {
      "category":    "<SINGLE_POINT_OF_FAILURE|FUNDING_DEPENDENCY|GEOGRAPHIC_CONCENTRATION|TECHNOLOGY_DEPENDENCY|WORKFORCE_DEPENDENCY|POLITICAL_FRAGILITY|SUPPLY_DEPENDENCY>",
      "description": "<specific named weakness in this policy exposed by this crisis>",
      "severity":    "<minor|moderate|severe|fatal>"
    }
  ],

  "impact_summary": "<3-sentence holistic narrative: crisis strikes, policy responds, outcome>",
  "survival_probability": "<high|moderate|low|near-zero>"
}
```

### 4.5 Backend — Database Columns (FinalReport additions)

```python
# In app/models/session.py — FinalReport table
# ── Black Swan Engine (enhanced) ──────────────────────────────
black_swan_crisis_id     = Column(String(50),  nullable=True)   # crisis id key
black_swan_crisis        = Column(String(200), nullable=True)   # full crisis name
black_swan_domain        = Column(String(50),  nullable=True)   # crisis domain
black_swan_severity      = Column(String(20),  nullable=True)   # high | critical

# Three measurement outputs
resilience_raw           = Column(Float, nullable=True)         # 0–100
recovery_speed           = Column(Float, nullable=True)         # 0–100
recovery_months          = Column(Integer, nullable=True)       # estimated months
failure_count            = Column(Integer, nullable=True)       # number of failure points
failure_penalty_score    = Column(Float, nullable=True)         # 0–100

# Final output
resilience_score         = Column(Float, nullable=True)         # composite 0–100
resilience_band          = Column(String(20), nullable=True)    # band label
black_swan_impact        = Column(Text, nullable=True)          # 3-sentence narrative
survival_probability     = Column(String(20), nullable=True)    # high|moderate|low|near-zero
failure_points           = Column(JSONB, nullable=True)         # List[FailurePoint]
```

### 4.6 Frontend TypeScript Interface

```typescript
// packages/shared-types/src/index.ts

export type CrisisId = "flood" | "recession" | "pandemic" | "infra_collapse" | "supply_shortage";
export type CrisisDomain = "economic" | "social" | "infrastructure" | "logistics" | "political";
export type CrisisSeverity = "high" | "critical";
export type ResilienceBand = "fortress" | "resilient" | "stable" | "fragile" | "vulnerable" | "catastrophic";
export type SurvivalProbability = "high" | "moderate" | "low" | "near-zero";
export type FailureCategory =
  | "SINGLE_POINT_OF_FAILURE"
  | "FUNDING_DEPENDENCY"
  | "GEOGRAPHIC_CONCENTRATION"
  | "TECHNOLOGY_DEPENDENCY"
  | "WORKFORCE_DEPENDENCY"
  | "POLITICAL_FRAGILITY"
  | "SUPPLY_DEPENDENCY";
export type FailureSeverity = "minor" | "moderate" | "severe" | "fatal";

export interface FailurePoint {
  category:    FailureCategory;
  description: string;
  severity:    FailureSeverity;
}

export interface BlackSwanResult {
  // Crisis identity
  crisis_id:     CrisisId;
  crisis_name:   string;
  crisis_domain: CrisisDomain;
  crisis_severity: CrisisSeverity;

  // Three measurements
  resilience_narrative: string;
  resilience_raw:       number;      // 0–100

  recovery_narrative:   string;
  recovery_months:      number;
  recovery_speed:       number;      // 0–100

  failure_points:       FailurePoint[];
  failure_count:        number;
  failure_penalty_score: number;     // 0–100

  // Final output
  resilience_score:    number;       // 0–100 composite
  resilience_band:     ResilienceBand;
  impact_summary:      string;       // 3-sentence narrative
  survival_probability: SurvivalProbability;
}

// UI metadata per crisis type
export interface CrisisMeta {
  id:       CrisisId;
  name:     string;
  domain:   CrisisDomain;
  severity: CrisisSeverity;
  icon:     string;          // Lucide icon name
  color:    string;          // Tailwind color
  badge:    string;
  emoji:    string;
}

export const CRISIS_META: Record<CrisisId, CrisisMeta> = {
  flood:           { id: "flood",           name: "Catastrophic 500-Year Flood",         domain: "infrastructure", severity: "critical", icon: "Waves",       color: "sky",    badge: "FLOOD EVENT",     emoji: "🌊" },
  recession:       { id: "recession",       name: "Global Economic Recession",            domain: "economic",       severity: "critical", icon: "TrendingDown",color: "red",    badge: "RECESSION EVENT", emoji: "💸" },
  pandemic:        { id: "pandemic",        name: "Global Pandemic",                      domain: "social",         severity: "critical", icon: "Biohazard",   color: "purple", badge: "PANDEMIC EVENT",  emoji: "🦠" },
  infra_collapse:  { id: "infra_collapse",  name: "Critical Infrastructure Collapse",     domain: "infrastructure", severity: "high",     icon: "Building2",   color: "orange", badge: "INFRA COLLAPSE",  emoji: "🏗️" },
  supply_shortage: { id: "supply_shortage", name: "Severe Global Supply Chain Shortage",  domain: "logistics",      severity: "high",     icon: "Package",     color: "amber",  badge: "SUPPLY CRISIS",   emoji: "📦" },
};

// Band visual config
export const RESILIENCE_BAND_META: Record<ResilienceBand, {
  label: string; color: string; icon: string; description: string
}> = {
  fortress:      { label: "FORTRESS",      color: "emerald", icon: "Shield",       description: "Crisis cannot derail this policy — may even accelerate it" },
  resilient:     { label: "RESILIENT",     color: "green",   icon: "ShieldCheck",  description: "Policy survives with managed timeline adjustments" },
  stable:        { label: "STABLE",        color: "blue",    icon: "ShieldHalf",   description: "Core survives; implementation significantly disrupted but recoverable" },
  fragile:       { label: "FRAGILE",       color: "yellow",  icon: "ShieldAlert",  description: "Major components fail; fundamental crisis redesign required" },
  vulnerable:    { label: "VULNERABLE",    color: "orange",  icon: "ShieldOff",    description: "Policy mostly collapses; salvage of select components only" },
  catastrophic:  { label: "CATASTROPHIC",  color: "red",     icon: "ShieldX",      description: "Policy destroyed by this crisis — must be abandoned" },
};
```

---

## 5. Engine Architecture

### 5.1 Node Execution Flow

```python
async def node_black_swan_engine(state: GovernanceState) -> Dict[str, Any]:
    """
    Enhanced Black Swan Engine — 3 measurement dimensions + composite score.
    """
    report  = state.get("final_report", {})
    problem = state["problem"]

    # ── Step 1: Select random crisis ──────────────────────────────
    crisis = random.choice(BLACK_SWAN_POOL)

    # ── Step 2: Build context block ───────────────────────────────
    chosen_option      = report.get("chosen_option", "Unknown")
    rationale          = report.get("rationale", "")[:500]
    risks_mitigations  = json.dumps(report.get("risks_and_mitigations", {}))[:400]
    impl_steps         = json.dumps(report.get("implementation_steps", []))[:400]

    # ── Step 3: Invoke LLM with structured 3-dimension prompt ─────
    prompt = build_black_swan_prompt(
        crisis=crisis,
        chosen_option=chosen_option,
        rationale=rationale,
        risks_mitigations=risks_mitigations,
        impl_steps=impl_steps,
    )

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_FLASH_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.6,
        max_output_tokens=2048,
    )

    t0       = time.monotonic()
    response = await llm.ainvoke([
        SystemMessage(content=BLACK_SWAN_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    raw = extract_json(str(response.content))

    # ── Step 4: Compute composite resilience score ─────────────────
    result = compute_resilience_score(raw, crisis)
    result["_elapsed_ms"] = elapsed_ms
    result["_timestamp"]  = _ts()

    return {
        "black_swan_results": result,
        "current_phase": "completed",
    }
```

### 5.2 System Prompt

```python
BLACK_SWAN_SYSTEM_PROMPT = """You are the TITAN Black Swan Resilience Engine.

Your job is to stress-test a finalized governance policy against a catastrophic, 
unpredictable crisis event and produce a structured resilience assessment.

You measure three dimensions:

1. RESILIENCE (0–100):
   How much of the policy's core value is preserved when the crisis hits?
   Higher score = more policy components survive intact.

2. RECOVERY SPEED (0–100, derived from recovery_months):
   How quickly can the policy return to its original trajectory after the crisis?
   0–6 months   → 90–100
   6–12 months  → 75–89
   12–24 months → 55–74
   24–48 months → 35–54
   48–72 months → 15–34
   72+ months   → 0–14

3. FAILURE POINTS (structural weaknesses exploited by this crisis):
   Name specific, concrete weaknesses in THIS policy exposed by THIS crisis.
   Categories: SINGLE_POINT_OF_FAILURE | FUNDING_DEPENDENCY | 
   GEOGRAPHIC_CONCENTRATION | TECHNOLOGY_DEPENDENCY | 
   WORKFORCE_DEPENDENCY | POLITICAL_FRAGILITY | SUPPLY_DEPENDENCY

RULES:
- Be specific. Name the policy component that fails, not just "implementation may be disrupted."
- Be honest. If the policy has no provisions for this crisis type, say so.
- Be proportionate. Not every policy collapses in every crisis.
- Acknowledge when crisis-domain minister's concerns were addressed.

OUTPUT: Valid JSON only. No commentary outside the schema."""
```

### 5.3 Per-Crisis Prompt Builder

```python
def build_black_swan_prompt(crisis: CrisisEvent, chosen_option: str,
                             rationale: str, risks_mitigations: str,
                             impl_steps: str) -> str:
    return f"""FINALIZED POLICY INFORMATION:
Chosen Option:    {chosen_option}
Rationale:        {rationale}
Risk Mitigations: {risks_mitigations}
Implementation:   {impl_steps}

BLACK SWAN EVENT: {crisis.name}
Severity:  {crisis.severity.value.upper()}
Domain:    {crisis.domain.value}

CRISIS PARAMETERS:
{chr(10).join(f"  • {p}" for p in crisis.shock_params)}

QUESTIONS YOU MUST ADDRESS:
{chr(10).join(f"  {i+1}. {q}" for i, q in enumerate(crisis.stress_questions))}

Analyze how this policy survives this crisis.
Return ONLY valid JSON matching this schema:
{BLACK_SWAN_OUTPUT_SCHEMA}"""
```

### 5.4 Score Computation (Post-LLM)

```python
def compute_resilience_score(raw: Dict[str, Any], crisis: CrisisEvent) -> BlackSwanResult:
    """
    Derive composite resilience_score from 3 raw LLM outputs.
    """
    # ── Dimension 1: Resilience ────────────────────────────────
    resilience_raw = float(raw.get("resilience_raw", 50))
    resilience_raw = max(0.0, min(100.0, resilience_raw))

    # ── Dimension 2: Recovery Speed ───────────────────────────
    recovery_months = int(raw.get("recovery_months", 24))
    if   recovery_months <= 6:   recovery_speed = 95.0
    elif recovery_months <= 12:  recovery_speed = 82.0
    elif recovery_months <= 24:  recovery_speed = 65.0
    elif recovery_months <= 48:  recovery_speed = 45.0
    elif recovery_months <= 72:  recovery_speed = 25.0
    else:                        recovery_speed = 7.0

    # ── Dimension 3: Failure Points ───────────────────────────
    failure_points = raw.get("failure_points", [])
    failure_count  = len(failure_points)
    penalties      = {0: 0, 1: 5, 2: 10, 3: 18, 4: 28}
    penalty        = penalties.get(failure_count, 40)  # 5+ → cap at 40
    failure_penalty_score = max(0.0, 100.0 - penalty)

    # ── Composite ─────────────────────────────────────────────
    composite = (
        resilience_raw      * 0.50 +
        recovery_speed      * 0.30 +
        failure_penalty_score * 0.20
    )
    composite = round(max(0.0, min(100.0, composite)), 2)

    # ── Band ──────────────────────────────────────────────────
    if   composite >= 90: band = "fortress"
    elif composite >= 75: band = "resilient"
    elif composite >= 55: band = "stable"
    elif composite >= 35: band = "fragile"
    elif composite >= 15: band = "vulnerable"
    else:                 band = "catastrophic"

    return BlackSwanResult(
        crisis_id=crisis.id,
        crisis_name=crisis.name,
        crisis_domain=crisis.domain.value,
        crisis_severity=crisis.severity.value,
        resilience_narrative=raw.get("resilience_narrative", ""),
        resilience_raw=resilience_raw,
        recovery_narrative=raw.get("recovery_narrative", ""),
        recovery_months=recovery_months,
        recovery_speed=recovery_speed,
        failure_points=failure_points,
        failure_count=failure_count,
        failure_penalty_score=failure_penalty_score,
        resilience_score=composite,
        resilience_band=band,
        impact_summary=raw.get("impact_summary", ""),
        survival_probability=raw.get("survival_probability", "moderate"),
    )
```

### 5.5 Fallback

```python
def _fallback_black_swan(crisis: CrisisEvent) -> BlackSwanResult:
    return {
        "crisis_id":              crisis.id,
        "crisis_name":            crisis.name,
        "crisis_domain":          crisis.domain.value,
        "crisis_severity":        crisis.severity.value,
        "resilience_narrative":   "Resilience analysis unavailable due to engine error.",
        "resilience_raw":         50.0,
        "recovery_narrative":     "Recovery data unavailable.",
        "recovery_months":        24,
        "recovery_speed":         65.0,
        "failure_points":         [],
        "failure_count":          0,
        "failure_penalty_score":  100.0,
        "resilience_score":       65.0,
        "resilience_band":        "stable",
        "impact_summary":         "Black Swan analysis could not be completed.",
        "survival_probability":   "moderate",
        "_fallback":              True,
    }
```

---

## 6. Visual Presentation Spec

### 6.1 Black Swan Reveal Sequence

```
1. "Black Swan Event" section header fades in     (300ms)
2. Crisis card FLIPS in from left                 (500ms)
3. Crisis emoji pulses twice                       (600ms × 2)
4. Crisis name and domain badge fade in            (200ms)
5. Impact summary text streams in                  (typewriter, 50ms/char)

6. Three measurement rows fill simultaneously:
   → Resilience bar: 0 → resilience_raw           (700ms ease-out)
   → Recovery bar: 0 → recovery_speed             (700ms ease-out, +100ms delay)
   → Failure points list reveals: stagger 100ms   (150ms × failure_count)

7. Composite score counts from 0 → resilience_score (800ms, large number)
8. Band badge stamps in (scale 2→1)               (400ms spring)
9. Band-specific glow activates on card border:
   fortress    → emerald glow
   resilient   → green glow
   stable      → blue glow
   fragile     → yellow glow
   vulnerable  → orange glow
   catastrophic → red pulse glow (repeating)
```

### 6.2 Black Swan Card Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ☠ BLACK SWAN EVENT                RESILIENCE SCORE         │
│                                                              │
│  🌊  Catastrophic 500-Year Flood                   70.5     │
│       CRITICAL   ·   Infrastructure Domain         RESILIENT │
│──────────────────────────────────────────────────────────────│
│  "The Technology-Led Transformation demonstrates moderate    │
│   resilience against catastrophic flooding. Digital service  │
│   delivery continues remotely for 70% of citizens; however,  │
│   the physical infrastructure phase stalls for 24 months."   │
│──────────────────────────────────────────────────────────────│
│  RESILIENCE          ███████████████████░░░░  76 / 100       │
│  RECOVERY SPEED      ████████████████░░░░░░░  62 / 100       │
│  FAILURE PENALTY     ███████████████████░░░░  82 / 100       │
│──────────────────────────────────────────────────────────────│
│  IDENTIFIED FAILURE POINTS                        3 found    │
│                                                              │
│  ⚠ GEOGRAPHIC_CONCENTRATION    [moderate]                   │
│    "Physical construction sites concentrated in flood-zone   │
│     districts A, B, C — all would be inundated."            │
│                                                              │
│  ⚠ FUNDING_DEPENDENCY          [severe]                     │
│    "30% of Year 2 budget allocated to infrastructure phases  │
│     that become undeliverable under crisis conditions."      │
│                                                              │
│  ● TECHNOLOGY_DEPENDENCY       [minor]                      │
│    "Data centers in coastal Zone 3 require backup power      │
│     planning — currently absent from the implementation plan."│
│──────────────────────────────────────────────────────────────│
│  ESTIMATED RECOVERY    18–24 months                          │
│  SURVIVAL PROBABILITY  MODERATE                              │
│──────────────────────────────────────────────────────────────│
│  composite:  (76 × 0.50) + (62 × 0.30) + (82 × 0.20)       │
│            = 38.0 + 18.6 + 16.4  =  73.0  RESILIENT         │
└──────────────────────────────────────────────────────────────┘
```

### 6.3 Failure Point Severity Visual

```typescript
const FAILURE_SEVERITY_STYLE: Record<FailureSeverity, {
  icon: string; color: string; label: string
}> = {
  minor:    { icon: "●",  color: "text-blue-400",   label: "Minor" },
  moderate: { icon: "⚠",  color: "text-yellow-400", label: "Moderate" },
  severe:   { icon: "⚠",  color: "text-orange-400", label: "Severe" },
  fatal:    { icon: "✕",  color: "text-red-500",    label: "FATAL" },
};

// Fatal failure points receive full red card treatment:
//   background: bg-red-950/40
//   border: border-red-500/60
//   pulse animation: animate-pulse (once on reveal)
```

### 6.4 Resilience Score — Large Display

```
╔══════════════════════════════════════╗
║                                      ║
║   RESILIENCE SCORE                   ║
║                                      ║
║         70.5                         ║
║        ────────                      ║
║        RESILIENT                     ║
║                                      ║
║   ████████████████████░░░░  70.5     ║
║                                      ║
╚══════════════════════════════════════╝

Score  Color mapping:
  0–14    → text-red-500    bg-red-950/40    (CATASTROPHIC)
  15–34   → text-orange-500 bg-orange-950/40 (VULNERABLE)
  35–54   → text-yellow-500 bg-yellow-950/40 (FRAGILE)
  55–74   → text-blue-500   bg-blue-950/40   (STABLE)
  75–89   → text-green-500  bg-green-950/40  (RESILIENT)
  90–100  → text-emerald-400 bg-emerald-950/40 (FORTRESS)
```

### 6.5 SSE Events

```
SSE event: "black_swan_selected"
  payload: { crisis_id, crisis_name, crisis_domain, crisis_severity }
  UI: crisis reveal animation → show name, domain, emoji, badge

SSE event: "session_complete"
  payload: { ..., black_swan: BlackSwanResult }
  UI: full Black Swan card renders with all 3 measurements + score
```

---

## 7. PM Synthesis Integration

The Prime Minister's final policy prompt is enriched with the Black Swan result so its `risks_and_mitigations` can pre-address identified failure points:

```
[NOTE: This runs AFTER PM synthesis. The Black Swan result is appended
 to the final_report row in the DB, not re-run through the PM.]

However: if a second "hardened policy" feature is ever added,
the PM would receive:
  - identified failure points list
  - resilience_band
  → and be asked: "Revise your implementation plan to address these specific 
    failure points and improve the resilience score."

This is the scale path — not in MVP.
```

---

*TITAN Black Swan Engine — because every policy must survive tomorrow's news.*
