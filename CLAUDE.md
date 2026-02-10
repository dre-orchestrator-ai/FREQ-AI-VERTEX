# FREQ-AI-VERTEX — SOL Lattice

> **Codename:** Antigravity
> **Authority:** Chief Dre — Sovereign Intent Originator (Level 0)
> **Status:** Phase 3 — Deployment & Demo Preparation

## System Identity

Sophisticated Operational Lattice (SOL): a multi-node AI orchestration system for autonomous maritime barge drafting operations, deployed on Google Cloud Vertex AI Agent Builder with Gemini substrates.

## Quick Commands

```bash
# Run all tests (68 expected)
PYTHONPATH=src python -m pytest tests/ -v

# Run demo simulation
PYTHONPATH=src python -m sol.simulation.demo_runner

# Run specific test suites
PYTHONPATH=src python -m pytest tests/test_sol.py -v        # 37 core tests
PYTHONPATH=src python -m pytest tests/test_maritime.py -v   # 31 maritime tests
```

## Architecture

### Lattice Nodes (8 types)
- **Strategic OP** — Mission-level coordination
- **SPCI** — Continuous improvement cycles
- **Legacy Architect** — Legacy system translation
- **GOV Engine** — FREQ LAW compliance, VETO authority (Priority 0)
- **Exec Automate** — Workflow execution
- **Optimal Intel** — Analytics and decision support
- **Element Design** — Schema and artifact generation
- **Maritime Barge Ops** — Draft survey, ballast optimization, stability analysis

### Agent Hierarchy (Vertex AI)
```
Level 0: Chief Dre ─── Sovereign Intent Originator (Human)
Level 1: SSC ───────── Strategic Synthesis Core (Gemini 3 Pro)
Level 2: CGE ───────── Cognitive Governance Engine (Gemini 3 Pro)
Level 3: SIL ───────── Specialization Intelligence Lead (Gemini 3 Flash)
Level 4: SA ────────── Specialization Agent (Gemini 3 Flash)
Level 5: TOM ───────── Tactical Optimization Module (Gemini 3 Flash)
```

### Governance: FREQ LAW
- **Fast:** All operations < 2000ms
- **Robust:** k=3 quorum consensus (BFT)
- **Evolutionary:** SPCI continuous improvement
- **Quantified:** BigQuery audit trail, 0.95 trust threshold

## Key Files

| File | Purpose |
|------|---------|
| `src/sol/nodes/base.py` | LatticeNode base class, NodeMessage, NodeResponse |
| `src/sol/nodes/maritime_ops.py` | Maritime barge operations (633 lines) |
| `src/sol/simulation/maritime_barge.py` | Simulation orchestrator |
| `src/sol/simulation/demo_runner.py` | Presentation-ready terminal demo |
| `src/sol/governance/freq_law.py` | FREQ LAW enforcement |
| `src/sol/governance/veto.py` | VETO authority |
| `src/sol/consensus/quorum.py` | k=3 quorum consensus |
| `src/sol/blueprint/freq_blueprint.py` | Mission vectors, deployment phases |
| `config/vertex_ai_agent.yaml` | Vertex AI Agent Builder config |
| `config/sol_config.yaml` | Node configuration |
| `public/index.html` | Dashboard (deploy to Firebase/Netlify) |
| `AGENT_PROTOCOL.md` | Agent hierarchy and communication protocol |

## Branch Rules
- Push only to `claude/` prefixed branches
- PR merge via GitHub web UI (proxy blocks direct main push)
- Fork: `dre-achitect/freq-ai-vertex`

## Meeting Context
- **Who:** Sulgi, Google Cloud Business Development
- **Ask:** $350,000 GCP credits (Google for Startups AI Tier)
- **Demo:** Cloud Shell (Python sim) LEFT + Firebase URL (dashboard) RIGHT
- **Key metric:** $2,113/yr SOL vs $162,000/yr manual (98.7% savings)
