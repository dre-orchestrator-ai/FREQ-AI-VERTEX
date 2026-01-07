# FREQ-AI-VERTEX

**Sophisticated Operational Lattice (SOL)** - Multi-node AI orchestration system for legacy modernization across regulated industries. Built on Gemini substrates with FREQ LAW governance, FSM state management, and sub-2000ms response protocols.

## 🚀 Overview

FREQ AI Sophisticated Operational Lattice is a natural language orchestration system running on Google Cloud Vertex AI. It eliminates traditional coding requirements by enabling verbal orchestration through 7 specialized Gemini nodes working in concert.

### Key Features

- **🎯 7 Gemini Nodes**: Specialized AI agents for comprehensive analysis
  - Strategic Operations
  - Supply Chain Intelligence (SPCI)
  - Legacy Architect
  - Governance Engine
  - Executive Automation
  - Optimal Intelligence
  - Element Design

- **🔄 FSM State Control**: Rigorous state machine management
  - `IDLE → DIRECTIVE → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE/VETO`

- **⚖️ FREQ LAW Compliance**:
  - Response time < 2000ms
  - k=3 consensus requirement
  - BigQuery audit trails

- **🏭 5 Vertical Domains**:
  - Maritime
  - Agriculture
  - Manufacturing
  - Healthcare
  - Construction

- **🗣️ Natural Language Interface**: No traditional coding required

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Natural Language Input                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   SOL Orchestrator                           │
│  ┌────────────────────────────────────────────────────┐     │
│  │              FSM State Controller                  │     │
│  │  IDLE→DIRECTIVE→VALIDATION→QUORUM→EXECUTION→      │     │
│  │         AUDIT→COMPLETE/VETO                        │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  7 Gemini Nodes (Parallel Processing)        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │  Strategic   │ │    SPCI      │ │   Legacy     │        │
│  │ Operations   │ │              │ │  Architect   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Governance   │ │  Executive   │ │   Optimal    │        │
│  │   Engine     │ │ Automation   │ │ Intelligence │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ┌──────────────┐                                            │
│  │   Element    │                                            │
│  │   Design     │                                            │
│  └──────────────┘                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    FREQ LAW Enforcer                         │
│  • <2000ms Response Time                                     │
│  • k=3 Consensus Voting                                      │
│  • BigQuery Audit Trail                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Execution & Results                         │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Google Cloud Project with Vertex AI enabled
- BigQuery dataset for audit logs (optional)

### Setup

```bash
# Clone the repository
git clone https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX.git
cd FREQ-AI-VERTEX

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

1. Set up Google Cloud credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
```

2. Configure `config.yaml` with your settings (optional)

## 🎯 Usage

### Command Line Interface

```bash
# Basic usage
python -m freq_ai.cli "Optimize shipping routes for next quarter"

# With vertical domain
python -m freq_ai.cli "Schedule preventive maintenance" --vertical maritime

# With GCP project
python -m freq_ai.cli "Analyze crop yields" --vertical agriculture --project my-gcp-project

# Verbose output
python -m freq_ai.cli "Design warehouse layout" --vertical manufacturing --verbose

# JSON output
python -m freq_ai.cli "Create compliance checklist" --json
```

### Python API

```python
import asyncio
from freq_ai import SOLOrchestrator

async def main():
    # Initialize orchestrator
    orchestrator = SOLOrchestrator(
        project_id="your-gcp-project",
        max_response_time_ms=2000,
        consensus_k=3
    )
    
    # Execute directive
    result = await orchestrator.orchestrate(
        directive="Optimize supply chain for Q2 2026",
        vertical="manufacturing"
    )
    
    # Check results
    if result.success:
        print(f"✅ Success! Elapsed: {result.elapsed_time_ms}ms")
        print(f"Consensus: {result.consensus_result['positive_votes']}/7")
    else:
        print(f"❌ Failed: {result.error}")

asyncio.run(main())
```

## 📚 Examples

### Example 1: Maritime Operations

```bash
python -m freq_ai.cli "Plan vessel routing from Shanghai to LA for next quarter considering fuel costs and weather patterns" --vertical maritime
```

### Example 2: Healthcare Compliance

```bash
python -m freq_ai.cli "Design HIPAA-compliant patient data migration strategy from legacy EHR system" --vertical healthcare
```

### Example 3: Manufacturing Optimization

```bash
python -m freq_ai.cli "Implement predictive maintenance program for assembly line robots" --vertical manufacturing
```

### Example 4: Agricultural Planning

```bash
python -m freq_ai.cli "Create harvest schedule based on weather forecasts and market demand" --vertical agriculture
```

### Example 5: Construction Safety

```bash
python -m freq_ai.cli "Generate comprehensive safety protocol for high-rise construction project" --vertical construction
```

See `examples/usage_examples.py` for more detailed examples.

## 🏗️ Project Structure

```
FREQ-AI-VERTEX/
├── src/
│   └── freq_ai/
│       ├── __init__.py
│       ├── cli.py                    # Command-line interface
│       ├── core/
│       │   ├── fsm.py               # FSM state management
│       │   └── freq_law.py          # FREQ LAW enforcement
│       ├── nodes/
│       │   ├── base_node.py         # Base node class
│       │   └── gemini_nodes.py      # 7 specialized nodes
│       ├── orchestration/
│       │   └── orchestrator.py      # Main orchestrator
│       └── verticals/
│           └── vertical_context.py   # Vertical domain support
├── examples/
│   └── usage_examples.py            # Usage examples
├── config.yaml                       # Configuration
├── requirements.txt                  # Dependencies
├── setup.py                         # Package setup
└── README.md                        # This file
```

## 🔧 Configuration

Edit `config.yaml` to customize:

- GCP project and location
- Vertex AI model settings
- FREQ LAW parameters
- FSM timeout settings
- Node configuration
- Vertical domain settings
- Logging configuration

## 🎭 The 7 Nodes

### 1. Strategic Operations
High-level strategic planning and decision coordination. Analyzes business objectives, resource allocation, and strategic alignment.

### 2. Supply Chain Intelligence (SPCI)
Supply chain optimization and logistics intelligence. Handles inventory, procurement, transportation, and demand forecasting.

### 3. Legacy Architect
Legacy system modernization and architecture. Provides technical guidance on system integration and migration strategies.

### 4. Governance Engine
Compliance, regulatory, and governance oversight. Ensures adherence to regulations, standards, and ethical practices.

### 5. Executive Automation
Automated execution of approved directives. Manages workflow execution, error handling, and monitoring.

### 6. Optimal Intelligence
Data analytics and optimization recommendations. Provides insights through predictive modeling and performance analysis.

### 7. Element Design
System and component design engineering. Handles design patterns, modularity, and engineering specifications.

## 📊 FSM State Flow

1. **IDLE**: System waiting for directive
2. **DIRECTIVE**: Directive received and parsed
3. **VALIDATION**: All 7 nodes analyze directive in parallel
4. **QUORUM**: Achieve k=3 consensus from node votes
5. **EXECUTION**: Execute approved directive
6. **AUDIT**: Audit execution and log to BigQuery
7. **COMPLETE**: Successful completion (or **VETO** if consensus fails)

## ⚖️ FREQ LAW Compliance

The system enforces three core principles:

1. **Response Time < 2000ms**: All operations must complete within 2 seconds
2. **k=3 Consensus**: At least 3 nodes must approve for execution
3. **BigQuery Audit**: All events logged for compliance and auditing

## 🏭 Vertical Domains

Each vertical has specialized context and regulatory considerations:

- **Maritime**: Vessel operations, port logistics, shipping regulations (IMO, SOLAS)
- **Agriculture**: Crop management, supply chain, food safety (FDA, USDA, GAP)
- **Manufacturing**: Production optimization, quality control, worker safety (ISO 9001, OSHA)
- **Healthcare**: Patient data, clinical workflows, compliance (HIPAA, FDA, HITECH)
- **Construction**: Project management, safety protocols, permits (OSHA, building codes)

## 🧪 Testing

```bash
# Run examples
python examples/usage_examples.py

# Test with mock data (no GCP credentials required)
python -m freq_ai.cli "Test directive" --verbose
```

## 📝 License

Copyright © 2026 DRE Orchestrator AI

## 🤝 Contributing

Contributions welcome! Please submit pull requests or open issues.

## 📞 Support

For support and questions, please open an issue on GitHub.

---

**FREQ AI VERTEX** - Natural language orchestration for the modern enterprise. No traditional coding required.
