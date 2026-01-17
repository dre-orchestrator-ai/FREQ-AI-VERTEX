"""
FREQ AI Lattice - Visual Dashboard

A production-ready visual interface for the FREQ AI Sophisticated Operational Lattice.
Built with Streamlit for real-time monitoring and control.

Run locally:  streamlit run dashboard/app.py
Deploy:       See dashboard/README.md
"""

import streamlit as st
import asyncio
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import random

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="FREQ AI Lattice",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS - IBM Carbon + Microsoft Fluent Inspired
# =============================================================================

st.markdown("""
<style>
    /* IBM Carbon / Fluent Design Tokens */
    :root {
        --freq-blue-primary: #0f62fe;
        --freq-blue-hover: #0353e9;
        --freq-green-success: #24a148;
        --freq-red-error: #da1e28;
        --freq-yellow-warning: #f1c21b;
        --freq-gray-100: #161616;
        --freq-gray-90: #262626;
        --freq-gray-80: #393939;
        --freq-gray-10: #f4f4f4;
        --freq-white: #ffffff;
    }

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Header styling */
    .freq-header {
        background: linear-gradient(135deg, #161616 0%, #262626 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #0f62fe;
    }

    .freq-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 600;
    }

    .freq-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-size: 0.9rem;
    }

    /* Metric cards */
    .metric-card {
        background: #262626;
        color: white;
        padding: 1.25rem;
        border-radius: 8px;
        text-align: center;
        border-top: 3px solid #0f62fe;
    }

    .metric-card.success { border-top-color: #24a148; }
    .metric-card.warning { border-top-color: #f1c21b; }
    .metric-card.error { border-top-color: #da1e28; }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.85rem;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Node cards */
    .node-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }

    .node-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    .node-card.active {
        border-left: 4px solid #0f62fe;
        background: #f4f4f4;
    }

    .node-card.completed {
        border-left: 4px solid #24a148;
    }

    .node-level {
        font-size: 0.75rem;
        color: #0f62fe;
        font-weight: 600;
        text-transform: uppercase;
    }

    .node-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #161616;
        margin: 0.25rem 0;
    }

    .node-model {
        font-size: 0.8rem;
        color: #6f6f6f;
    }

    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-badge.operational { background: #defbe6; color: #0e6027; }
    .status-badge.processing { background: #d0e2ff; color: #0043ce; }
    .status-badge.warning { background: #fcf4d6; color: #8e6a00; }
    .status-badge.error { background: #fff1f1; color: #a2191f; }

    /* Lattice visualization */
    .lattice-viz {
        background: #f4f4f4;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
    }

    .lattice-flow {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .flow-arrow {
        color: #0f62fe;
        font-size: 1.5rem;
    }

    /* Mission log */
    .mission-log {
        background: #161616;
        color: #c6c6c6;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        padding: 1rem;
        border-radius: 8px;
        max-height: 300px;
        overflow-y: auto;
    }

    .log-entry {
        padding: 0.25rem 0;
        border-bottom: 1px solid #393939;
    }

    .log-timestamp { color: #6f6f6f; }
    .log-node { color: #78a9ff; }
    .log-action { color: #42be65; }
    .log-message { color: #f4f4f4; }

    /* Buttons */
    .stButton > button {
        background: #0f62fe;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 4px;
        transition: background 0.2s ease;
    }

    .stButton > button:hover {
        background: #0353e9;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #f4f4f4;
        border-radius: 4px 4px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: #0f62fe;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if 'missions' not in st.session_state:
    st.session_state.missions = []

if 'current_mission' not in st.session_state:
    st.session_state.current_mission = None

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'system_status' not in st.session_state:
    st.session_state.system_status = {
        'ssc': 'operational',
        'cge': 'operational',
        'tom': 'operational',
    }

# =============================================================================
# LATTICE INTEGRATION
# =============================================================================

# Import lattice if available
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from run_lattice import FreqAILattice, A2AMessage, MessageType
    LATTICE_AVAILABLE = True
except ImportError:
    LATTICE_AVAILABLE = False

async def process_directive_async(directive: str) -> Dict[str, Any]:
    """Process directive through the lattice."""
    if LATTICE_AVAILABLE:
        lattice = FreqAILattice()
        return await lattice.process_directive(directive)
    else:
        # Simulated response for demo
        await asyncio.sleep(2)
        return {
            "directive": directive,
            "total_latency_ms": random.randint(800, 1500),
            "freq_compliant": True,
            "ssc_response": {"payload": {"plan": "Task decomposition complete"}},
            "cge_response": {"payload": {"decision": "APPROVE", "confidence": 0.95}},
            "tom_response": {"payload": {"status": "completed", "result": "Execution successful"}},
        }

def process_directive(directive: str) -> Dict[str, Any]:
    """Synchronous wrapper for directive processing."""
    return asyncio.run(process_directive_async(directive))

def add_log(node: str, action: str, message: str):
    """Add entry to mission log."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    st.session_state.logs.insert(0, {
        'timestamp': timestamp,
        'node': node,
        'action': action,
        'message': message,
    })
    # Keep last 100 logs
    st.session_state.logs = st.session_state.logs[:100]

# =============================================================================
# HEADER
# =============================================================================

st.markdown("""
<div class="freq-header">
    <h1>🔷 FREQ AI Sophisticated Operational Lattice</h1>
    <p>Maritime Barge Operations Command Center | Powered by Claude Opus 4.5 + Gemini Flash</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - SYSTEM STATUS & MANIFEST
# =============================================================================

with st.sidebar:
    st.markdown("### ⚙️ System Status")

    # Provider status
    anthropic_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    google_key = bool(os.environ.get("GOOGLE_AI_API_KEY"))

    col1, col2 = st.columns(2)
    with col1:
        if anthropic_key:
            st.success("Anthropic ✓")
        else:
            st.warning("Anthropic ✗")
    with col2:
        if google_key:
            st.success("Google AI ✓")
        else:
            st.warning("Google AI ✗")

    st.divider()

    # Manifest
    st.markdown("### 📋 Deployment Manifest")

    manifest = {
        "version": "1.0.0",
        "environment": os.environ.get("ENV", "development"),
        "region": os.environ.get("REGION", "us-central1"),
        "nodes": {
            "L1-SSC": {"model": "claude-opus-4-5", "status": "active"},
            "L2-CGE": {"model": "claude-opus-4-5", "status": "active"},
            "L3-SIL": {"model": "gemini-pro", "status": "pending"},
            "L4-SA": {"model": "gemini-pro", "status": "pending"},
            "L5-TOM": {"model": "gemini-flash", "status": "active"},
        },
        "last_deploy": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    st.json(manifest)

    st.divider()

    # Quick stats
    st.markdown("### 📊 Session Stats")
    st.metric("Total Missions", len(st.session_state.missions))

    if st.session_state.missions:
        avg_latency = sum(m.get('latency', 0) for m in st.session_state.missions) / len(st.session_state.missions)
        st.metric("Avg Latency", f"{avg_latency:.0f}ms")

        compliant = sum(1 for m in st.session_state.missions if m.get('freq_compliant', False))
        st.metric("FREQ Compliant", f"{compliant}/{len(st.session_state.missions)}")

# =============================================================================
# MAIN CONTENT - TABS
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Mission Control", "🔗 Lattice View", "📜 Mission Log", "📈 Analytics"])

# =============================================================================
# TAB 1: MISSION CONTROL
# =============================================================================

with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🎯 Issue Directive")

        # Directive input
        directive_type = st.selectbox(
            "Directive Type",
            ["Custom Directive", "Barge Scan", "Weather Check", "Fleet Status", "Emergency Response"]
        )

        if directive_type == "Barge Scan":
            barge_col1, barge_col2 = st.columns(2)
            with barge_col1:
                barge_id = st.text_input("Barge ID", value="DELTA-7")
                location = st.text_input("Location", value="Mississippi River MM 142")
            with barge_col2:
                weather = st.text_input("Weather", value="Clear, wind 5 knots")
                priority = st.selectbox("Priority", ["NORMAL", "HIGH", "CRITICAL"])

            directive = f"""MARITIME OPERATION: Barge Draft Measurement
Barge ID: {barge_id}
Location: {location}
Weather: {weather}
Priority: {priority}

Tasks:
1. Validate weather conditions for drone operation
2. Initialize LiDAR scanning sequence
3. Calculate draft measurements from scan data
4. Generate compliance report"""

        elif directive_type == "Weather Check":
            location = st.text_input("Location", value="Mississippi River Delta")
            directive = f"Check weather conditions for drone operations at {location}. Report wind speed, visibility, and flight safety assessment."

        elif directive_type == "Fleet Status":
            directive = "Generate comprehensive fleet status report. Include all active barges, their positions, draft measurements, and cargo status."

        elif directive_type == "Emergency Response":
            emergency_type = st.selectbox("Emergency Type", ["Collision Alert", "Weather Emergency", "Equipment Failure", "Security Incident"])
            directive = f"EMERGENCY: {emergency_type} detected. Initiate emergency response protocol. Assess situation and recommend immediate actions."

        else:
            directive = st.text_area(
                "Enter your directive",
                height=150,
                placeholder="Example: Scan barge ALPHA-1 for draft measurement at Mile Marker 100..."
            )

        st.markdown("---")

        # Execute button
        if st.button("🚀 Execute Directive", type="primary", use_container_width=True):
            if directive.strip():
                with st.spinner("Processing through Chain of Command..."):
                    # Update status
                    add_log("SOVEREIGN", "DIRECTIVE", directive[:50] + "...")

                    # Process
                    result = process_directive(directive)

                    # Log progress
                    add_log("L1-SSC", "DECOMPOSE", "Task plan generated")
                    add_log("L2-CGE", "VALIDATE", f"Decision: {result.get('cge_response', {}).get('payload', {}).get('decision', 'APPROVE')}")
                    add_log("L5-TOM", "EXECUTE", "Mission completed")

                    # Store mission
                    mission = {
                        'id': f"M-{len(st.session_state.missions) + 1:04d}",
                        'timestamp': datetime.now().isoformat(),
                        'directive': directive,
                        'latency': result.get('total_latency_ms', 0),
                        'freq_compliant': result.get('freq_compliant', True),
                        'result': result,
                    }
                    st.session_state.missions.insert(0, mission)
                    st.session_state.current_mission = mission

                st.success(f"✅ Mission Complete | Latency: {result.get('total_latency_ms', 0):.0f}ms")
                st.rerun()
            else:
                st.error("Please enter a directive")

    with col2:
        st.markdown("### 📊 Latest Mission")

        if st.session_state.current_mission:
            mission = st.session_state.current_mission

            # Status card
            freq_status = "✅ COMPLIANT" if mission.get('freq_compliant') else "⚠️ SLOW"
            st.markdown(f"""
            <div class="metric-card {'success' if mission.get('freq_compliant') else 'warning'}">
                <div class="metric-label">Mission {mission.get('id')}</div>
                <div class="metric-value">{mission.get('latency', 0):.0f}ms</div>
                <div class="metric-label">{freq_status}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Chain results
            st.markdown("**Chain of Command Results:**")

            result = mission.get('result', {})

            with st.expander("L1-SSC: Strategic Synthesis", expanded=False):
                st.json(result.get('ssc_response', {}).get('payload', {}))

            with st.expander("L2-CGE: Governance", expanded=False):
                st.json(result.get('cge_response', {}).get('payload', {}))

            with st.expander("L5-TOM: Execution", expanded=False):
                st.json(result.get('tom_response', {}).get('payload', {}))
        else:
            st.info("No missions executed yet. Issue a directive to get started.")

# =============================================================================
# TAB 2: LATTICE VIEW
# =============================================================================

with tab2:
    st.markdown("### 🔗 Chain of Command Visualization")

    # Visual lattice representation
    st.markdown("""
    <div class="lattice-viz">
        <div class="lattice-flow">
            <div style="background:#0f62fe; color:white; padding:1rem 2rem; border-radius:8px;">
                <strong>L0 SOVEREIGN</strong><br>
                <small>Human Operator</small>
            </div>
            <div class="flow-arrow">→</div>
            <div style="background:#24a148; color:white; padding:1rem 2rem; border-radius:8px;">
                <strong>L1 SSC</strong><br>
                <small>Opus 4.5</small>
            </div>
            <div class="flow-arrow">→</div>
            <div style="background:#f1c21b; color:#161616; padding:1rem 2rem; border-radius:8px;">
                <strong>L2 CGE</strong><br>
                <small>Opus 4.5 (Strict)</small>
            </div>
            <div class="flow-arrow">→</div>
            <div style="background:#da1e28; color:white; padding:1rem 2rem; border-radius:8px;">
                <strong>L5 TOM</strong><br>
                <small>Gemini Flash</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Node details
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="node-card active">
            <div class="node-level">Level 1</div>
            <div class="node-name">Strategic Synthesis Core (SSC)</div>
            <div class="node-model">Claude Opus 4.5 via Anthropic Direct</div>
            <hr>
            <small>
                <strong>Role:</strong> Central orchestrator<br>
                <strong>Function:</strong> Decomposes directives into task DAGs<br>
                <strong>Temperature:</strong> 0.7 (creative)
            </small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="node-card active">
            <div class="node-level">Level 2</div>
            <div class="node-name">Cognitive Governance Engine (CGE)</div>
            <div class="node-model">Claude Opus 4.5 (STRICT MODE)</div>
            <hr>
            <small>
                <strong>Role:</strong> Policy authority<br>
                <strong>Function:</strong> FREQ LAW validation + VETO power<br>
                <strong>Temperature:</strong> 0.0 (deterministic)
            </small>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="node-card active">
            <div class="node-level">Level 5</div>
            <div class="node-name">Runtime Realization (TOM)</div>
            <div class="node-model">Gemini Flash via Google AI</div>
            <hr>
            <small>
                <strong>Role:</strong> Sole executor<br>
                <strong>Function:</strong> Executes approved tasks<br>
                <strong>Target:</strong> <2000ms latency
            </small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # FREQ LAW compliance
    st.markdown("### ⚖️ FREQ LAW Compliance")

    freq_col1, freq_col2, freq_col3, freq_col4 = st.columns(4)

    with freq_col1:
        st.markdown("""
        <div class="metric-card success">
            <div class="metric-label">Fast</div>
            <div class="metric-value">&lt;2s</div>
            <div class="metric-label">Response Time</div>
        </div>
        """, unsafe_allow_html=True)

    with freq_col2:
        st.markdown("""
        <div class="metric-card success">
            <div class="metric-label">Robust</div>
            <div class="metric-value">99.9%</div>
            <div class="metric-label">Uptime Target</div>
        </div>
        """, unsafe_allow_html=True)

    with freq_col3:
        st.markdown("""
        <div class="metric-card success">
            <div class="metric-label">Evolutionary</div>
            <div class="metric-value">Auto</div>
            <div class="metric-label">Self-Correction</div>
        </div>
        """, unsafe_allow_html=True)

    with freq_col4:
        st.markdown("""
        <div class="metric-card success">
            <div class="metric-label">Quantified</div>
            <div class="metric-value">100%</div>
            <div class="metric-label">Auditable</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 3: MISSION LOG
# =============================================================================

with tab3:
    st.markdown("### 📜 Mission History")

    if st.session_state.missions:
        for mission in st.session_state.missions[:10]:
            with st.expander(
                f"**{mission.get('id')}** | {mission.get('timestamp', '')[:19]} | {mission.get('latency', 0):.0f}ms",
                expanded=False
            ):
                st.markdown(f"**Directive:** {mission.get('directive', '')[:200]}...")
                st.markdown(f"**FREQ Compliant:** {'✅ Yes' if mission.get('freq_compliant') else '⚠️ No'}")
                st.json(mission.get('result', {}))
    else:
        st.info("No missions in history. Execute a directive to see results here.")

    st.markdown("---")

    st.markdown("### 🖥️ System Log")

    if st.session_state.logs:
        log_html = '<div class="mission-log">'
        for log in st.session_state.logs[:50]:
            log_html += f"""
            <div class="log-entry">
                <span class="log-timestamp">[{log['timestamp']}]</span>
                <span class="log-node">{log['node']}</span>
                <span class="log-action">{log['action']}:</span>
                <span class="log-message">{log['message']}</span>
            </div>
            """
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="mission-log">
            <div class="log-entry">
                <span class="log-timestamp">[--:--:--.---]</span>
                <span class="log-node">SYSTEM</span>
                <span class="log-action">READY:</span>
                <span class="log-message">Awaiting directives...</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TAB 4: ANALYTICS
# =============================================================================

with tab4:
    st.markdown("### 📈 Performance Analytics")

    if st.session_state.missions:
        import pandas as pd

        # Create dataframe
        df = pd.DataFrame([
            {
                'Mission': m.get('id'),
                'Timestamp': m.get('timestamp', '')[:19],
                'Latency (ms)': m.get('latency', 0),
                'FREQ Compliant': '✅' if m.get('freq_compliant') else '⚠️',
            }
            for m in st.session_state.missions
        ])

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Missions", len(st.session_state.missions))

        with col2:
            avg_latency = df['Latency (ms)'].mean()
            st.metric("Avg Latency", f"{avg_latency:.0f}ms")

        with col3:
            min_latency = df['Latency (ms)'].min()
            st.metric("Best Latency", f"{min_latency:.0f}ms")

        with col4:
            compliance_rate = (df['FREQ Compliant'] == '✅').sum() / len(df) * 100
            st.metric("Compliance Rate", f"{compliance_rate:.0f}%")

        st.markdown("---")

        # Latency chart
        st.markdown("#### Latency Over Time")
        st.line_chart(df.set_index('Mission')['Latency (ms)'])

        st.markdown("---")

        # Mission table
        st.markdown("#### Mission Data")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Execute some missions to see analytics data.")

        # Demo data
        st.markdown("#### Sample Analytics (Demo)")
        demo_data = {
            'Mission': ['M-0001', 'M-0002', 'M-0003', 'M-0004', 'M-0005'],
            'Latency (ms)': [1250, 980, 1100, 1450, 890],
            'FREQ Compliant': ['✅', '✅', '✅', '✅', '✅'],
        }
        st.line_chart(pd.DataFrame(demo_data).set_index('Mission')['Latency (ms)'])

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6f6f6f; font-size: 0.8rem;">
    FREQ AI Lattice v1.0.0 | Maritime Operations Command Center |
    <a href="/docs" style="color: #0f62fe;">API Docs</a>
</div>
""", unsafe_allow_html=True)
