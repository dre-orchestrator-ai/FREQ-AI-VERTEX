#!/usr/bin/env python3
"""
FREQ AI SOL Command Line Interface
Natural language orchestration interface
"""

import asyncio
import argparse
import sys
import json
from typing import Optional
import structlog

from freq_ai.orchestration.orchestrator import SOLOrchestrator
from freq_ai.verticals.vertical_context import Vertical

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger(__name__)


async def run_orchestration(
    directive: str,
    vertical: Optional[str] = None,
    project_id: Optional[str] = None,
    verbose: bool = False
):
    """
    Run orchestration for a directive
    
    Args:
        directive: Natural language directive
        vertical: Optional vertical domain
        project_id: Optional GCP project ID
        verbose: Enable verbose output
    """
    print("\n" + "="*80)
    print("FREQ AI SOPHISTICATED OPERATIONAL LATTICE (SOL)")
    print("Natural Language Orchestration System")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    print(f"📡 Initializing SOL Orchestrator...")
    orchestrator = SOLOrchestrator(
        project_id=project_id,
        max_response_time_ms=2000,
        consensus_k=3,
        audit_enabled=True
    )
    
    # Display configuration
    if verbose:
        status = orchestrator.get_status()
        print(f"\n🔧 Configuration:")
        print(f"  - Nodes: {len(status['nodes'])}")
        print(f"  - FREQ LAW: <{status['freq_law']['max_response_time_ms']}ms, k={status['freq_law']['consensus_k']}")
        print(f"  - Audit Enabled: {status['freq_law']['audit_enabled']}")
        print(f"  - Supported Verticals: {', '.join(status['verticals'])}")
    
    # Process directive
    print(f"\n📝 Processing Directive:")
    print(f"  {directive}")
    if vertical:
        print(f"  Vertical: {vertical.upper()}")
    
    print(f"\n⚙️  Orchestrating through FSM states...")
    print(f"  IDLE → DIRECTIVE → VALIDATION → QUORUM → EXECUTION → AUDIT → COMPLETE")
    
    # Execute orchestration
    result = await orchestrator.orchestrate(
        directive=directive,
        vertical=vertical
    )
    
    # Display results
    print(f"\n" + "="*80)
    if result.success:
        print(f"✅ ORCHESTRATION SUCCESSFUL")
    else:
        print(f"❌ ORCHESTRATION FAILED")
    print("="*80)
    
    print(f"\n📊 Results:")
    print(f"  Session ID: {result.session_id}")
    print(f"  Final State: {result.final_state.value}")
    print(f"  Elapsed Time: {result.elapsed_time_ms}ms")
    print(f"  FREQ LAW Compliance: {'✅ YES' if result.elapsed_time_ms < 2000 else '❌ NO'}")
    
    if result.consensus_result:
        print(f"\n🗳️  Consensus (k=3):")
        print(f"  Positive Votes: {result.consensus_result['positive_votes']}/{len(result.consensus_result['node_votes'])}")
        print(f"  Status: {'✅ PASSED' if result.consensus_result['passed'] else '❌ FAILED'}")
        
        if verbose:
            print(f"\n  Node Votes:")
            for node, vote in result.consensus_result['node_votes'].items():
                vote_symbol = "✅" if vote else "❌"
                print(f"    {vote_symbol} {node}")
    
    if verbose and result.node_responses:
        print(f"\n📡 Node Responses:")
        for resp in result.node_responses:
            status_symbol = "✅" if resp.get("success") else "❌"
            print(f"\n  {status_symbol} {resp['node_name']}:")
            if resp.get("success"):
                response_preview = resp.get("response", "")[:150]
                print(f"    {response_preview}...")
            else:
                print(f"    Error: {resp.get('error', 'Unknown error')}")
    
    if result.error:
        print(f"\n⚠️  Error: {result.error}")
    
    print(f"\n" + "="*80 + "\n")
    
    # Return result as JSON if needed
    return result


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FREQ AI SOL - Natural Language Orchestration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic directive
  %(prog)s "Optimize shipping routes for next quarter"
  
  # With vertical domain
  %(prog)s "Schedule preventive maintenance for fleet" --vertical maritime
  
  # With GCP project for Vertex AI
  %(prog)s "Analyze crop yield predictions" --vertical agriculture --project my-gcp-project
  
  # Verbose output
  %(prog)s "Design new warehouse layout" --vertical manufacturing --verbose

Supported Verticals:
  - maritime      : Maritime operations and logistics
  - agriculture   : Agricultural operations and supply chain
  - manufacturing : Manufacturing processes and optimization
  - healthcare    : Healthcare systems and compliance
  - construction  : Construction project management and safety
        """
    )
    
    parser.add_argument(
        "directive",
        type=str,
        help="Natural language directive to orchestrate"
    )
    
    parser.add_argument(
        "--vertical",
        "-v",
        type=str,
        choices=[v.value for v in Vertical],
        help="Target vertical domain"
    )
    
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        help="Google Cloud project ID for Vertex AI"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON"
    )
    
    args = parser.parse_args()
    
    # Run orchestration
    try:
        result = asyncio.run(run_orchestration(
            directive=args.directive,
            vertical=args.vertical,
            project_id=args.project,
            verbose=args.verbose
        ))
        
        # Output JSON if requested
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Orchestration interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
