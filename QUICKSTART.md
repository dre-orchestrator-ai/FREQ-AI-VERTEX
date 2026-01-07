# FREQ AI SOL - Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/dre-orchestrator-ai/FREQ-AI-VERTEX.git
cd FREQ-AI-VERTEX

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## 5-Minute Quick Start

### 1. Basic Command Line Usage

```bash
# Simple directive
python -m freq_ai.cli "Optimize operations for next quarter"

# With vertical domain
python -m freq_ai.cli "Plan vessel routes" --vertical maritime

# Verbose output with all node responses
python -m freq_ai.cli "Design safety system" --vertical construction --verbose
```

### 2. Python API Usage

```python
import asyncio
from freq_ai import SOLOrchestrator

async def main():
    # Initialize
    orchestrator = SOLOrchestrator()
    
    # Execute directive
    result = await orchestrator.orchestrate(
        directive="Optimize supply chain operations",
        vertical="manufacturing"
    )
    
    # Check results
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    print(f"Consensus: {result.consensus_result['positive_votes']}/7")

asyncio.run(main())
```

### 3. Run Examples

```bash
# Run all examples
python examples/usage_examples.py

# Run tests
python tests/test_api.py
```

## Understanding the Output

### CLI Output Explanation

```
📡 Initializing SOL Orchestrator...
   ↓ System initializes 7 Gemini nodes

📝 Processing Directive:
   ↓ Your natural language input

⚙️  Orchestrating through FSM states...
   ↓ State machine progresses through:
      IDLE → DIRECTIVE → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE

📊 Results:
   ✅ ORCHESTRATION SUCCESSFUL
   - Session ID: Unique identifier for this orchestration
   - Final State: COMPLETE (or VETO if consensus failed)
   - Elapsed Time: < 2000ms (FREQ LAW compliance)
   - FREQ LAW Compliance: ✅ YES

🗳️  Consensus (k=3):
   - Positive Votes: X/7 nodes approved
   - Status: ✅ PASSED (needs at least 3 votes)
   - Individual node votes listed

📡 Node Responses: (in verbose mode)
   - Each of the 7 nodes' analysis
   - Vote: APPROVED or REJECTED
```

## Key Concepts

### The 7 Nodes

1. **Strategic Operations** - Business strategy and planning
2. **SPCI** - Supply chain optimization
3. **Legacy Architect** - System modernization
4. **Governance Engine** - Compliance and regulations
5. **Executive Automation** - Workflow execution
6. **Optimal Intelligence** - Data analytics
7. **Element Design** - System design

### FSM States

```
IDLE: Waiting for directive
  ↓
DIRECTIVE: Received and parsed
  ↓
VALIDATION: All 7 nodes analyze in parallel
  ↓
QUORUM: Check k=3 consensus
  ↓
EXECUTION: Execute if approved
  ↓
AUDIT: Log to audit trail
  ↓
COMPLETE: Success!
```

### FREQ LAW

Three core requirements:
- **< 2000ms**: All operations complete in under 2 seconds
- **k=3**: Minimum 3 nodes must approve (consensus)
- **Audit**: All events logged to BigQuery

### Verticals

Specialized domain contexts:
- **maritime**: Shipping, ports, logistics
- **agriculture**: Farming, crops, supply chain
- **manufacturing**: Production, quality control
- **healthcare**: Patient care, compliance
- **construction**: Projects, safety, permits

## Common Use Cases

### Maritime
```bash
python -m freq_ai.cli "Optimize shipping routes for fuel efficiency" --vertical maritime
python -m freq_ai.cli "Plan port operations for peak season" --vertical maritime
```

### Agriculture
```bash
python -m freq_ai.cli "Schedule harvest based on weather forecast" --vertical agriculture
python -m freq_ai.cli "Optimize crop rotation strategy" --vertical agriculture
```

### Manufacturing
```bash
python -m freq_ai.cli "Implement predictive maintenance program" --vertical manufacturing
python -m freq_ai.cli "Design quality control automation" --vertical manufacturing
```

### Healthcare
```bash
python -m freq_ai.cli "Create HIPAA-compliant data migration plan" --vertical healthcare
python -m freq_ai.cli "Optimize patient scheduling system" --vertical healthcare
```

### Construction
```bash
python -m freq_ai.cli "Design safety protocol for high-rise project" --vertical construction
python -m freq_ai.cli "Create resource allocation plan" --vertical construction
```

## Configuration

### Basic Configuration (No GCP)

Works out of the box with mock responses:
```bash
python -m freq_ai.cli "Test directive"
```

### With Google Cloud (Full Features)

1. Set up credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export GCP_PROJECT_ID="your-project-id"
```

2. Use with project:
```bash
python -m freq_ai.cli "Your directive" --project your-project-id
```

### Custom Configuration

Edit `config.yaml` to customize:
- Response time limits
- Consensus requirements
- BigQuery settings
- Node configurations

## Troubleshooting

### "No module named freq_ai"
```bash
pip install -e .
```

### Timeout errors
- Check FREQ LAW settings in config.yaml
- Increase timeout for complex operations

### All nodes voting reject
- Refine your directive
- Check vertical domain match
- Use --verbose to see node reasoning

## Next Steps

1. **Read the full README.md** for comprehensive documentation
2. **Check ARCHITECTURE.md** for technical details
3. **Explore examples/** for more use cases
4. **Run tests/** to verify your setup

## Support

- Issues: GitHub Issues
- Documentation: README.md, ARCHITECTURE.md
- Examples: examples/ directory

---

**FREQ AI VERTEX** - Natural language orchestration for the modern enterprise.
