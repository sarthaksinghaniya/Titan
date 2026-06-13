# TITAN — UI/UX Design System

> **Futuristic. Premium. Hackathon-winning.**
> Dark-first, motion-rich, data-dense without being overwhelming.
> Every screen tells a story — from problem to decision.

---

## Design Philosophy

```
TITAN is not a dashboard. TITAN is a theatre.
Every phase is a scene. Every agent is a character.
Every number is a verdict.

Three principles govern every design decision:

  1. INFORMATION HIERARCHY
     The user must always know: what phase are we in? what just happened?
     Never make them hunt for status.

  2. MOTION AS MEANING
     Animations signal causality, not decoration.
     A card sliding in = an agent just responded.
     A bar filling = a vote being counted.

  3. PREMIUM RESTRAINT
     Dark backgrounds. Strategic colour. Controlled glow.
     One gold accent. One blue accent. Colour reserved for signal, not noise.
```

---

## 1. Design Token System

### 1.1 Color Palette

```css
/* ─── Core Background Stack ─────────────────────────── */
--bg-void:       #050508;   /* Page background — near-black with blue tint */
--bg-surface:    #0d0d14;   /* Card base — 1 step lighter */
--bg-surface-2:  #13131f;   /* Card inner panels */
--bg-surface-3:  #1a1a2e;   /* Hover states, active rows */

/* ─── Brand Accents ──────────────────────────────────── */
--gold:          #f59e0b;   /* Prime Minister / Final Decision / CTA */
--gold-light:    #fbbf24;   /* Headings, hover text */
--gold-glow:     rgba(245, 158, 11, 0.20);
--blue:          #6366f1;   /* System accent / analysis phase */
--blue-light:    #818cf8;   /* Links, highlights */
--blue-glow:     rgba(99, 102, 241, 0.15);

/* ─── Border System ──────────────────────────────────── */
--border:        rgba(255, 255, 255, 0.06);  /* Default — barely visible */
--border-accent: rgba(255, 255, 255, 0.12); /* Hover / focus */
--border-gold:   rgba(245, 158, 11, 0.30);  /* PM / decision elements */
--border-blue:   rgba(99, 102, 241, 0.30);  /* Analysis / system elements */

/* ─── Text System ────────────────────────────────────── */
--text-primary:   rgba(255, 255, 255, 0.95); /* Headings, key data */
--text-secondary: rgba(255, 255, 255, 0.60); /* Body copy, labels */
--text-muted:     rgba(255, 255, 255, 0.35); /* Placeholders, disabled */
--text-micro:     rgba(255, 255, 255, 0.20); /* Timestamps, metadata */

/* ─── Minister Color System ──────────────────────────── */
--minister-pm:       #f59e0b;  /* Prime Minister — gold */
--minister-economic: #10b981;  /* Economic — emerald */
--minister-tech:     #6366f1;  /* Technology — indigo */
--minister-infra:    #f97316;  /* Infrastructure — orange */
--minister-citizen:  #ec4899;  /* Citizen — pink */
--minister-env:      #22c55e;  /* Environment — green */
--minister-opp:      #ef4444;  /* Opposition — red */
--minister-sim:      #0ea5e9;  /* Simulation — cyan */

/* ─── Status Progression (matches pipeline phases) ───── */
--status-pending:     #6b7280;  /* grey */
--status-analyzing:   #6366f1;  /* indigo */
--status-debating:    #f59e0b;  /* amber */
--status-challenging: #ef4444;  /* red */
--status-rebutting:   #f97316;  /* orange */
--status-voting:      #ec4899;  /* pink */
--status-simulating:  #0ea5e9;  /* cyan */
--status-synthesizing:#f59e0b;  /* gold */
--status-completed:   #10b981;  /* emerald */
--status-failed:      #ef4444;  /* red */

/* ─── Simulation Future Colors ───────────────────────── */
--future-a: #10b981;  /* Optimistic — emerald */
--future-b: #f43f5e;  /* Pessimistic — rose */
--future-c: #6366f1;  /* Tech-driven — indigo */
--future-d: #f59e0b;  /* Constrained — amber */

/* ─── Black Swan Colors ──────────────────────────────── */
--bs-fortress:     #10b981;
--bs-resilient:    #22c55e;
--bs-stable:       #6366f1;
--bs-fragile:      #eab308;
--bs-vulnerable:   #f97316;
--bs-catastrophic: #ef4444;
```

### 1.2 Typography Scale

```css
/* Font families */
--font-display: "Space Grotesk", system-ui, sans-serif;   /* Hero headings */
--font-sans:    "Inter", system-ui, sans-serif;            /* Body everywhere */
--font-mono:    "JetBrains Mono", monospace;               /* Scores, data */

/* Scale */
--text-hero:   clamp(52px, 7vw, 84px);   /* Landing headline */
--text-h1:     clamp(32px, 4vw, 48px);   /* Page titles */
--text-h2:     clamp(22px, 2.5vw, 30px); /* Section headers */
--text-h3:     18px;                      /* Card titles */
--text-body:   14px;                      /* Default body */
--text-sm:     12px;                      /* Labels, badges */
--text-xs:     10px;                      /* Micro labels, timestamps */
--text-score:  clamp(48px, 6vw, 72px);   /* Large score display */
```

### 1.3 Spacing & Radius

```css
/* Radius */
--radius-sm:  6px;    /* Badges, chips */
--radius-md:  10px;   /* Inputs, small cards */
--radius-lg:  16px;   /* Main cards */
--radius-xl:  24px;   /* Modals, large panels */
--radius-2xl: 32px;   /* Hero elements */

/* Spacing grid: 4px base */
--space-1:  4px;   --space-2:  8px;   --space-3:  12px;
--space-4:  16px;  --space-5:  20px;  --space-6:  24px;
--space-8:  32px;  --space-10: 40px;  --space-12: 48px;
--space-16: 64px;
```

### 1.4 Animation System

```css
/* Durations */
--dur-instant: 100ms;
--dur-fast:    200ms;
--dur-normal:  350ms;
--dur-slow:    500ms;
--dur-reveal:  700ms;

/* Easings */
--ease-out:     cubic-bezier(0, 0, 0.2, 1);
--ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);   /* Bouncy reveals */
--ease-smooth:  cubic-bezier(0.25, 0.46, 0.45, 0.94);

/* Named animations */
@keyframes slide-up     { from: opacity:0 + translateY(20px);  to: opacity:1 + translateY(0) }
@keyframes slide-right  { from: opacity:0 + translateX(-20px); to: opacity:1 + translateX(0) }
@keyframes scale-in     { from: opacity:0 + scale(0.92);       to: opacity:1 + scale(1) }
@keyframes count-up     { /* JS-driven counter animation */ }
@keyframes bar-fill     { from: width:0%; }
@keyframes glow-pulse   { 0%,100%: opacity:1; 50%: opacity:0.5 }
@keyframes typewriter   { /* character-by-character text reveal */ }
@keyframes radar-draw   { /* SVG stroke-dashoffset reveal */ }
@keyframes stamp-in     { from: opacity:0 + scale(1.5) + rotate(-3deg); to: opacity:1 + scale(1) + rotate(0) }
```

### 1.5 Component Library (shadcn/ui base)

```
Button       → variant: default, outline, ghost, gold, destructive
Badge        → variant: default, minister (colored), status, band
Card         → titan-card class: dark surface + subtle border + hover glow
Input        → dark bg, blue focus ring
Textarea     → dark bg, blue focus ring, resize-none
Progress     → dark track, gradient fill
Tabs         → underline style (not boxed)
Tooltip      → dark, instant on hover
Dialog       → glass panel, backdrop blur
Separator    → rgba(255,255,255,0.06)
ScrollArea   → 4px custom scrollbar
Sonner toast → dark, bottom-right, minister-colored variants
```

---

## 2. Layout System

### 2.1 Navigation Shell

```
┌─────────────────────────────────────────────────────────────────┐
│  NAVBAR (fixed, h-14, glass background, border-bottom)          │
│                                                                  │
│  [⬡ TITAN]                              [●] Live   [?] Help    │
│   wordmark                              session indicator        │
└─────────────────────────────────────────────────────────────────┘

┌───────┬─────────────────────────────────────────────────────────┐
│       │                                                          │
│  NAV  │  PAGE CONTENT                                           │
│       │                                                          │
│  w-56 │  max-w-screen-xl  mx-auto  px-6                        │
│ fixed │                                                          │
│       │                                                          │
└───────┴─────────────────────────────────────────────────────────┘

Sidebar nav items (icon + label):
  ⬡  TITAN           (logo / home link)
  ─────────────────
  ◎  New Session     → /
  ◉  Parliament      → /parliament   (disabled until session active)
  ◈  Simulation      → /simulation   (disabled until voting complete)
  ◇  Final Report    → /report       (disabled until synthesizing complete)
  ─────────────────
  📂 Session History → /sessions
  ─────────────────
  ⚙  Status         → shows API health badge

Active state: gold left border accent, slight background highlight
Disabled state: muted opacity, cursor-not-allowed
```

### 2.2 Responsive Grid

```
Desktop (≥1280px):   12-column grid, 24px gap
Tablet (768–1280px): 8-column grid, 16px gap
Mobile (<768px):     4-column grid, 12px gap — some panels collapse to accordion

Content regions:
  Full-width panels:   col-span-12
  Two-column:          col-span-8 + col-span-4 (main + sidebar)
  Three-column:        col-span-4 × 3 (minister grid, simulation futures)
  Parliament feed:     col-span-7 + col-span-5 (debate + vote panel)
```

---

## 3. Page 1 — Landing Page

### 3.1 Purpose
Transform the landing into TITAN's front door — instantly communicate the power of the system, build trust through visual complexity, and funnel the user toward submitting a problem with confidence.

### 3.2 Above the Fold

```
┌─────────────────────────────────────────────────────────────────┐
│  [NAVBAR]                                                        │
│                                                                  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  ← orb-1 (indigo, top-left)│
│                                                                  │
│         [⬡ Multi-Agent Governance Engine]  ← pill badge         │
│                                                                  │
│    Simulate Policy Impact                                        │
│    Before It Happens.         ← gradient text (gold → blue)     │
│                               ← font: Space Grotesk, 72px black │
│                                                                  │
│    Input a complex societal challenge. TITAN's autonomous        │
│    AI cabinet analyses, debates, votes, and simulates            │
│    outcomes — delivering a government-grade policy.              │
│                               ← Inter 16px, text-secondary       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PROBLEM SUBMISSION CARD  (glass card, blue glow)       │    │
│  │                                                         │    │
│  │  [Cpu icon] Core Problem Statement                      │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  Textarea — h-28, dark bg, placeholder text     │   │    │
│  │  │  "e.g., India needs to transition its energy    │   │    │
│  │  │   grid to 100% renewables by 2035..."           │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  Context & Constraints  (optional)                      │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  Single-line input                              │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  Character count ── 0/500         [Engage Ministers →] │    │
│  │                              ← gold CTA button          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ░░░░░░░░░░░░  ← orb-2 (gold, bottom-right)                    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 Below the Fold — Process Strip

```
┌─────────────────────────────────────────────────────────────────┐
│  HOW TITAN WORKS                                                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  [1]──────────[2]──────────[3]──────────[4]──────────[5]        │
│  Problem  →  Analysis  →  Parliament →  Simulation →  Decision  │
│                                                                  │
│  Each step: icon + 2-word label + 1-sentence description        │
│  Connected by arrow lines with gradient fill                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.4 Below the Fold — Cabinet Preview

```
┌─────────────────────────────────────────────────────────────────┐
│  YOUR CABINET AWAITS                                             │
│  7 AI ministers, each with a distinct mandate                    │
│                                                                  │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                        │
│  │  📈  │  │  💻  │  │  🏗️  │  │  👥  │                        │
│  │Econ  │  │Tech  │  │Infra │  │Citiz │                        │
│  └──────┘  └──────┘  └──────┘  └──────┘                        │
│       ┌──────┐  ┌──────┐  ┌──────┐                             │
│       │  🌿  │  │  🛡️  │  │  👑  │  ← PM appears last         │
│       │Envir │  │Oppos │  │ PM   │      (gold card, larger)     │
│       └──────┘  └──────┘  └──────┘                             │
│                                                                  │
│  Each card: minister color gradient border, icon, title,        │
│  1-line description, 3 focus area tags                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.5 Below the Fold — Stats Bar

```
┌─────────────────────────────────────────────────────────────────┐
│  ┌──────────────┬──────────────┬──────────────┬────────────────┐│
│  │     7        │     4        │     6        │    ~4 min      ││
│  │  Ministers   │  Futures     │  Debate      │  Per Session   ││
│  │  Debating    │  Simulated   │  Phases      │                ││
│  └──────────────┴──────────────┴──────────────┴────────────────┘│
│  Numbers count up on scroll-into-view                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3.6 Submit CTA State Machine

```
IDLE:         "Engage Ministers →"  (gold button, arrow icon)
LOADING:      "Initializing Cabinet..."  (spinner, disabled, pulsing)
ERROR:        red banner above form, button re-enables
SUCCESS:      "Cabinet Assembled" (green check) → auto-redirect /parliament
```

---

## 4. Page 2 — Problem Workspace (Currently: /)

> **Note:** This is the same as the Landing Page. As TITAN grows, this becomes a dedicated `/workspace` page with richer problem tooling — tags, examples, template problems, and previous session links.

### 4.1 Enhanced Problem Card

```
┌─────────────────────────────────────────────────────────────────┐
│  PROBLEM WORKSPACE                        Session: New          │
│─────────────────────────────────────────────────────────────────│
│                                                                  │
│  Problem Statement *                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Textarea — 6 rows — blue focus ring                    │   │
│  │  Real-time: character count / 1000                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Context & Constraints (optional)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Input — placeholder: budget, timeframe, region         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ── Example Problems ────────────────────────────────────────   │
│  [▶ Urban Unemployment] [▶ Climate Transition] [▶ Healthcare]   │
│    ← click to auto-fill textarea                                │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  WHAT HAPPENS NEXT                                               │
│  ① Cabinet analyses in parallel     ~60 seconds                │
│  ② Ministers debate and challenge   ~90 seconds                │
│  ③ Democratic vote tallied          ~30 seconds                │
│  ④ Four futures simulated           ~45 seconds                │
│  ⑤ Prime Minister issues decision  ~30 seconds                 │
│  ─────────────────────────────────────────────────────────────  │
│                                                       [→ Engage] │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Page 3 — AI Parliament

### 5.1 Purpose
The most complex and visually impressive page. The user watches the AI cabinet think, argue, vote, and decide — in real time. This is TITAN's primary WOW moment.

### 5.2 Full Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  NAVBAR  ·  TITAN Parliament  ·  [status badge]  [copy project id]  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PHASE TIMELINE (sticky, below navbar)                              │
│  ①Analysis ──► ②Debate ──► ③Challenge ──► ④Rebuttal ──► ⑤Vote     │
│  [done]        [active]     [pending]     [pending]     [pending]   │
│                                                                      │
├──────────────────────────────┬──────────────────────────────────────┤
│                              │                                       │
│   DEBATE FEED                │   SIDE PANEL                         │
│   col-span-7                 │   col-span-5                         │
│                              │                                       │
│   [Phase system messages]    │   ┌─────────────────────────────┐   │
│   [Minister cards stream in] │   │  CABINET STATUS             │   │
│                              │   │  6 minister avatars         │   │
│   [see section 5.3]          │   │  each with: status dot +    │   │
│                              │   │  current action label       │   │
│                              │   └─────────────────────────────┘   │
│                              │                                       │
│                              │   ┌─────────────────────────────┐   │
│                              │   │  VOTE PANEL                 │   │
│                              │   │  (appears after voting      │   │
│                              │   │   phase begins)             │   │
│                              │   └─────────────────────────────┘   │
│                              │                                       │
│                              │   ┌─────────────────────────────┐   │
│                              │   │  LIVE METRICS               │   │
│                              │   │  Total words: 1,247         │   │
│                              │   │  Arguments: 11/12           │   │
│                              │   │  Concessions: 8             │   │
│                              │   │  Vetoes filed: 2            │   │
│                              │   └─────────────────────────────┘   │
│                              │                                       │
└──────────────────────────────┴──────────────────────────────────────┘
```

### 5.3 Phase Timeline (Sticky)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ●─────────────●────────────○────────────○────────────○         │
│  Analysis     Debate     Challenge    Rebuttal      Vote         │
│  ✓ done       ⟳ active   · pending   · pending    · pending    │
│  72s          —           —           —             —            │
│                                                                  │
│  Segment colors: done=emerald, active=amber pulsing, pending=grey│
│  Connecting line fills green as phases complete                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Debate Feed Cards

**A — Analysis Card (Phase 1)**

```
┌──────────────────────────────────────────────────────────┐
│  ████  Economic Minister              ANALYSIS  ·  72ms  │
│  ████  ← 4px color stripe (emerald) + icon               │
│  ████                                                     │
│─────────────────────────────────────────────────────────│
│  "India's 35% urban unemployment represents a structural  │
│   failure of the labour market to absorb AI displacement..."│
│                                                           │
│  KEY FINDINGS                                             │
│  ●  GDP contraction of 2.3% projected Q1                 │
│  ●  47M workers at immediate risk                        │
│  ●  Fiscal deficit at 5.8% — above red line             │
│                                                           │
│  PROPOSED SOLUTIONS                                       │
│  →  Market-Driven Reskilling ($12B, 18 months)          │
│  →  Universal Basic Income Pilot (10 cities, 2 years)   │
│  →  Green Jobs Transition Fund ($8B, 36 months)         │
│                                                           │
│  Priority ████████░░ 82    Confidence █████████░ 91      │
│                                      ← mini bar charts    │
└──────────────────────────────────────────────────────────┘
```

**B — Debate Card (Phase 2)**

```
┌──────────────────────────────────────────────────────────┐
│  ████  Economic Minister         ROUND 1 · DEBATE  ●●○   │
│        targets: [Citizen Minister] [Environment Minister] │
│─────────────────────────────────────────────────────────│
│  "While I acknowledge the equity concerns raised by the   │
│   Citizen Minister, the fiscal arithmetic does not support │
│   a universal basic income at scale. OECD data from 2023  │
│   shows that direct skills investment yields 3× the GDP   │
│   return compared to transfer payments..."               │
│                                                           │
│  Concedes: "The green transition gap is real..."          │
│  Evidence: "OECD 2023, South Korea skills data"          │
└──────────────────────────────────────────────────────────┘
```

**C — Attack Card (Phase 3 — Opposition)**

```
┌──────────────────────────────────────────────────────────┐
│  ████  Opposition Minister    ⚡ OPPOSITION ATTACK  ●●●   │
│        border: 2px solid red-500/60                       │
│        background: red-950/40                             │
│        glow: 0 0 20px rgba(239,68,68,0.15)                │
│─────────────────────────────────────────────────────────│
│  "The Economic Minister's reskilling proposal contains a  │
│   fatal assumption: that displaced workers can be         │
│   reskilled within 18 months. Historical data from        │
│   Germany's Kurzarbeit programme shows 36–48 months       │
│   is the minimum realistic timeline. The entire Phase 1   │
│   budget is being built on a false premise..."           │
│                                                           │
│  Targeting:  📈 Economic Minister  ·  💻 Technology Minister│
│                                                           │
│  ← TARGETED MINISTERS: their avatars flash red ×2        │
└──────────────────────────────────────────────────────────┘
```

**D — Rebuttal Card (Phase 4)**

```
┌──────────────────────────────────────────────────────────┐
│  ████  Economic Minister       ROUND 2 · REBUTTAL  ●○○   │
│        indent: slightly right (nested under attack)       │
│        border-left: amber-500/40                          │
│─────────────────────────────────────────────────────────│
│  "The Opposition correctly identifies the 18-month        │
│   assumption as optimistic. We concede on this point.    │
│   However, South Korea's 2023 Digital Bridge programme   │
│   achieved 28-month median reskilling by co-locating     │
│   training within the existing workplace..."             │
│                                                           │
│  Concedes: "18-month timeline is optimistic"             │
│  Evidence: "South Korea Digital Bridge (2023)"           │
└──────────────────────────────────────────────────────────┘
```

**E — Phase Separator (System Message)**

```
  ─────────────────── ⚡ OPPOSITION TAKING THE FLOOR ─────────────── 
  ← centered, red icon, dimmed text, full-width hairline
```

**F — Vote Card**

```
┌──────────────────────────────────────────────────────────┐
│  ████  Economic Minister                    VOTE CAST    │
│─────────────────────────────────────────────────────────│
│  Voted for:  Technology-Led Transformation               │
│                                                           │
│  Confidence  ████████████░░  78%                         │
│  Justification: "Market mechanisms and tech leverage     │
│   offer the highest ROI within fiscal constraints..."    │
│                                                           │
│  Second choice: Green Jobs Transition Fund               │
│  Veto: Market-Driven Reskilling  (uncosted timeline)    │
└──────────────────────────────────────────────────────────┘
```

### 5.5 Vote Panel (Side Panel)

```
┌─────────────────────────────────────────────────────────┐
│  🗳  DEMOCRATIC VOTE                       5 / 6 cast   │
│─────────────────────────────────────────────────────────│
│  Option A — Market-Driven Reskilling                    │
│  ▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌  1 vote                 │
│                                                          │
│  Option B — Technology-Led Transformation  ← WINNING   │
│  ▐████████████████████████████▌  4 votes                │
│  ← gold fill, glow                                      │
│                                                          │
│  Option C — Community-Centered Development              │
│  ▐░░░░░░░░░░░░░░░░░░░░░░░░░░░░▌  0 votes   veto: 3     │
│                                                          │
│─────────────────────────────────────────────────────────│
│  Consensus: HIGH   ████████████████████  83%            │
│                                                          │
│  Per-minister breakdown (avatar + voted option):        │
│  📈 → Option B    💻 → Option B    🏗️ → Option B        │
│  👥 → Option B    🌿 → Option B    🛡️ → Option A        │
└─────────────────────────────────────────────────────────┘
```

### 5.6 Cabinet Status Panel (Side Panel)

```
┌─────────────────────────────────────────────────────────┐
│  CABINET STATUS                                          │
│─────────────────────────────────────────────────────────│
│  📈 Economic       ● Analysis complete                   │
│  💻 Technology     ● Debate round 1 complete             │
│  🏗️ Infrastructure ⟳ Debating now...                    │
│  👥 Citizen        ○ Waiting                             │
│  🌿 Environment    ○ Waiting                             │
│  🛡️ Opposition     ○ Standing by for attack              │
│  👑 Prime Minister ○ Deliberating after vote             │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Page 4 — Future Simulator

### 6.1 Purpose
Make the four simulated futures feel like windows into alternate worlds. The user should understand at a glance: which future is best, which is worst, where the policy is most vulnerable.

### 6.2 Full Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  FUTURE SIMULATOR                    Winning Option: [option name]   │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  RADAR OVERLAY — All 4 futures on one pentagon chart         │    │
│  │  5 axes: Economy, Sustainability, Satisfaction, Cost, Risk  │    │
│  │  4 semi-transparent fills (emerald/rose/indigo/amber)       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐      │
│  │  FUTURE A    │  FUTURE B    │  FUTURE C    │  FUTURE D    │      │
│  │  Optimistic  │  Pessimistic │  Tech-Driven │  Constrained │      │
│  │  emerald     │  rose        │  indigo      │  amber       │      │
│  │              │              │              │              │      │
│  │  Composite   │  Composite   │  Composite   │  Composite   │      │
│  │     81       │     42       │     80       │     61       │      │
│  │   STRONG     │   POOR       │   STRONG     │   MODERATE   │      │
│  │              │              │              │              │      │
│  │  [metrics    │  [metrics    │  [metrics    │  [metrics    │      │
│  │   bars]      │   bars]      │   bars]      │   bars]      │      │
│  └──────────────┴──────────────┴──────────────┴──────────────┘      │
│                                                                      │
│  COMPOSITE COMPARISON                                                │
│  Future A  ████████████████████  81  STRONG                        │
│  Future C  ████████████████████  80  STRONG                        │
│  Future D  ████████████░░░░░░░░  61  MODERATE                      │
│  Future B  █████████░░░░░░░░░░░  42  POOR                          │
│                                                                      │
│  Volatility: VOLATILE  Δ39  Most sensitive: Public Satisfaction     │
│                                                                      │
│  ─────────────────────────────────────────────────────────────────  │
│  ☠ BLACK SWAN ENGINE                                                │
│  Crisis: 🌊 Catastrophic 500-Year Flood          Resilience: 70.5  │
│  [see Black Swan card spec]                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.3 Future Card Design

```
┌──────────────────────────────────────────────────────────┐
│  [A]  FUTURE A — Optimistic              STRONG          │
│        gradient top border (emerald-600 → teal-500)      │
│        background: emerald-950/20                        │
│─────────────────────────────────────────────────────────│
│                                                          │
│        81                                                │
│    ─────────    ← large mono font                        │
│     STRONG                                               │
│                                                          │
│─────────────────────────────────────────────────────────│
│  📈 Economy       ████████████████████  87               │
│  🌿 Sustainability ████████████████░░░  78               │
│  👥 Satisfaction  █████████████████░░░  83               │
│  💰 Cost Effic.   ██████████████░░░░░  72               │
│  🛡️ Risk Score    █████████████████░░  85               │
│─────────────────────────────────────────────────────────│
│  📅 18 months   💵 $2.8B   👥 45M people                │
│─────────────────────────────────────────────────────────│
│  ✓ Strong economic multiplier                            │
│  ✓ High public adoption rate                             │
│  ⚠ Assumes stable political mandate                    │
└──────────────────────────────────────────────────────────┘

Metric bars:
  Track: bg-white/5, h-1.5, rounded-full
  Fill:  gradient matching future color, animated fill-from-left
  Value: mono text right-aligned
```

### 6.4 Radar Chart

```
Library: Recharts RadarChart

Config:
  Size:          500 × 400
  Axes:          5 (Economy, Sustainability, Satisfaction, Cost, Risk)
  gridType:      "polygon"
  polarGridLines: 5 rings at 20/40/60/80/100
  Tick labels:   white/60, text-xs

Per future Radar:
  fillOpacity:  0.15
  strokeWidth:  2
  stroke:       future color
  fill:         future color

Overlay toggle buttons:
  [A Optimistic] [B Pessimistic] [C Tech] [D Constrained]
  Click to show/hide individual futures on overlay
  All visible by default
```

### 6.5 Black Swan Card

```
┌──────────────────────────────────────────────────────────┐
│  ☠ BLACK SWAN EVENT                                      │
│  background: zinc-950/80   border: zinc-600/30           │
│─────────────────────────────────────────────────────────│
│  🌊  Catastrophic 500-Year Flood                         │
│       CRITICAL   ·   Infrastructure Domain               │
│─────────────────────────────────────────────────────────│
│  "The Technology-Led Transformation shows moderate       │
│   resilience against catastrophic flooding. Digital      │
│   delivery continues for 70% of citizens; however,      │
│   the physical Phase 2 stalls for 24 months..."         │
│─────────────────────────────────────────────────────────│
│  RESILIENCE       ███████████████████░  76               │
│  RECOVERY SPEED   ████████████████░░░░  62               │
│  FAILURE PENALTY  ████████████████████  82               │
│─────────────────────────────────────────────────────────│
│  FAILURE POINTS                              3 found     │
│  ⚠ GEOGRAPHIC_CONCENTRATION    [moderate]               │
│  ⚠ FUNDING_DEPENDENCY          [severe]                 │
│  ● TECHNOLOGY_DEPENDENCY       [minor]                   │
│─────────────────────────────────────────────────────────│
│  RESILIENCE SCORE                                        │
│                                                          │
│         70.5                                             │
│       RESILIENT                                          │
│  ████████████████████████░░░░  70.5 / 100               │
│                                                          │
│  Estimated recovery: 18–24 months                        │
│  Survival probability: MODERATE                          │
└──────────────────────────────────────────────────────────┘

On card reveal:
  1. header fades in
  2. crisis emoji stamps in (scale 2→1)
  3. narrative streams in (typewriter)
  4. bars fill simultaneously
  5. failure points slide in (staggered)
  6. score counts up 0→70.5 (large, 800ms)
  7. band badge stamps in (spring)
  8. card border pulses color × 1 based on band
```

---

## 7. Page 5 — Final Decision Report

### 7.1 Purpose
The full policy synthesis — exportable, printable, and visually structured as a government policy document. This should feel authoritative and complete.

### 7.2 Full Page Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  FINAL DECISION REPORT                     [Export PDF]  [Share]    │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  👑 PRIME MINISTER DECISION                    [gold glow]  │    │
│  │                                                             │    │
│  │  Chosen Option:  Technology-Led Transformation              │    │
│  │  Confidence:     84 / 100   ██████████████████████░        │    │
│  │  Consensus:      HIGH ·  5 of 6 ministers voted in favour  │    │
│  │─────────────────────────────────────────────────────────── │    │
│  │  Executive Summary                                          │    │
│  │  "The TITAN Cabinet has reached a strong consensus around   │    │
│  │   a technology-led transformation approach..."              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────┐  ┌──────────────────────────────┐   │
│  │  VOTE BREAKDOWN            │  │  SIMULATION SCORES           │   │
│  │  Option B: 5 votes (83%)   │  │  Best future: A (81)         │   │
│  │  [vote bars]               │  │  [mini radar chart]          │   │
│  └────────────────────────────┘  └──────────────────────────────┘   │
│                                                                      │
│  MINISTERIAL RATIONALE                                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Collapsible accordion — one row per minister                │   │
│  │  📈 Economic Minister said... [expand]                       │   │
│  │  💻 Technology Minister said... [expand]                     │   │
│  │  🛡️ Opposition raised... [expand — always open]             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  IMPLEMENTATION ROADMAP                                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Phase 1 ─── Phase 2 ─── Phase 3                            │   │
│  │  0–6mo       6–24mo      24–60mo                             │   │
│  │                                                              │   │
│  │  [Phase 1 card: actions + owner + budget %]                  │   │
│  │  [Phase 2 card: actions + owner + budget %]                  │   │
│  │  [Phase 3 card: actions + owner + budget %]                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──────────────────────┐  ┌───────────────────────────────────┐    │
│  │  SUCCESS METRICS     │  │  RISKS & MITIGATIONS             │    │
│  │  Table: metric /     │  │  Table: risk / mitigation        │    │
│  │  target / deadline   │  │  colour-coded by severity        │    │
│  └──────────────────────┘  └───────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  ☠ BLACK SWAN RESILIENCE                                    │    │
│  │  [same card as simulation page — smaller variant]           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  DISSENTING VIEWS                                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  🛡️ "The Opposition raised: [concern]"                      │    │
│  │  👑 "PM response: [why overruled]"                          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.3 PM Decision Hero Card

```
┌──────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████████████████    │
│  ████ gold gradient top border (full width, 3px) ████    │
│  ████████████████████████████████████████████████████    │
│                                                          │
│  👑  PRIME MINISTER DECISION                             │
│      gold text, Space Grotesk, 13px semibold uppercase   │
│                                                          │
│  Technology-Led Transformation                           │
│  ← h2, white, 30px, Space Grotesk bold                  │
│                                                          │
│  Confidence                                              │
│  ████████████████████████░░░  84 / 100                   │
│                                                          │
│  HIGH CONSENSUS  ·  5 of 6 ministers  ·  83.3% vote     │
│  ← badges: emerald (consensus), violet (vote count)     │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  "The TITAN Cabinet has reached a strong consensus       │
│   around a technology-led approach. The Economic         │
│   Minister's fiscal analysis, the Technology Minister's  │
│   implementation roadmap, and simulation data across     │
│   three of four futures support this option as the       │
│   highest-value, lowest-risk path forward..."            │
│                                                          │
│  ← italic, text-secondary, 15px, leading-relaxed        │
└──────────────────────────────────────────────────────────┘

Reveal animation:
  1. Gold border draws from left to right (800ms)
  2. Card fades in (400ms)
  3. Title slides up (300ms)
  4. Confidence bar fills (700ms)
  5. Summary text streams in (typewriter)
  6. Subtle confetti burst (1s, muted gold particles)
```

### 7.4 Implementation Roadmap

```
Phase cards connected by timeline line:

─────────────────────────────────────────────────────────────
  [Phase 1]  ──────────────  [Phase 2]  ─────────  [Phase 3]
  0–6 months                 6–24 months            24–60 months
─────────────────────────────────────────────────────────────

Each phase card:
┌──────────────────────────────────────────────────────────┐
│  PHASE 1 — Foundation                    Months 0–6      │
│  Owner: Technology Ministry                              │
│  Budget: 30% of total allocation                        │
│─────────────────────────────────────────────────────────│
│  ✓ Establish national digital skills registry           │
│  ✓ Deploy 50 AI-powered retraining centres              │
│  ✓ Launch e-government portal for job matching          │
│─────────────────────────────────────────────────────────│
│  KPIs: Registry live by month 3 · Centres open month 5  │
└──────────────────────────────────────────────────────────┘
```

### 7.5 Success Metrics Table

```
┌──────────────────────────────────────────────────────────┐
│  METRIC                TARGET              DEADLINE      │
│─────────────────────────────────────────────────────────│
│  Unemployment rate     Below 8%            24 months     │
│  Digital literacy      +40% penetration    36 months     │
│  GDP growth            Return to 3%+       18 months     │
│  Job placement rate    70% of trained      30 months     │
│  Carbon footprint      −15% from baseline  48 months     │
│─────────────────────────────────────────────────────────│
│  Review: Quarterly for Year 1, then annual               │
└──────────────────────────────────────────────────────────┘
```

### 7.6 Risks & Mitigations Table

```
┌──────────────────────────────────────────────────────────┐
│  RISK                              MITIGATION            │
│─────────────────────────────────────────────────────────│
│  🔴  Political reversal after     Ring-fence budget in   │
│      election cycle               multi-year fiscal law  │
│                                                          │
│  🟡  Digital divide worsens       Mandatory analog       │
│      for rural elderly            fallback in Phase 1    │
│                                                          │
│  🟡  Implementation costs         Cost escalation clause │
│      spike 40% above estimate     + quarterly review     │
│─────────────────────────────────────────────────────────│
│  ← Row colours: red (HIGH), yellow (MEDIUM), green (LOW) │
└──────────────────────────────────────────────────────────┘
```

---

## 8. Micro-Interaction Catalogue

### 8.1 Scroll-Triggered Entry (all cards)

```
Class: .titan-entry
State: opacity:0, translateY:20px
Trigger: IntersectionObserver (threshold: 0.1)
Reveal: opacity:1, translateY:0  (350ms ease-out)
Stagger: 80ms per sibling card
```

### 8.2 Minister Avatar Hover

```
Avatar circle: w-8 h-8 rounded-full  (minister color gradient)
Hover: scale(1.1) + ring(2px minister color)  (200ms spring)
Tooltip: minister name + role description
```

### 8.3 Number Counter

```
All large numbers (composite scores, vote counts, resilience scores):
  Start: 0
  End: target value
  Duration: 800ms
  Easing: ease-out cubic
  Font: JetBrains Mono
```

### 8.4 Progress Bar Fill

```
All progress bars:
  Initial: width: 0%
  Animated: width: {value}%  (700ms ease-out)
  Trigger: IntersectionObserver
  Fill: gradient from [metric color] to [metric color light]
```

### 8.5 SSE Live Indicator

```
While SSE connection is active:
  Green dot (w-2 h-2) in navbar pulsing
  Label: "Live"
  On disconnect: dot turns grey, label: "Disconnected"
  On reconnect: yellow dot, label: "Reconnecting..."
```

### 8.6 Toast Notifications (Sonner)

```
Phase changes:        system toasts (dark, icon, phase color)
Minister responds:    bottom-left toast with minister avatar
Vote cast:            "📈 Economic Minister voted: Option B"
Error:                red toast, persistent, close button
Session complete:     gold toast "Decision ready" + link to report
```

### 8.7 Skeleton Loading States

```
Before SSE data arrives, all panels show skeleton cards:
  Lines: animate-shimmer class (moving gradient)
  Avatar circles: shimmer circles
  Progress bars: shimmer tracks (no fill)
  Text blocks: 3-line shimmer pattern
```

---

## 9. Component File Map

```
apps/web/src/
├── app/
│   ├── layout.tsx               ← Root: fonts, metadata, NavShell
│   ├── globals.css              ← Design token system (CSS vars)
│   ├── page.tsx                 ← Landing / Problem Workspace
│   ├── parliament/
│   │   └── page.tsx             ← AI Parliament (SSE-driven)
│   ├── simulation/
│   │   └── page.tsx             ← Future Simulator
│   └── report/
│       └── page.tsx             ← Final Decision Report
│
├── components/
│   ├── layout/
│   │   ├── NavShell.tsx         ← Sidebar + Topbar wrapper
│   │   ├── Sidebar.tsx          ← Navigation + session status
│   │   └── Topbar.tsx           ← Phase indicator + live badge
│   │
│   ├── parliament/
│   │   ├── DebateFeed.tsx       ← Scrolling message feed
│   │   ├── DebateCard.tsx       ← Single message card (all types)
│   │   ├── PhaseTimeline.tsx    ← Sticky 5-step progress
│   │   ├── CabinetPanel.tsx     ← Right panel: minister status
│   │   ├── VotePanel.tsx        ← Right panel: vote tally
│   │   ├── LiveMetrics.tsx      ← Word count, arguments, vetoes
│   │   ├── MinisterAvatar.tsx   ← Icon + color dot + tooltip
│   │   └── PhaseSystemMessage.tsx ← Full-width phase separators
│   │
│   ├── simulation/
│   │   ├── FutureGrid.tsx       ← 4-card future layout
│   │   ├── FutureCard.tsx       ← Single future: scores + narrative
│   │   ├── RadarOverlay.tsx     ← Recharts radar, all 4 futures
│   │   ├── CompositeBar.tsx     ← Ranked composite comparison
│   │   ├── VolatilityBadge.tsx  ← stable/moderate/volatile
│   │   ├── MetricRow.tsx        ← Metric label + animated bar + value
│   │   └── BlackSwanCard.tsx    ← Crisis + 3 measurements + score
│   │
│   ├── report/
│   │   ├── PMHeroCard.tsx       ← Gold PM decision reveal card
│   │   ├── VoteBreakdown.tsx    ← Compact vote tally
│   │   ├── ImplementationRoadmap.tsx ← Phase timeline
│   │   ├── SuccessMetrics.tsx   ← Metrics table
│   │   ├── RisksTable.tsx       ← Risks + mitigations table
│   │   ├── DissentsAccordion.tsx ← Ministerial dissents
│   │   └── MiniRadar.tsx        ← Compact simulation summary
│   │
│   └── ui/                      ← shadcn/ui primitives + extensions
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       ├── score-counter.tsx    ← Animated number counter
│       ├── minister-badge.tsx   ← Colored role badge
│       └── status-badge.tsx     ← Phase status indicator
```

---

## 10. Fonts & External Assets

```html
<!-- Load in layout.tsx -->
<link
  href="https://fonts.googleapis.com/css2?
  family=Space+Grotesk:wght@400;500;600;700&
  family=Inter:wght@300;400;500;600;700;800;900&
  family=JetBrains+Mono:wght@400;500;600&
  display=swap"
  rel="stylesheet"
/>

Usage:
  Space Grotesk → All page titles, hero headings, TITAN wordmark
  Inter         → All body copy, labels, UI text
  JetBrains Mono → All scores, percentages, timestamps, code

Icon library: lucide-react (already installed)
Chart library: recharts (RadarChart, BarChart, PolarGrid)
Animation: framer-motion (page transitions, card reveals)
Toast: sonner (already in stack)
```

---

## 11. Hackathon Differentiation Checklist

```
UI Differentiation that wins hackathon demos:

  □  Phase Timeline — judges see exactly where TITAN is at a glance
  □  Live green pulse dot — communicates "AI is running right now"
  □  Opposition attack card — red glow, targeted ministers flash
     → Most visually memorable moment in the whole pipeline
  □  Vote panel live-filling — bars extend as each vote arrives
  □  Radar overlay — all 4 futures on one chart is instantly impressive
  □  Composite score counter — 0→81 count-up is satisfying
  □  Black Swan reveal — crisis name + stamped badge = "moment"
  □  PM hero card gold reveal — feels like a verdict, not a dashboard
  □  Dissenting views section — signals intellectual depth
  □  Implementation roadmap — makes AI output feel "real" and actionable
  □  Space Grotesk + gold gradient text — premium visual identity
  □  Dark void background with blue/gold orbs — no "form on white" feel
  □  JetBrains Mono for scores — data feels authoritative
```

---

*TITAN UI — Every pixel earns its place. Every animation means something.*
