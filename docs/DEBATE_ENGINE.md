# TITAN — Debate Engine Design

> **5 phases. 7 agents. 1 binding decision.**
> The debate engine is the core of TITAN — where independent analyses collide,
> get stress-tested by the Opposition, and resolve into a democratic mandate.

---

## Full Debate Flow

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   PROBLEM SUBMITTED                                                          ║
║          │                                                                   ║
║          ▼                                                                   ║
║  ┌───────────────────┐                                                       ║
║  │  PHASE 0          │  Input validation · context enrichment                ║
║  │  INTAKE           │  status → pending → analyzing                         ║
║  └────────┬──────────┘                                                       ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 1 — PROPOSAL PHASE                                     │           ║
║  │  6 ministers analyze in parallel (LangGraph Send fan-out)     │           ║
║  │                                                               │           ║
║  │  📈 Economic   💻 Technology   🏗️ Infrastructure              │           ║
║  │  👥 Citizen    🌿 Environment  🛡️ Opposition                  │           ║
║  │                                                               │           ║
║  │  Each → MinisterOutput {assessment, solutions, red_lines}     │           ║
║  │  status → analyzing                                           │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │ aggregate_analyses: merge + extract policy_options                ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 2 — DEBATE ROUND (Proposal Presentations)              │           ║
║  │  5 ministers speak sequentially (can see prior arguments)     │           ║
║  │                                                               │           ║
║  │  📈 → 💻 → 🏗️ → 👥 → 🌿  (Opposition withheld)              │           ║
║  │                                                               │           ║
║  │  Each → DebateArgument {argument, concessions, new_evidence}  │           ║
║  │  status → debating                                            │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 3 — OPPOSITION CHALLENGE                               │           ║
║  │  Opposition reads full corpus → surgical attack               │           ║
║  │                                                               │           ║
║  │  🛡️ Opposition: targets strongest 1–2 proposals by name      │           ║
║  │       → DebateArgument {phase: "opposition_attack"}           │           ║
║  │  status → debating (opposition)                               │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 4 — REBUTTAL                                           │           ║
║  │  5 ministers rebut in parallel (independent of each other)    │           ║
║  │                                                               │           ║
║  │  📈 ║ 💻 ║ 🏗️ ║ 👥 ║ 🌿  (parallel asyncio.gather)          │           ║
║  │                                                               │           ║
║  │  Each → DebateArgument {phase: "rebuttal", concessions}       │           ║
║  │  status → debating (rebuttal)                                 │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 5 — DEMOCRATIC VOTE                                    │           ║
║  │  All 6 ministers vote in parallel (LangGraph Send fan-out)    │           ║
║  │                                                               │           ║
║  │  Each → VoteRecord {voted_option, confidence_score, veto}     │           ║
║  │  tally_votes: count + consensus_level + weighted_confidence   │           ║
║  │  status → voting                                              │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 6 — SIMULATION                                         │           ║
║  │  Simulation Agent tests winning option across 4 futures       │           ║
║  │  status → simulating                                          │           ║
║  └────────┬──────────────────────────────────────────────────────┘           ║
║           │                                                                   ║
║           ▼                                                                   ║
║  ┌───────────────────────────────────────────────────────────────┐           ║
║  │  PHASE 7 — PRIME MINISTER DECISION                            │           ║
║  │  Gemini Pro reads all corpus → FinalPolicy JSON               │           ║
║  │  + Black Swan resilience engine                               │           ║
║  │  status → synthesizing → completed                            │           ║
║  └───────────────────────────────────────────────────────────────┘           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 1. Debate States

### 1.1 Session Status Enum

```typescript
type DebateStatus =
  | "pending"          // Session created, not started
  | "analyzing"        // Phase 1: 6 ministers analyzing in parallel
  | "debating"         // Phase 2: Proposal presentations (sequential)
  | "challenging"      // Phase 3: Opposition attack (dedicated)
  | "rebutting"        // Phase 4: Ministerial rebuttals (parallel)
  | "voting"           // Phase 5: Democratic vote (parallel)
  | "simulating"       // Phase 6: Simulation agent running futures
  | "synthesizing"     // Phase 7: Prime Minister synthesis
  | "completed"        // Terminal: full report available
  | "failed"           // Terminal: error in pipeline
```

### 1.2 Phase State Machine

```
pending
  │ POST /api/v1/sessions
  ▼
analyzing ──── (6 parallel LLM calls) ──── if error ──► failed
  │
  ▼ all 6 complete → aggregate_analyses
debating ──── (5 sequential) ──── if error ──► failed
  │
  ▼ debate_round complete
challenging ─── (1 dedicated attack) ──── if error ──► failed
  │
  ▼ opposition_attack complete
rebutting ──── (5 parallel) ──── if error ──► failed
  │
  ▼ rebuttals complete
voting ──── (6 parallel) → tally_votes ──── if error ──► failed
  │
  ▼ winner resolved
simulating ──── (4 parallel futures) ──── if error ──► failed
  │
  ▼ simulation_results ready
synthesizing ──── (1 Gemini Pro call) ──── if error ──► failed
  │
  ▼ final_report + black_swan complete
completed
```

### 1.3 Phase Metadata (stored in `GovernanceState.metadata`)

```python
{
  "started_at":         "2026-06-13T06:00:00Z",
  "problem_length":     247,
  "cabinet_size":       6,

  # Set when analysis completes
  "analysis_completed_at": "2026-06-13T06:01:12Z",
  "analysis_duration_ms":  72000,

  # Set when debate completes
  "debate_completed_at":   "2026-06-13T06:02:30Z",
  "debate_word_count":     1240,

  # Set when votes tallied
  "winning_option":     "Technology-Led Transformation",
  "vote_percentage":    83.3,
  "consensus_level":    "high",   # low | moderate | high
  "total_votes":        6,
  "winning_votes":      5,

  # Set at completion
  "completed_at":       "2026-06-13T06:04:45Z",
  "total_duration_ms":  285000
}
```

---

## 2. Message Schema

### 2.1 Core Debate Message Types

```typescript
// ─── Phase Label ───────────────────────────────────────────────
type DebatePhase =
  | "presentation"        // Phase 1 outputs recorded as debate entries
  | "debate"              // Phase 2 proposal presentations
  | "opposition_attack"   // Phase 3 dedicated challenge
  | "rebuttal"            // Phase 4 ministerial defence

type MessageType =
  | "analysis"            // MinisterOutput (Phase 1)
  | "proposal"            // Initial position (Phase 2)
  | "attack"              // Opposition strike (Phase 3)
  | "rebuttal"            // Defence argument (Phase 4)
  | "vote"                // VoteRecord (Phase 5)
  | "verdict"             // FinalPolicy (Phase 7)
  | "system"              // Phase transition notification
```

### 2.2 DebateMessage (Frontend Canonical Type)

```typescript
// Complete, unified message object for UI rendering
interface DebateMessage {
  // Identity
  id:            string          // UUID
  session_id:    string
  sequence:      number          // monotonic order index for timeline rendering

  // Authorship
  author_role:   MinisterRole
  author_meta:   MinisterMeta    // from MINISTER_META — color, icon, gradient, title

  // Content
  type:          MessageType
  phase:         DebatePhase
  round_number:  number          // 0 = analysis, 1 = debate/attack, 2 = rebuttal

  // Payload
  content:       string          // The main argument / analysis text
  key_points?:   string[]        // Bullet points (analysis only)
  solutions?:    string[]        // Proposed solutions (analysis only)
  concessions?:  string[]        // Points conceded (debate/rebuttal)
  evidence?:     string[]        // New evidence introduced
  targets?:      MinisterRole[]  // Ministers being challenged (attack only)

  // Signals
  sentiment:     "constructive" | "challenging" | "conceding" | "neutral"
  intensity:     1 | 2 | 3       // 1=mild, 2=moderate, 3=confrontational
  word_count:    number

  // Timing
  timestamp:     string          // ISO 8601
  duration_ms?:  number          // LLM call duration
}
```

### 2.3 Backend DebateArgument (Python TypedDict)

```python
class DebateArgument(TypedDict):
    # Identity
    agent_role:          str       # e.g. "economic_minister"
    round_number:        int       # 0=presentation, 1=debate/attack, 2=rebuttal
    phase:               str       # "debate" | "opposition_attack" | "rebuttal"

    # Content
    argument:            str       # 150–250 words
    attacking_roles:     List[str] # which ministers are being challenged
    defending_positions: List[str] # positions being protected
    concessions:         List[str] # points conceded to other ministers
    new_evidence:        List[str] # new data points introduced

    # Metadata
    word_count:          int
    _timestamp:          str       # ISO 8601
    _elapsed_ms:         int       # LLM latency
```

### 2.4 Phase Transition System Messages

```typescript
// Injected into the debate feed by the frontend (not from backend)
// Driven by SSE phase-change events

interface SystemMessage {
  type:      "system"
  event:     SSEEventType
  label:     string           // Human-readable phase label
  icon:      string           // Lucide icon name
  color:     string           // Tailwind color class
  timestamp: string
}

// Examples:
{ event: "debate_started",   label: "Cabinet Debate Open",          icon: "Gavel",    color: "text-blue-400" }
{ event: "debate_argument",  label: "Opposition Taking The Floor",   icon: "ShieldAlert", color: "text-red-400" }
{ event: "voting_started",   label: "Democratic Vote In Progress",   icon: "Vote",     color: "text-amber-400" }
{ event: "synthesis_started",label: "Prime Minister Deliberating",   icon: "Crown",    color: "text-yellow-400" }
{ event: "session_complete", label: "Final Policy Issued",           icon: "CheckCircle2", color: "text-green-400" }
```

### 2.5 Complete SSE Event → DebateMessage Mapping

| SSE Event | Message Type | Author | Content Source |
|---|---|---|---|
| `analysis_complete` | `analysis` | minister_role | `MinisterOutput.situation_assessment` |
| `debate_argument` (phase=debate) | `proposal` | agent_role | `DebateArgument.argument` |
| `debate_argument` (phase=opposition_attack) | `attack` | `opposition_minister` | `DebateArgument.argument` |
| `debate_argument` (phase=rebuttal) | `rebuttal` | agent_role | `DebateArgument.argument` |
| `vote_cast` | `vote` | agent_role | `VoteRecord` |
| `synthesis_complete` | `verdict` | `prime_minister` | `FinalPolicy.executive_summary` |

---

## 3. Voting Mechanism

### 3.1 VoteRecord Schema (Backend)

```python
class VoteRecord(TypedDict):
    agent_role:       str        # minister casting the vote
    voted_option:     str        # exact option name from policy_options list
    confidence_score: float      # 0–100 (see scoring formula below)
    justification:    str        # 2–3 sentence reasoning
    second_choice:    str        # fallback option if first is vetoed
    veto_options:     List[str]  # "option_name: reason for blocking"
    _timestamp:       str
```

### 3.2 Voting Process (LangGraph fan-out)

```
rebuttal_round completes
        │
        ▼ route_to_voting()
        │
        ├── Send("minister_vote", {..., role: "economic_minister"})
        ├── Send("minister_vote", {..., role: "technology_minister"})
        ├── Send("minister_vote", {..., role: "infrastructure_minister"})
        ├── Send("minister_vote", {..., role: "citizen_minister"})
        ├── Send("minister_vote", {..., role: "environment_minister"})
        └── Send("minister_vote", {..., role: "opposition_minister"})

        All 6 fire in parallel via asyncio
        Each carries: problem, policy_options[], all_analyses[], all_debates[]

        GovernanceState.votes: Annotated[List, operator.add]
        → appends each VoteRecord as it completes

        ▼ tally_votes()
```

### 3.3 Vote Tally Algorithm

```python
def tally_votes(votes: List[VoteRecord], options: List[str]) -> VoteTally:

    # 1. Raw vote count
    raw_tally = Counter(v["voted_option"] for v in votes)

    # 2. Weighted tally (confidence-adjusted)
    weighted_tally: Dict[str, float] = defaultdict(float)
    for v in votes:
        weighted_tally[v["voted_option"]] += v["confidence_score"] / 100.0

    # 3. Veto processing
    veto_counts: Dict[str, int] = defaultdict(int)
    for v in votes:
        for veto in v.get("veto_options", []):
            option_name = veto.split(":")[0].strip()
            veto_counts[option_name] += 1

    # 4. Effective score (raw + weighted - veto penalty)
    effective_scores: Dict[str, float] = {}
    for option in options:
        raw   = raw_tally.get(option, 0)
        wt    = weighted_tally.get(option, 0.0)
        vetos = veto_counts.get(option, 0)
        effective_scores[option] = (raw * 0.5) + (wt * 0.5) - (vetos * 0.25)

    # 5. Winner
    winner = max(effective_scores, key=effective_scores.get)
    winning_raw = raw_tally.get(winner, 0)
    total = len(votes)
    vote_pct = round((winning_raw / total * 100) if total else 0, 1)

    # 6. Consensus level
    if vote_pct >= 80:   consensus = "high"
    elif vote_pct >= 50: consensus = "moderate"
    else:                consensus = "low"

    return {
        "winner":           winner,
        "raw_tally":        dict(raw_tally),
        "weighted_tally":   dict(weighted_tally),
        "veto_counts":      dict(veto_counts),
        "effective_scores": effective_scores,
        "vote_percentage":  vote_pct,
        "total_votes":      total,
        "winning_votes":    winning_raw,
        "consensus_level":  consensus,
    }
```

### 3.4 Vote Result Schema (Frontend)

```typescript
interface VoteTally {
  winner:          string
  vote_percentage: number        // % of raw votes for winner (0–100)
  consensus_level: "low" | "moderate" | "high"
  total_votes:     number        // always 6
  winning_votes:   number

  // Per-option breakdown
  options: {
    [option: string]: {
      raw_votes:       number    // vote count
      weighted_score:  number    // confidence-adjusted score
      veto_count:      number    // number of ministers blocking
      effective_score: number    // final ranked score
    }
  }

  // Per-minister breakdown
  minister_votes: {
    [role: MinisterRole]: {
      voted_option:    string
      confidence_score: number
      justification:   string
      second_choice:   string
      veto_options:    string[]
    }
  }
}
```

### 3.5 Veto Rule

A veto does not eliminate an option — it penalises its effective score. This preserves democratic legitimacy while flagging dangerous options. A winning option with 2+ vetoes triggers a mandatory risk flag in the Prime Minister synthesis prompt.

```
effective_score = (raw_votes × 0.5) + (confidence_weighted_votes × 0.5) - (veto_count × 0.25)

Example:
  Option A: 4 raw votes, confidence avg 78%, 0 vetoes
    → (4 × 0.5) + (3.12 × 0.5) - 0 = 3.56

  Option B: 2 raw votes, confidence avg 91%, 0 vetoes
    → (2 × 0.5) + (1.82 × 0.5) - 0 = 1.91

  Option C: 0 raw votes, confidence 0%, 4 vetoes
    → (0 × 0.5) + (0 × 0.5) - (4 × 0.25) = -1.00
```

---

## 4. Confidence Scoring

### 4.1 Per-Minister Confidence Score (in VoteRecord)

The confidence score represents how certain a minister is about their voted option, given the full debate context. It is not a score of option quality — it is a score of the minister's conviction.

```
confidence_score: float   // 0–100
```

**What raises confidence:**
- The voted option directly aligns with the minister's stated `primary_goal`
- The option received support from coalition ministers in debate
- The option's simulation score is strong in the minister's domain
- The Opposition's attack on this option was rebuttable

**What lowers confidence:**
- The voted option was attacked by the Opposition without a clean rebuttal
- The option forces the minister to concede red lines
- High veto counts from other ministers on this option
- Simulation scores are weak in the minister's domain

### 4.2 Confidence Score Bands

| Range | Label | Meaning | Visual Treatment |
|---|---|---|---|
| 90–100 | **Certain** | Minister is fully aligned | Solid filled badge, bright color |
| 75–89 | **Confident** | Strong conviction, minor reservations | Filled badge, standard color |
| 55–74 | **Leaning** | Votes for option but with noted concerns | Half-filled badge, muted color |
| 35–54 | **Uncertain** | Forced choice, significant reservations | Outlined badge, warning color |
| 0–34 | **Reluctant** | Voting against preference, fallback only | Dashed outline badge, dim color |

### 4.3 Cabinet Confidence Score (Aggregate)

```
cabinet_confidence = weighted_average(
  [v.confidence_score for v in votes if v.voted_option == winner],
  weights=[1.0, 1.0, 1.0, 1.0, 1.0, 0.8]  # Opposition weighted slightly lower
)
```

### 4.4 Consensus Confidence Matrix (UI Visual)

```
High consensus + High avg confidence     → "Strong Mandate"       (green)
High consensus + Low avg confidence      → "Reluctant Majority"   (yellow)
Moderate consensus + High avg confidence → "Divided Expert View"  (blue)
Moderate consensus + Low avg confidence  → "Uncertain Coalition"  (orange)
Low consensus + Any confidence           → "Fractured Cabinet"    (red)
```

### 4.5 Prime Minister Confidence Score (in FinalPolicy)

The PM's `confidence_score` is computed differently — it reflects the quality of the decision-making process, not just the vote result.

```
pm_confidence = base_score × modifiers

base_score = vote_percentage   // 83.3% winner vote share → base 83.3

modifiers:
  × 1.1   if consensus_level == "high"
  × 1.0   if consensus_level == "moderate"
  × 0.85  if consensus_level == "low"

  × 1.05  if best_simulation_composite_score >= 75
  × 0.95  if best_simulation_composite_score < 50

  × 1.05  if opposition_attack was acknowledged and rebutted in final report
  × 0.90  if opposition attack was not addressed

  → clamp to [0, 100]

Example:
  vote_percentage: 83.3
  consensus: high       → × 1.1 = 91.6
  simulation: 78        → × 1.05 = 96.2
  opposition: addressed → × 1.05 = 100 (clamped)
  pm_confidence: 100
```

---

## 5. Visual Presentation Design

### 5.1 Debate Feed Layout

```
┌─────────────────────────────────────────────────────────────┐
│  📋 DEBATE FEED                               Phase: DEBATE │
│─────────────────────────────────────────────────────────────│
│                                                             │
│  ── PROPOSAL PHASE ──────────────────── 6 ministers ──────  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [📈 TrendingUp]  Economic Minister           PROPOSAL │   │
│  │  gradient: from-emerald-500 to-green-600              │   │
│  │                                                       │   │
│  │  "The 35% unemployment crisis requires..."            │   │
│  │                                                       │   │
│  │  Key Findings                                         │   │
│  │  ● GDP contraction of 2.3% projected                 │   │
│  │  ● 47M workers at immediate risk                     │   │
│  │  ● Fiscal deficit at 5.8% — above red line           │   │
│  │                                                       │   │
│  │  Proposed Solutions                                   │   │
│  │  → Market-Driven Reskilling Programme ($12B)         │   │
│  │  → Universal Basic Income Pilot (10 cities)          │   │
│  │                                                        │   │
│  │  Priority: ████████░░ 82   Confidence: █████████░ 91 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  [similar cards for Technology, Infrastructure, Citizen,    │
│   Environment, Opposition]                                  │
│                                                             │
│  ── DEBATE ROUND ────────────────────── sequential ───────  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [📈]  Economic Minister          ROUND 1 · DEBATE    │   │
│  │       targets: [environment_minister, citizen_minister]│   │
│  │                                                       │   │
│  │  "While I support the Citizen Minister's equity goals,│   │
│  │   the fiscal reality is that..."                      │   │
│  │                                                       │   │
│  │  Concedes: "Equity concerns are valid..."             │   │
│  │  Evidence: "OECD 2024 data shows..."                 │   │
│  │                                 intensity: ●●○       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ── OPPOSITION ATTACK ────────────────── dedicated ───────  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [🛡️ ShieldAlert]  Opposition           ⚡ ATTACK    │   │
│  │  background: from-red-950/40   border: red-500/60     │   │
│  │                                                       │   │
│  │  "The Economic Minister's reskilling proposal..."     │   │
│  │  "The Technology Minister assumes..."                 │   │
│  │                                                       │   │
│  │  Targeting: 📈 Economic Minister, 💻 Technology       │   │
│  │                                 intensity: ●●●       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ── REBUTTAL PHASE ───────────────────── parallel ────────  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ [📈]  Economic Minister      ROUND 2 · REBUTTAL      │   │
│  │                                                       │   │
│  │  "The Opposition correctly identifies..."             │   │
│  │                                                       │   │
│  │  Concedes: "The implementation risk is real..."       │   │
│  │  New evidence: "South Korea's 2023 programme..."     │   │
│  │                                 intensity: ●○○       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Message Card Visual Spec

Each `DebateMessage` renders as a card. Visual treatment varies by `type` and `phase`:

```typescript
// Card visual config by message type
const MESSAGE_STYLES: Record<MessageType, MessageStyle> = {
  analysis: {
    badge:     "ANALYSIS",
    badgeColor: "bg-slate-700 text-slate-300",
    border:    "border-l-4",         // left accent stripe in author color
    background:"bg-slate-900/60",
    showKeyPoints:    true,
    showSolutions:    true,
    showPriority:     true,
    showConfidence:   true,
    showIntensity:    false,
  },
  proposal: {
    badge:     "PROPOSAL",
    badgeColor: "bg-blue-900/60 text-blue-300",
    border:    "border-l-4",
    background:"bg-slate-900/80",
    showTargets:      true,
    showConcessions:  true,
    showEvidence:     true,
    showIntensity:    true,
  },
  attack: {
    badge:     "⚡ ATTACK",
    badgeColor: "bg-red-900/80 text-red-300",
    border:    "border-2 border-red-500/60",
    background:"bg-red-950/40",
    glow:      "shadow-[0_0_20px_rgba(239,68,68,0.15)]",
    showTargets:      true,          // targeted ministers highlighted
    showIntensity:    true,          // always max intensity for attacks
    pulse:     true,                 // animated pulse border on arrival
  },
  rebuttal: {
    badge:     "REBUTTAL",
    badgeColor: "bg-amber-900/60 text-amber-300",
    border:    "border-l-4 border-amber-500/60",
    background:"bg-slate-900/80",
    indent:    true,                 // visually nested under attack card
    showConcessions:  true,
    showEvidence:     true,
    showIntensity:    true,
  },
  vote: {
    badge:     "VOTE CAST",
    badgeColor: "bg-violet-900/60 text-violet-300",
    background:"bg-slate-900/90",
    showConfidence:   true,          // large confidence bar
    showVeto:         true,
    showSecondChoice: true,
  },
  verdict: {
    badge:     "👑 FINAL DECISION",
    badgeColor: "bg-amber-600 text-white",
    border:    "border-2 border-amber-500",
    background:"bg-amber-950/40",
    glow:      "shadow-[0_0_40px_rgba(245,158,11,0.20)]",
    fullWidth: true,                 // spans full container width
    animate:   "reveal",            // animated reveal on entry
  },
  system: {
    centered:  true,                 // phase separator — full-width centered
    line:      true,                 // horizontal rule with label
    noCard:    true,
  },
}
```

### 5.3 Intensity Indicator

```
intensity: 1 (mild)          → ●○○  (1 dot filled)
intensity: 2 (moderate)      → ●●○  (2 dots filled)
intensity: 3 (confrontational)→ ●●●  (3 dots filled, red tint)

// Computed from:
// attack → always 3
// rebuttal after attack → 1–2
// debate with many concessions → 1
// debate challenging specific minister → 2–3
```

### 5.4 Live Animation Sequence

```
On SSE event received:

  1. System message slides in from top (phase announcement)     → 300ms slide-down
  2. New minister card fades in at bottom of feed              → 400ms fade + slide-up
  3. Minister avatar pulses once                               → 600ms pulse
  4. Text content streams in character by character            → typewriter (if chunked)
     OR fades in as complete block                             → 200ms fade (if full)
  5. Key points / solutions reveal with staggered delay        → 100ms each, staggered
  6. Intensity dots fill one by one                            → 150ms stagger
  7. Confidence bar fills from 0 to value                      → 600ms ease-out

On opposition_attack:
  1. Red glow pulses on card container                         → 800ms pulse
  2. Targeted minister avatars flash red                       → 400ms flash × 2
  3. Card border animates (dashed → solid)                     → 300ms

On vote_cast:
  1. Vote panel bar extends to new value                       → 500ms ease-out
  2. Confidence arc fills                                      → 600ms ease-out
  3. "Vote cast" toast fires with minister color               → Sonner toast

On session_complete:
  1. Confetti burst (subtle, 1 second)
  2. Final report card slides in with gold glow
  3. All phase timeline segments fill green
```

### 5.5 Vote Panel Visual Spec

```
┌─────────────────────────────────────────────────────────────┐
│  🗳️  DEMOCRATIC VOTE                                         │
│                                                             │
│  RESULT          Technology-Led Transformation              │
│  VOTES           5 / 6   (83.3%)                           │
│  CONSENSUS       HIGH ████████████████████████  83%        │
│─────────────────────────────────────────────────────────────│
│  Option A — Market-Driven Reskilling                       │
│  │███░░░░░░░░░░░░░░░░│  1 vote    veto: 2                  │
│                                                             │
│  Option B — Technology-Led Transformation  ← WINNER        │
│  │██████████████████│  5 votes   veto: 0                   │
│                                                             │
│  Option C — Community-Centered Development                 │
│  │░░░░░░░░░░░░░░░░░░│  0 votes   veto: 3                   │
│─────────────────────────────────────────────────────────────│
│  PER-MINISTER VOTES                                         │
│                                                             │
│  📈 Economic       Option B   ████████████░░  78%          │
│  💻 Technology     Option B   ███████████████ 95%          │
│  🏗️ Infrastructure Option B   █████████░░░░░  64%          │
│  👥 Citizen        Option B   ████████████░░  82%          │
│  🌿 Environment    Option B   ███████████░░░  74%          │
│  🛡️ Opposition     Option A   ██████░░░░░░░░  48%  ← low   │
│                                                             │
│  CABINET CONFIDENCE            84.7 / 100                  │
│  Mandate: STRONG MANDATE                                    │
└─────────────────────────────────────────────────────────────┘
```

### 5.6 Phase Timeline Bar

```
┌──────────────────────────────────────────────────────────────┐
│  TITAN GOVERNANCE PIPELINE                                   │
│                                                              │
│  ● Analysis  ● Debate  ● Challenge  ● Rebuttal  ● Vote      │
│  ─────────   ───────   ─────────   ────────    ────         │
│  ✓ done      ✓ done    ✓ done     ✓ done      ⟳ active     │
│                                                              │
│  ○ Simulation   ○ Decision                                   │
│  ──────────     ────────                                     │
│  · pending      · pending                                    │
└──────────────────────────────────────────────────────────────┘

Visual states per segment:
  ✓ done      → filled green segment, check icon
  ⟳ active   → pulsing amber segment, spinner icon
  · pending   → outlined grey segment, clock icon
  ✗ failed   → filled red segment, x icon
```

---

## 6. GovernanceState — Complete Debate Fields

```python
class GovernanceState(TypedDict):
    # Identity
    project_id:  str
    problem:     str
    context:     str

    # Phase 1 — Parallel analyses
    # Annotated[List, operator.add] = parallel fan-out safe
    analyses: Annotated[List[MinisterOutput], operator.add]

    # Phase 2 — Debate round (5 ministers sequential)
    debate_arguments: Annotated[List[DebateArgument], operator.add]

    # Phase 3 — Opposition dedicated attack
    opposition_attacks: Annotated[List[DebateArgument], operator.add]

    # Phase 4 — Rebuttals (5 ministers parallel)
    rebuttals: Annotated[List[DebateArgument], operator.add]

    # Derived from aggregate_analyses
    policy_options: List[str]        # option names extracted from proposed_solutions

    # Phase 5 — Votes (6 ministers parallel)
    votes: Annotated[List[VoteRecord], operator.add]
    vote_tally: Dict[str, int]       # option → raw vote count

    # Phase 6 — Simulation
    simulation_results: Annotated[List[Dict], operator.add]

    # Phase 7 — PM Synthesis
    final_report: Optional[Dict[str, Any]]

    # Phase 8 — Black Swan
    black_swan_results: Optional[Dict[str, Any]]

    # Control
    current_phase: str               # maps to DebateStatus enum
    error:         Optional[str]
    metadata:      Dict[str, Any]    # timing, vote metadata, completion data
```

---

## 7. Debate Message Feed — Frontend State

```typescript
// session-store.ts (Zustand)
interface SessionStore {
  // Identity
  sessionId:       string | null
  status:          DebateStatus

  // Phase 1 — Analysis outputs (map for O(1) access by role)
  analyses:        Record<MinisterRole, MinisterOutput>
  analysesOrdered: MinisterRole[]    // insertion order for rendering

  // Phases 2–4 — Unified debate feed (all phases merged, ordered by sequence)
  debateMessages:  DebateMessage[]   // appended by SSE dispatcher

  // Phase 5 — Vote state
  votes:           Record<MinisterRole, VoteRecord>
  voteTally:       VoteTally | null

  // Phase 6 — Simulation
  simulationResults: SimulationResult[]

  // Phase 7 — Final report
  finalPolicy:     FinalPolicy | null
  blackSwan:       BlackSwanResult | null

  // UI helpers
  activePhase:     DebateStatus
  lastEventAt:     string | null
  error:           string | null

  // Dispatcher — single handler for all SSE events
  handleSSEEvent:  (event: SSEEvent) => void
  reset:           () => void
}

// Dispatcher logic
function handleSSEEvent(event: SSEEvent): void {
  switch (event.event) {

    case "analysis_complete":
      store.analyses[event.data.minister_role]   = toMinisterOutput(event.data)
      store.analysesOrdered.push(event.data.minister_role)
      store.debateMessages.push(toDebateMessage(event, "analysis"))
      break

    case "debate_argument":
      const msgType = event.data.phase === "opposition_attack" ? "attack"
                    : event.data.phase === "rebuttal"          ? "rebuttal"
                    :                                            "proposal"
      store.debateMessages.push(toDebateMessage(event, msgType))
      break

    case "vote_cast":
      store.votes[event.data.agent_role] = event.data
      store.debateMessages.push(toDebateMessage(event, "vote"))
      break

    case "voting_complete":
      store.voteTally = event.data
      break

    case "simulation_result":
      store.simulationResults.push(event.data)
      break

    case "synthesis_complete":
      store.finalPolicy = event.data.policy
      store.debateMessages.push(toDebateMessage(event, "verdict"))
      break

    case "session_complete":
      store.blackSwan    = event.data.black_swan
      store.status       = "completed"
      break

    case "error":
      store.error        = event.data.message
      store.status       = "failed"
      break
  }
  store.lastEventAt = event.timestamp
}
```

---

## 8. Debate Quality Signals

These signals are computed on the frontend from the accumulated debate state and surfaced as UI indicators:

```typescript
interface DebateQualityMetrics {
  // How much ministers changed their minds
  concession_rate: number         // avg concessions per minister / total positions
  // 0% = rigid debate, 100% = everyone agreed immediately

  // Opposition effectiveness
  opposition_hit_rate: number     // proposals the Opposition targeted that lost votes
  // high = Opposition influenced the outcome

  // Coalition detection
  detected_coalitions: Array<{
    ministers: MinisterRole[]
    shared_option: string
    avg_confidence: number
  }>

  // Debate richness
  total_word_count:   number      // all debate arguments combined
  unique_evidence:    number      // distinct evidence items introduced
  cross_references:   number      // times a minister references another by role

  // Consensus path
  consensus_trajectory: "converging" | "diverging" | "stable"
  // based on whether minister positions shifted toward same option across rounds
}
```

---

*TITAN Debate Engine — structured disagreement, resolved democratically.*
