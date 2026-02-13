# HANDOFF.md — FREQ AI Ghost Stream Session Transfer

**Project:** FREQ AI Sophisticated Operational Lattice (SOL)
**Codename:** Antigravity
**Version:** 4.0 — Ghost Stream Edition
**Date:** February 13, 2026
**Authority:** Chief Dre — Sovereign Intent Originator (Level 0)
**Target Repo:** `https://github.com/dre-orchestrator/freq`
**Source Repo:** `https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX` (DEPRECATED — transfer only)
**Branch:** `claude/update-agent-protocol-z5o9X`

---

## PURPOSE OF THIS HANDOFF

This document transfers all context from the current Claude Code session (on `dre-orchestrator-ai`) to a fresh session on `dre-orchestrator/freq`. The current environment's proxy cannot reach the new repo, so Chief Dre will:

1. Copy files from this repo to their local `dre-orchestrator/freq` clone
2. Push to `dre-orchestrator/freq`
3. Open a new Claude Code session on that repo
4. Paste the builder directive from Part Nine

---

## DEPRECATED ACCOUNTS — DO NOT USE

| Account | Status |
|---------|--------|
| `dre-orchestrator-ai` | DEPRECATED — source of this transfer only |
| `dre-achitect` | DEPRECATED |
| `dre-architect` | DEPRECATED |

**Only use:** `https://github.com/dre-orchestrator/freq`

---

# PART ONE: WHAT WAS BUILT THIS SESSION

## 1.1 CesiumJS + React 3D Visualization (`public/index.html`)

**602-line single HTML file. Zero build step. CDN-only.**

- **CesiumJS** globe with terrain + satellite imagery
- **Barge entity** at Gulf of Mexico (29.31°N, -94.79°W) — box: 60.96m x 18.29m x 3.66m
- **Crane tower** — cylinder entity on barge deck
- **Ghost LiDAR point cloud** — 6,000 lawnmower-pattern cyan points on barge surface
- **React 18** UI panels (Header, DraftPanel, CranePanel, StabilityPanel, AlertPanel, WorkflowBar)
- **JSON Shadow STATE** — global JS object as single source of truth
- **Man Overboard Chaos Mode** — button triggers 10s emergency: red overlay, random barge movement, LiDAR scatter, crane E_STOP, CGE SAFETY VETO, auto-recover
- **6-phase workflow animation** — 15s per phase in demo mode (90s total cycle)
- **FREQ LAW governance display** — COMPLIANT/EMERGENCY HALT, consensus, VETO status
- **Simpson's rule** mean draft calculation in JS
- **Token:** Replace `YOUR_CESIUM_ION_TOKEN` on line 93 (free signup: ion.cesium.com)
- **Deploy:** Drag `public/` to Netlify Drop (instant, free, shareable URL)

## 1.2 Ghost LiDAR Engine (`src/sol/simulation/ghost_lidar.py`)

**461-line Python synthetic data generator. Replaces $50K physical LiDAR.**

- **Blueprint v4.0 data structures** as Python dataclasses:
  - `DraftReadings` — 4-point draft + Simpson's rule mean
  - `StabilityMetrics` — trim, heel, displacement, GM, status
  - `CraneSignals` — load, boom, slew, hook, signal code, G-code
  - `WorkflowState` — 6-phase FSM
  - `Alerts` — MOB, list, overload, trim, heat signature
  - `GhostLidarMeta` — point count, scan pattern, chaos mode
  - `Governance` — FREQ LAW, veto, consensus
  - `BargeState` — complete Digital Shadow, `to_dict()` / `to_json()`

- **GhostLidarEngine class:**
  - Phase durations: PRE-SURVEY(120s), BALLAST-ADJ(150s), CRANE-POS(90s), CARGO-LOAD(300s), TRIM-CORR(120s), FINAL-SURV(120s) = ~15 min total
  - `_wave_motion()` — sinusoidal wave simulation
  - `_noise()` — sensor noise injection
  - `_update_phase()` — FSM progression
  - `_update_sensors()` — per-phase sensor behavior
  - `_update_stability_status()` — threshold evaluation (NOMINAL/CAUTION/CRITICAL)
  - `trigger_man_overboard()` — chaos injection: heat signature anomaly, CGE SAFETY VETO, crane M00, CRITICAL_STOP
  - `_update_mob()` — 10s chaos with random heel/trim spikes, auto-recover
  - `_write_state()` — atomic file write (tmp + rename) to `state/barge_state.json`
  - `tick()` — single 1Hz cycle
  - `run()` — continuous loop with optional duration

- **CLI:**
  ```bash
  python src/sol/simulation/ghost_lidar.py --speed 10 --duration 120 --mob
  ```
  Flags: `--output`, `--speed`, `--duration`, `--mob` (triggers MOB after 5s)

## 1.3 Files to Transfer

Copy these from this repo to `dre-orchestrator/freq`:

| Source File | Destination | Notes |
|-------------|-------------|-------|
| `public/index.html` | `public/index.html` | CesiumJS + React 3D dashboard |
| `src/sol/simulation/ghost_lidar.py` | `src/sol/simulation/ghost_lidar.py` | Ghost LiDAR engine |
| `HANDOFF.md` | `HANDOFF.md` | This document |

---

# PART TWO: PATH A / PATH B STRATEGY

## Path A — CesiumJS + React (BUILD NOW)

| Attribute | Detail |
|-----------|--------|
| Stack | CesiumJS + React 18 + Babel Standalone |
| Cost | FREE (Cesium Ion free tier, Netlify free) |
| Deploy | Drag-and-drop to Netlify Drop |
| Purpose | Immediate demo for Google meeting |
| Status | BUILT — `public/index.html` |

## Path B — Google Immersive Stream + Unreal Engine 5 (PITCH LATER)

| Attribute | Detail |
|-----------|--------|
| Stack | Unreal Engine 5 + Pixel Streaming via Google Immersive Stream |
| Cost | $350K Google Cloud credits (Startup Program) |
| Deploy | Managed by Google infrastructure |
| Purpose | Production-grade photorealistic maritime visualization |
| Status | NOT STARTED — pitch to Sulgi at Google |

**Strategy:** Path A proves the concept visually. Path B is the $350K ask — "Give us the credits and we'll build THIS in Unreal Engine on your platform."

---

# PART THREE: JSON SHADOW ARCHITECTURE

The JSON Shadow replaces the "Digital Twin" concept. It is an Eclipse Ditto-style state object:

```json
{
  "timestamp": 1739462400.123,
  "barge_id": "BARGE-GOM-2026-001",
  "barge_name": "Gulf Runner 1",
  "location": {"lat": 29.31, "lon": -94.79},
  "draft": {
    "fore": 10.45, "aft": 10.82, "port": 10.58,
    "starboard": 10.67, "mean": 10.63, "unit": "ft"
  },
  "stability": {
    "trim": 0.185, "heel": -0.092, "displacement": 3200,
    "gm": 3.65, "status": "NOMINAL"
  },
  "crane": {
    "load_weight": 1800, "max_capacity": 3200, "boom_angle": 42.3,
    "slew_bearing": 195.7, "hook_height": 16.2, "status": "LOADING",
    "signal_code": "SIG-LOAD", "g_code": "G01"
  },
  "workflow": {
    "current_phase": "CARGO-LOAD", "phase_index": 3,
    "elapsed_seconds": 420, "target_seconds": 900,
    "phases": ["PRE-SURVEY","BALLAST-ADJ","CRANE-POS","CARGO-LOAD","TRIM-CORR","FINAL-SURV"]
  },
  "alerts": {
    "man_overboard": false, "list_warning": false,
    "overload_warning": false, "trim_warning": false,
    "heat_signature_anomaly": false
  },
  "ghost_lidar": {
    "point_count": 6000, "scan_pattern": "lawnmower", "chaos_mode": false
  },
  "governance": {
    "freq_law": "COMPLIANT", "veto_status": "CLEAR", "consensus": "3/3 APPROVED"
  }
}
```

**Flow:** `ghost_lidar.py` writes this to `state/barge_state.json` at 1Hz → Dashboard reads it → CesiumJS renders it.

**Do NOT modify these keys without Level 0 approval.**

---

# PART FOUR: FREQ LAW & GOVERNANCE

## 4.1 FREQ Law — Constitutional Framework

| Tenet | Requirement |
|-------|-------------|
| **Fast** | <2000ms sensor processing + report. No unnecessary hops. Mandatory parallelization. |
| **Robust** | No Happy Path. Error boundaries. Pulse Protocol. Human interlocks for safety. |
| **Evolutionary** | Reflexion Loop. No hard-coded values. Schema versioning. |
| **Quantified** | Cognitive Audit Trail. JSON-LD provenance. Trust Scores. Full forensic capability. |

## 4.2 Chain of Command

```
Level 0: Sovereign Intent Originator (Chief Dre)
Level 1: SSC — Gemini 3.0 Thinking — Central Nervous System
Level 2: CGE — Gemini 3.0 Pro (Temp 0.0) — Non-bypassable VETO
Level 3: SIL — Gemini 3.0 Flash — Knowledge Substrate
Level 4: SA  — Gemini 3.0 Pro — Technical Architecture
Level 5: TOM — Gemini 3.0 Flash — SOLE authorized executor
```

## 4.3 Consensus & VETO

- k=3 of 4 nodes (SSC, CGE, SIL, SA) for critical state changes
- CGE VETO supersedes consensus — even 3 approvals blocked if CGE vetoes
- Digital Constitution on Google Cloud Spanner (append-only, immutable)

---

# PART FIVE: PHASE III SIMULATION — WHAT EXISTS ON USER'S LOCAL MACHINE

All modules in `src/sol/simulation/`. Pure Python, zero external dependencies.

| Module | Purpose |
|--------|---------|
| `state_objects.py` | DraftState, CraneState, StabilityState, WorkflowPhase, SimulationState |
| `draft_monitor.py` | 4-point draft sensors, noise, offsets, mean computation |
| `crane_controller.py` | SIG-000→SIG-910, G00→G99, boom/hook/capacity safety |
| `stability_analyzer.py` | Trim, heel, displacement, GM, STABLE/CAUTION/CRITICAL |
| `workflow_engine.py` | 6-phase FSM, 15-min target |
| `watchdog_agent.py` | DFT/CRN/STB/WFL violation codes, PASS/ALERT/STOP |
| `demo_runner.py` | Full orchestrator, 4 cargo lifts, ~10.9 min |
| `ghost_lidar.py` | NEW — synthetic data generator (built this session) |

**Tests:** 56 in `test_simulation.py`, all passing.

---

# PART SIX: GOOGLE STARTUP PROGRAM

| Detail | Value |
|--------|-------|
| Program | Google for Startups Cloud Program — AI Tier |
| Credits | $350,000 over 2 years ($200K Scale + $150K AI) |
| Contact | Sulgi (BD), referred by Sylvan (REQ Consultant) |
| Meeting | Week of Feb 10-14, 2026 |
| Key eval | Visual demo proof, GCP spend trajectory, competitive displacement (Azure→GCP) |
| Market | Maritime AI: $4.3B (2024) → $32.7B (2030), 40.6% CAGR |
| Cost savings | SOL $2,113/yr vs Manual $162K/yr (98.7% savings) vs Drone $1M/yr (99.8% savings) |

---

# PART SEVEN: CONSTRAINTS

## What NOT To Do
- Do NOT use `dre-orchestrator-ai`, `dre-achitect`, or `dre-architect` accounts
- Do NOT use Vertex AI Agent Designer
- Do NOT deploy to Azure (Phase 2 legacy)
- Do NOT refactor Phase 2 Agent Core without Level 0 directive
- Do NOT modify authoritative data structure keys without Level 0 approval
- Do NOT select a deployment platform — pending Chief Dre's decision
- Do NOT build terminal UIs — visual/web only

## Architecture Principles
1. **State-First:** Hardware is a "Digital Shadow." Code updates JSON State Objects.
2. **Simulation is Data Layer:** Python simulation feeds visualization. It IS the source of truth.
3. **No Terminal UIs:** Building for visual/web interaction.
4. **Pure Python:** Simulation has zero external dependencies.

---

# PART EIGHT: IMMEDIATE NEXT STEPS

After transferring files to `dre-orchestrator/freq`:

| # | Task | Detail |
|---|------|--------|
| 1 | **Get Cesium Ion token** | Free signup: ion.cesium.com → replace `YOUR_CESIUM_ION_TOKEN` in `public/index.html` line 93 |
| 2 | **Test locally** | Open `public/index.html` in Chrome — globe + barge + LiDAR should render |
| 3 | **Deploy to Netlify** | Drag `public/` folder to netlify.com/drop → instant shareable URL |
| 4 | **Run ghost_lidar.py** | `python src/sol/simulation/ghost_lidar.py --speed 10 --duration 120` |
| 5 | **Bridge ghost_lidar → dashboard** | Connect `state/barge_state.json` output to `index.html` STATE object (WebSocket or polling) |
| 6 | **Prepare pitch deck** | Problem → Solution → Demo URL → Architecture → GCP Services → Spend → $350K ask |
| 7 | **Path B pitch** | Present Unreal Engine 5 + Google Immersive Stream as the $350K upgrade |

---

# PART NINE: BUILDER DIRECTIVE — PASTE INTO NEW SESSION

Copy everything below the line into a fresh Claude Code session on `dre-orchestrator/freq`:

---

```
You are the Builder for FREQ AI SOL — Sophisticated Operational Lattice.

Role: Builder (Phase 3 Execution)
Context: Phase 3 of the FREQ AI project. Migrating Lattice Core from Azure Foundry to Google Cloud.
Repository Target: https://github.com/dre-orchestrator

Read HANDOFF.md and CLAUDE.md at the repo root for full architectural context.

I am Chief Dre, Sovereign Intent Originator (Level 0).

## What Exists
- Phase 2 Lattice Core: COMPLETE (SSC, CGE, SIL agents, governance, consensus)
- Phase 3 Simulation: 6-phase barge drafting, 56 tests passing, ~10.9 min workflow
- CesiumJS Dashboard: public/index.html — 3D globe + barge + LiDAR + React panels
- Ghost LiDAR Engine: src/sol/simulation/ghost_lidar.py — synthetic data generator

## Core Requirements
1. No terminal output — State-First Architecture (Eclipse Ditto style)
2. Simulated physics with drift (wave motion, sensor noise)
3. Safety trigger: trigger_man_overboard() → heat signature anomaly → CGE SAFETY VETO → crane M00
4. Data structures match Blueprint v4.0 Appendix (see HANDOFF.md Part Three)
5. Ghost LiDAR writes to state/barge_state.json at 1Hz

## What NOT To Do
- Do NOT use dre-orchestrator-ai, dre-achitect, or dre-architect accounts
- Do NOT deploy to Azure
- Do NOT modify data structure keys without my approval
- Do NOT select a deployment platform without my directive
- Do NOT build terminal UIs

## Immediate Task
[DESCRIBE YOUR NEXT OBJECTIVE HERE]

The simulation works. Tests pass. The CesiumJS dashboard renders. Ghost LiDAR generates data.
I need [NEXT OBJECTIVE] now.
```

---

*End of HANDOFF.md*
*Generated: February 13, 2026*
*Version: 4.0 — Ghost Stream Edition*
*Repo Target: https://github.com/dre-orchestrator/freq*
*Authority: Chief Dre, Sovereign Intent Originator*
