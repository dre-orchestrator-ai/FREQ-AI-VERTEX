"""
Example usage of FREQ AI SOL
Demonstrates natural language orchestration
"""

import asyncio
from freq_ai.orchestration.orchestrator import SOLOrchestrator


async def example_maritime():
    """Example: Maritime operations"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Maritime Operations")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Optimize shipping routes from Shanghai to Los Angeles for Q2 2026",
        vertical="maritime"
    )
    
    print(f"\nResult: {result.final_state.value}")
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    
    if result.consensus_result:
        print(f"Consensus: {result.consensus_result['positive_votes']}/7 nodes approved")
    
    return result


async def example_agriculture():
    """Example: Agriculture operations"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Agriculture Operations")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Schedule harvest operations for corn fields based on weather forecast",
        vertical="agriculture"
    )
    
    print(f"\nResult: {result.final_state.value}")
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    
    return result


async def example_manufacturing():
    """Example: Manufacturing operations"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Manufacturing Operations")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Implement predictive maintenance for assembly line equipment",
        vertical="manufacturing"
    )
    
    print(f"\nResult: {result.final_state.value}")
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    
    return result


async def example_healthcare():
    """Example: Healthcare operations"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Healthcare Operations")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Optimize patient scheduling system to reduce wait times",
        vertical="healthcare"
    )
    
    print(f"\nResult: {result.final_state.value}")
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    
    return result


async def example_construction():
    """Example: Construction operations"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Construction Operations")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Create safety compliance checklist for high-rise construction project",
        vertical="construction"
    )
    
    print(f"\nResult: {result.final_state.value}")
    print(f"Success: {result.success}")
    print(f"Time: {result.elapsed_time_ms}ms")
    
    return result


async def example_complex_workflow():
    """Example: Complex multi-step workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Complex Multi-Step Workflow")
    print("="*80)
    
    orchestrator = SOLOrchestrator()
    
    # Step 1: Analyze current state
    print("\n📍 Step 1: Analyzing current manufacturing efficiency...")
    result1 = await orchestrator.orchestrate(
        directive="Analyze current manufacturing efficiency and identify bottlenecks",
        vertical="manufacturing"
    )
    print(f"  Status: {result1.final_state.value} ({result1.elapsed_time_ms}ms)")
    
    # Step 2: Design improvements
    if result1.success:
        print("\n📍 Step 2: Designing process improvements...")
        result2 = await orchestrator.orchestrate(
            directive="Design automated quality control system for identified bottlenecks",
            vertical="manufacturing"
        )
        print(f"  Status: {result2.final_state.value} ({result2.elapsed_time_ms}ms)")
    
    # Step 3: Implementation plan
    if result1.success and result2.success:
        print("\n📍 Step 3: Creating implementation plan...")
        result3 = await orchestrator.orchestrate(
            directive="Create phased implementation plan with resource allocation",
            vertical="manufacturing"
        )
        print(f"  Status: {result3.final_state.value} ({result3.elapsed_time_ms}ms)")
    
    print("\n✅ Workflow completed successfully!")
    
    return result3


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("FREQ AI SOPHISTICATED OPERATIONAL LATTICE")
    print("Example Usage Demonstrations")
    print("="*80)
    
    # Run examples
    await example_maritime()
    await example_agriculture()
    await example_manufacturing()
    await example_healthcare()
    await example_construction()
    await example_complex_workflow()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
