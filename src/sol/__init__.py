"""
Sophisticated Operational Lattice (SOL)

A distributed AI orchestration system deployed on Google Cloud Vertex AI 
Agent Builder using Gemini substrates.

FREQ LAW Governance:
- Fast: Response times < 2000ms
- Robust: Resilient to failures with quorum consensus
- Evolutionary: Continuous improvement cycles
- Quantified: All outputs measured and logged to BigQuery
"""

__version__ = "0.1.0"

from .governance.freq_law import FreqLaw
from .consensus.quorum import QuorumConsensus
from .nodes.base import LatticeNode

__all__ = ["FreqLaw", "QuorumConsensus", "LatticeNode"]
