# HANDOFF.md — FREQ AI Session Continuity & Architecture Blueprint

**Project:** FREQ AI Sophisticated Operational Lattice (SOL)
**Codename:** Antigravity
**Version:** 3.0
**Date:** February 13, 2026
**Authority:** Chief Dre — Sovereign Intent Originator (Level 0)
**Primary GitHub:** `https://github.com/dre-orchestrator/freq`
**Local Path:** `/Users/dre.orchestrator.ai/FREQ-AI-VERTEX/`
**Classification:** Proprietary / Strategic

---

## DEPRECATED ACCOUNTS — DO NOT USE

| Account | Status | Notes |
|---------|--------|-------|
| `dre-orchestrator-ai` | DEPRECATED | Old upstream, PR #8 never merged |
| `dre-achitect` | DEPRECATED | Fork, never used for production |
| `dre-architect` | DEPRECATED | Alternate fork reference |

**Only use:** `https://github.com/dre-orchestrator/freq`

---

# PART ONE: CURRENT STATE

## 1.1 Project Identity

FREQ AI SOL is a multi-node AI orchestration system for autonomous maritime barge drafting operations. The system eliminates manual human labor and drones from barge loading operations by coordinating AI agents across the full operational cycle: draft measurement, crane operations, ballast optimization, stability monitoring, regulatory compliance, and cost analysis.

**The 4-Hour Problem:** Currently, measuring barge draft requires 2–4 crew members working on deck for ~4 hours per barge. This exposes workers to Man Overboard risk, produces imprecise measurements (+/- several inches), and delays cargo operations.

**The Solution:** FREQ AI reduces this to ~15 minutes using sensor fusion (LiDAR/IoT) + AI inference + governance, with zero human deck exposure. Current simulation achieves ~10.9 minutes.

## 1.2 Phase Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | COMPLETE | Initial PoC, lattice concept validation |
| Phase 2: Enterprise Lattice | COMPLETE | Lattice Core developed, tested, published. Production-ready. |
| Phase 3: Digital Twin + Edge AI | ACTIVE | 6-phase simulation built, 3D visualization platform TBD |

## 1.3 Platform Status

**Platform selection is PENDING.** Do not commit to any platform.

| Platform | Status |
|----------|--------|
| Google Cloud Vertex AI | Under evaluation (Startup Program pending) |
| Azure AI Foundry | Phase 2 legacy — do not deploy new work here |
| Firebase | Abandoned — deployment blocker for 24+ hours |
| Vertex Workbench / Colab | Moving away — not suitable for visual demos |

## 1.4 Team Lanes

| Role | Agent | Directive |
|------|-------|-----------|
| Backend Engineer | Claude Code | BUILD — coding, debugging, architecture implementation |
| Research | Chrome (Coworker) | Research platforms, technologies, market intel |
| Strategic Planning | Opus | High-level strategy, architecture decisions |
| Sovereign | Chief Dre (Level 0) | All directives originate here |

---

# PART TWO: V3 ARCHITECTURAL BLUEPRINT

## 2.1 FREQ Law — Constitutional Framework

FREQ Law is the binding constitutional constraint governing all lattice operations. It cannot be modified by any node. Authority derives solely from the Sovereign Intent of Chief Dre.

| Tenet | Requirement | Implementation |
|-------|-------------|----------------|
| **Fast** | Operations complete within latency thresholds | Runtime target: <2000ms for sensor processing + report generation. Prohibits unnecessary hops, mandates parallelization. |
| **Robust** | Redundancy, safety mechanisms, graceful degradation | No Happy Path implementations. Error boundaries on all externals. Pulse Protocol for edge connectivity loss. Human interlocks for safety-critical actions. |
| **Evolutionary** | Learn from errors, continuous improvement | Reflexion Loop for self-correction. No hard-coded values. Schema versioning. Operational data feeds training pipelines. |
| **Quantified** | Every action observable and auditable | Comprehensive Cognitive Audit Trail. JSON-LD provenance records. Trust Scores quantify output confidence. Full forensic reconstruction capability. |

**Digital Constitution:** Immutable policy store on Google Cloud Spanner. Append-only — records never modified or deleted. New records supersede old while preserving history. Strong global consistency ensures a VETO is immediately and universally enforceable.

## 2.2 Chain of Command (6-Level Hierarchy)

```
Level 0: Sovereign Intent Originator (Chief Dre)
         └── Natural Language Orchestration, Vibe Coding
         └── Ultimate human authority, final escalation point

Level 1: Strategic Synthesis Core (SSC)
         └── Substrate: Gemini 3.0 Thinking
         └── Central Nervous System — Decomposition of intent → DAG of atomic tasks
         └── Multi-model routing, Reflexion Loop replanning

Level 2: Cognitive Governance Engine (CGE)
         └── Substrate: Gemini 3.0 Pro (Temp 0.0, Top-K 1 — deterministic)
         └── Non-bypassable policy authority, absolute VETO power
         └── Enforces Digital Constitution, validates all proposed operations

Level 3: Strategic Intelligence Lead (SIL)
         └── Substrate: Gemini 3.0 Flash
         └── Educator/Librarian — manages Knowledge Substrate
         └── RAG support, historical pattern analysis

Level 4: System Architect (SA) / Paradigm Design
         └── Substrate: Gemini 3.0 Pro
         └── Strategic plans → technical schemas
         └── Heritage Code Parsing for legacy integration

Level 5: Runtime Realization Node (TOM — Tactical Operations Module)
         └── Substrate: Gemini 3.0 Flash
         └── SOLE authorized executor — only node with write/API/hardware permissions
         └── Controls LiDAR drones, processes sensor data, generates reports
```

## 2.3 Pure Gemini Mesh Architecture

The lattice operates as a homogeneous Gemini deployment on Google Cloud Vertex AI. No external LLMs in production.

| Substrate | Capability | Nodes |
|-----------|-----------|-------|
| Gemini 3.0 Thinking | Highest reasoning, extended context, deep planning | SSC (Level 1) |
| Gemini 3.0 Pro | Analytical reasoning, deterministic compliance | CGE (Level 2), SA (Level 4) |
| Gemini 3.0 Flash | High-speed throughput, low latency | SIL (Level 3), TOM (Level 5) |

**Topology:** K4 hyper-connected — complete graph, network diameter of 1, vertex connectivity of 3 (three simultaneous node failures required to isolate a fourth).

**Communication:** Semantic Bus via Agent-to-Agent Protocol. Typed, schema-validated JSON payloads with request ID, intent vectors, timestamps, source/target node IDs, governance hash.

## 2.4 Byzantine Fault Tolerance

- Critical state changes require 75% majority (k=3 of 4 nodes: SSC, CGE, SIL, SA)
- CGE VETO supersedes consensus — even 3 approvals blocked if CGE vetoes
- Protects against hallucination propagation through the lattice

## 2.5 Knowledge Substrate Database (Tiered Memory)

| Tier | Store | Purpose |
|------|-------|---------|
| **Hot (Retrieval)** | Vertex AI Search | Embedded docs for semantic RAG — policies, regulations, procedures, specs |
| **Cold (Analytical)** | BigQuery | Cognitive Audit Trail — immutable JSON-LD provenance records for forensic reconstruction |
| **Raw (Archive)** | Cloud Storage ("Iron Vault") | LiDAR point clouds, drone telemetry, imagery, sensor logs. Tiered lifecycle management. |

---

# PART THREE: MARITIME BARGE DRAFTING MISSION

## 3.1 Mission Overview

**Primary:** Automate barge draft measurement — 4 hours manual → 15 minutes automated, zero human deck exposure, 99.8% accuracy target.

**Secondary:** Validate FREQ AI architecture under real-world maritime conditions (variable connectivity, harsh environment, regulatory complexity, safety criticality).

**Tertiary:** Establish patterns for expansion to cargo management, fleet tracking, maintenance prediction.

## 3.2 Sensor Technology

**LiDAR (Primary):** Near-infrared laser pulses (905nm/1550nm), +/-2-5mm precision, millions of points/second. Water absorbs/scatters IR → waterline appears as transition zone between hull returns and absent water returns.

**Drone Platform:** 15-20 min endurance, 2-5kg payload, "lawnmower pattern" scanning (~3 min/barge), GPS+RTK positioning, return-to-home failsafes.

**Sensor Alternatives (V3 Addition):**

| Technology | Application | Notes |
|------------|-------------|-------|
| LiDAR (airborne) | Full hull geometry + waterline | Primary approach |
| Ultrasonic sensors (hull-mounted) | Continuous draft monitoring | Retrofit challenges on existing fleet |
| Pressure transducers | Water depth at hull | Requires calibration, sensor drift |
| Camera + CV | Visual draft mark reading | Works with existing infrastructure |
| Radar (marine) | Surface-level measurement | Supplementary data source |

**For demo purposes:** Physical hardware not required. The Python simulation engine generates realistic sensor data that feeds the digital twin.

## 3.3 The 6-Phase Workflow (V3 — Authoritative)

```
Phase 1: PRE-SURVEY    — Pre-Load Draft Survey
Phase 2: BALLAST-ADJ   — Ballast Adjustment
Phase 3: CRANE-POS     — Crane Positioning
Phase 4: CARGO-LOAD    — Cargo Loading Operations
Phase 5: TRIM-CORR     — Trim Correction
Phase 6: FINAL-SURV    — Final Draft Survey
```

**Target:** Complete cycle in 15 minutes (900 seconds).
**Current Performance:** ~10.9 minutes simulated (under target).

## 3.4 Data Processing Pipeline

1. Point cloud registration (align to vessel coordinate system)
2. Noise filtering (spray, debris, atmospheric)
3. Surface reconstruction (points → mesh)
4. Waterline detection (IR + point cloud analysis)
5. Wave action analysis (extract stable reference)
6. Displacement calculation (naval architecture algorithms)
7. Draft derivation (from hydrostatic characteristics)
8. Stability curve validation
9. Report generation → Sovereign's tablet
10. Audit trail → BigQuery

**Processing target:** <30 seconds, 99.8% accuracy vs reference measurements.

## 3.5 Deployment Roadmap

| Phase | Focus | Key Activities |
|-------|-------|---------------|
| Phase 1: Foundation | Core lattice + Shadow Mode | Deploy nodes on Vertex AI, load Digital Constitution, validate against historical data, achieve 95% Trust Score |
| Phase 2: Controlled | Physical drone ops, limited fleet | Platform certification, regulatory approvals (USCG/FAA), parallel human/automated measurement, refine algorithms |
| Phase 3: Scaled | Full fleet, role transition | Fleet expansion, human transition to oversight/exception, activate training pipeline, Reflexion Loop analysis |

## 3.6 Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| Efficiency | Measurement time | 4 hours → 15 minutes (93.75% reduction) |
| Safety | Deck exposure hours | >90% reduction |
| Safety | Measurement-related injuries | Zero |
| Quality | Measurement accuracy | 99% within +/- 1 inch |
| Quality | Documentation completeness | 100% with full provenance |
| Regulatory | Audit on demand | Complete trail for any measurement |

---

# PART FOUR: PHASE III SIMULATION — WHAT EXISTS

## 4.1 Implemented Modules

All modules live in `src/sol/simulation/`. Pure Python, zero external dependencies.

### state_objects.py — Digital Shadow State Models
- `DraftState`, `CraneState`, `StabilityState` — JSON-serializable dataclasses
- `WorkflowPhase` enum — 6 phases with `WORKFLOW_PHASE_ORDER`
- `SimulationState` — composite holding all sub-states + workflow metadata
- All implement `.to_dict()` / `.to_json()` for Eclipse Ditto-style serialization

### draft_monitor.py — 4-Point Draft Sensor Simulation
- Simulates ultrasonic sensors at fore, aft, port, starboard
- Configurable base draft and noise range
- Per-sensor offsets for load/ballast effects
- Automatic mean draft computation

### crane_controller.py — Signal Codes, G-Codes, Safety
- Signal codes: `SIG-000` (IDLE) → `SIG-910` (OVERLOAD)
- G-codes: `G00` (rapid) → `G99` (emergency stop)
- Safety: boom angle clamp (15-80 deg), hook height floor (2ft), capacity check
- State machine: IDLE → POSITIONED → ACTIVE → LOWERING → IDLE, plus OVERLOAD/E_STOP

### stability_analyzer.py — Trim, Heel, Displacement, GM
- Trim = fore - aft (positive = bow-heavy)
- Heel = angle from port/starboard draft difference
- Displacement = volume x water density (long tons)
- GM = BM - BG approximation
- Status: STABLE / CAUTION / CRITICAL (configurable thresholds)

### workflow_engine.py — 6-Phase FSM
- Ordered transitions through 6 phases
- 15-minute target (900s)
- Per-phase and total elapsed time tracking
- `get_summary()` → JSON-serializable report

### watchdog_agent.py — Safety Checks
- 4 categories: draft limits, crane overload, stability margins, phase timeouts
- Coded violations: `DFT-001`–`DFT-004`, `CRN-001`–`CRN-003`, `STB-001`–`STB-005`, `WFL-001`
- Overall: PASS (clean) / ALERT (warnings) / STOP (critical halt)

### demo_runner.py — Full Simulation Orchestrator
- Orchestrates all 6 phases with realistic cargo loading
- 4 cargo lifts: 8K, 12K, 15K, 10K lbs with progressive draft increase
- Ballast adjustments and trim corrections
- Produces all 5 SOL Event Log prefixes
- Completes in ~10.9 min simulated

## 4.2 Authoritative Data Structures

**Do NOT modify these keys without Level 0 approval.**

```python
# Draft Reading
{"fore": 10.45, "aft": 10.82, "port": 10.58, "starboard": 10.67, "mean": 10.63, "unit": "ft"}

# Crane Signal
{"load_weight": 1800, "max_capacity": 3200, "boom_angle": 42.3, "slew_bearing": 195.7,
 "hook_height": 16.2, "status": "LOADING", "signal_code": "SIG-LOAD", "g_code": "G01"}

# Stability
{"trim": 0.185, "heel": -0.092, "displacement": 3200, "gm": 3.65, "status": "NOMINAL"}

# Workflow
["PRE-SURVEY", "BALLAST-ADJ", "CRANE-POS", "CARGO-LOAD", "TRIM-CORR", "FINAL-SURV"]
```

## 4.3 SOL Event Log Format (Strict)

```
[SOL.DraftMonitor]      draft_readings: fore=X.XXft aft=X.XXft port=X.XXft starboard=X.XXft mean=X.XXft
[SOL.CraneController]   signal=SIG-XXX boom_angle=XX.X slew=XXX.X hook_height=XX.X load=XXXX.X status=STATUS
[SOL.StabilityAnalyzer]  trim=X.XXX heel=X.XXX displacement=XXXX.X gm=X.XXX status=STATUS
[SOL.WorkflowEngine]    phase_active: STEP-ID elapsed=XXs
[SOL.WatchdogAgent]     safety_check: PASS | ALERT | STOP
```

## 4.4 Test Status (February 2026)

| Test File | Tests | Status |
|-----------|-------|--------|
| test_simulation.py | 56 | PASS |
| test_sol.py | All | PASS |
| test_workflow.py | All | PASS |
| test_sil_advanced.py | All | PASS |
| test_sil_agent.py | — | 4 pre-existing failures (Phase II, not simulation) |

## 4.5 Commands

```bash
# Run simulation
PYTHONPATH=src ./venv/bin/python -m sol.simulation.demo_runner

# Test all
PYTHONPATH=src ./venv/bin/python -m pytest tests/ -v

# Test simulation only
PYTHONPATH=src ./venv/bin/python -m pytest tests/test_simulation.py -v

# Lint
PYTHONPATH=src ./venv/bin/python -m ruff check src/

# Format
./venv/bin/python -m black src/
```

---

# PART FIVE: GOOGLE STARTUP PROGRAM

## 5.1 The $350K Ask

| Detail | Value |
|--------|-------|
| Program | Google for Startups Cloud Program — AI Tier |
| Total credits | $350,000 over 2 years |
| Breakdown | $200K (Scale) + $150K (AI add-on) |
| Year 1 | $250K at 100% coverage |
| Year 2 | 20% monthly reimbursement capped at $100K |
| Additional | $12K Enhanced Support + $10K third-party models via Vertex AI |
| Pipeline | Spoke with Sylvan (REQ Consultant) → Referred to Sulgi (BD) |
| Meeting | Scheduled week of Feb 10-14, 2026 |

## 5.2 BD Evaluation Criteria

Sulgi evaluates:
1. **Visual demo proof** — live, shareable URL showing maritime ops
2. **GCP spend trajectory** — $8K/mo → $100K+/yr ramp
3. **Competitive displacement** — Azure → GCP migration story
4. **AI as core technology** — multi-agent lattice, not just using an API
5. **Reference case study potential** — showcase for Google marketing

## 5.3 Demonstration Requirements

The Phase 3 demo must showcase:
- Complete 6-phase maritime barge drafting workflow
- Real-time 3D visualization (not terminal output)
- Lattice governance in action (consensus, VETO)
- Cost savings data (98.7% vs manual, 99.8% vs drones)
- Audit trail / compliance documentation
- Must be shareable via URL (not local-only)

## 5.4 Market Position

| Metric | Value |
|--------|-------|
| Maritime AI market (2024) | $4.3 billion |
| Maritime AI market (2030) | $32.7 billion |
| CAGR | 40.6% |
| FREQ unique position | First platform unifying full barge drafting cycle (Pre-Load → Ballast → Crane → Cargo → Trim → Final Survey) with AI orchestration + digital twin for US inland waterways |

## 5.5 Cost Analysis

| Method | Annual Cost | vs SOL |
|--------|-------------|--------|
| SOL Autonomous | $2,113/year | — |
| Manual Surveyors | $162,000/year | SOL saves 98.7% |
| Drone-Based | $1,000,000/year | SOL saves 99.8% |

## 5.6 GCP Spend Trajectory

| Period | Monthly Spend |
|--------|--------------|
| Month 1-6 | $8-15K |
| Month 6-12 | $12-25K |
| Month 12-18 | $30-60K |
| Month 18-24+ | $100K+/year (paid, post-credits) |

---

# PART SIX: CONSTRAINTS & DIRECTIVES

## 6.1 What NOT To Do

- Do NOT use `dre-orchestrator-ai` GitHub account (deprecated)
- Do NOT use `dre-achitect` or `dre-architect` accounts (deprecated)
- Do NOT use Vertex AI Agent Designer
- Do NOT deploy to Azure (Phase 2 legacy)
- Do NOT refactor Phase 2 Agent Core (SSC, CGE, SIL) unless directed by Level 0
- Do NOT modify authoritative data structure keys without Level 0 approval
- Do NOT select a deployment platform — that decision is pending
- Do NOT build terminal UIs — building for visual/web (React/Three.js/Cesium)

## 6.2 Architecture Principles

1. **State-First:** Hardware is a "Digital Shadow." Code updates JSON State Objects (Eclipse Ditto style), not hardware directly.
2. **Simulation is Data Layer:** The Python simulation feeds the visualization. It is the source of truth.
3. **No Terminal UIs:** Building for visual/web interaction once platform is selected.
4. **Pure Python:** Simulation module has zero external dependencies — only stdlib and dataclasses.

## 6.3 Pending Priorities (Ordered)

| # | Priority | Status | Detail |
|---|----------|--------|--------|
| 1 | **3D Visualization Platform** | TBD | Find platform for 3D graph, UI/UX, maritime scene. Candidates: React+Three.js, React Three Fiber, Cesium, Deck.gl |
| 2 | **Deploy to Shareable URL** | BLOCKED | Need platform selection first. Must be demo-able via link for Google meeting |
| 3 | **Pitch Materials** | NOT STARTED | Visual proof for Sulgi. Problem → Solution → Demo → Architecture → GCP services → Spend → $350K ask |
| 4 | **Platform Selection** | PENDING | Chief Dre decides. Not Azure, not Firebase. GCP under evaluation. |
| 5 | **Edge-Core Governance** | NOT STARTED | Local policy agent + central CGE sync prototype |
| 6 | **Containerize Agents** | NOT STARTED | Docker packaging for selected platform |

---

# PART SEVEN: REPOSITORY STRUCTURE

```
FREQ-AI-VERTEX/                              # Local path
├── src/sol/
│   ├── __init__.py                          # SOL package (Phase II core)
│   ├── agents/                              # SSC, SIL agents
│   ├── audit/                               # BigQuery audit trail
│   ├── blueprint/                           # FREQ blueprint config
│   ├── consensus/                           # k=3 quorum consensus
│   ├── demo.py                              # Phase II lattice demo
│   ├── governance/                          # FREQ LAW, veto authority
│   ├── nodes/                               # Lattice nodes (StrategicOP, GOVEngine, etc.)
│   ├── orchestration/                       # Workflow orchestrator
│   └── simulation/                          # ★ PHASE III ★
│       ├── __init__.py
│       ├── __main__.py                      # python -m entry point
│       ├── state_objects.py                 # Digital Shadow state models
│       ├── draft_monitor.py                 # 4-point draft sensor sim
│       ├── crane_controller.py              # Signal codes, G-codes, safety
│       ├── stability_analyzer.py            # Trim, heel, displacement, GM
│       ├── workflow_engine.py               # 6-phase barge drafting workflow
│       ├── watchdog_agent.py                # Safety checks (PASS/ALERT/STOP)
│       └── demo_runner.py                   # Full simulation orchestrator
├── tests/
│   ├── test_sol.py                          # Phase II tests
│   ├── test_simulation.py                   # Phase III tests (56)
│   ├── test_workflow.py
│   ├── test_sil_advanced.py
│   └── test_sil_agent.py                   # 4 pre-existing failures
├── config/
├── docs/
├── knowledge/
├── pyproject.toml
├── CLAUDE.md                                # System instructions v5.0
├── HANDOFF.md                               # This document
└── venv/                                    # Python 3.9+ virtual env
```

---

# PART EIGHT: NEXT PROMPT

Copy and paste this into a fresh Claude Code session:

---

> **Continue FREQ AI project from HANDOFF.md.**
>
> I am Chief Dre, Sovereign Intent Originator (Level 0). Read `HANDOFF.md` and `CLAUDE.md` at the repo root for full context.
>
> **Repo:** `https://github.com/dre-orchestrator/freq`
>
> **Current state:**
> - Phase 2 (Lattice Core): COMPLETE
> - Phase 3 (Digital Twin + Simulation): ACTIVE — 6-phase simulation built, 56 tests passing, ~10.9 min workflow
> - Platform: TBD — do not select or deploy to any platform without my directive
>
> **Your role:** Backend Engineer. You BUILD. Stay in your lane.
>
> **Immediate task:** [DESCRIBE WHAT YOU NEED]
>
> The simulation works. Tests pass. I need [NEXT OBJECTIVE] now.

---

*End of HANDOFF.md*
*Generated: February 13, 2026*
*Version: 3.0*
*Repo: https://github.com/dre-orchestrator/freq*
*Authority: Chief Dre, Sovereign Intent Originator*
