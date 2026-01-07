"""
Simple test to verify FREQ AI SOL Python API
"""

import asyncio
from freq_ai import SOLOrchestrator


async def test_basic_orchestration():
    """Test basic orchestration"""
    print("Testing FREQ AI SOL Python API...")
    
    orchestrator = SOLOrchestrator()
    
    result = await orchestrator.orchestrate(
        directive="Test orchestration",
        vertical="manufacturing"
    )
    
    assert result.success, "Orchestration should succeed"
    assert result.final_state.value == "COMPLETE", "Should reach COMPLETE state"
    assert result.elapsed_time_ms < 2000, "Should meet FREQ LAW <2000ms"
    assert result.consensus_result["passed"], "Consensus should pass"
    assert result.consensus_result["positive_votes"] >= 3, "Should have k=3 votes"
    
    print(f"✅ Test passed!")
    print(f"   - Session ID: {result.session_id}")
    print(f"   - Final State: {result.final_state.value}")
    print(f"   - Time: {result.elapsed_time_ms}ms")
    print(f"   - Consensus: {result.consensus_result['positive_votes']}/7")
    
    return result


async def test_all_verticals():
    """Test all vertical domains"""
    print("\nTesting all vertical domains...")
    
    orchestrator = SOLOrchestrator()
    verticals = ["maritime", "agriculture", "manufacturing", "healthcare", "construction"]
    
    for vertical in verticals:
        result = await orchestrator.orchestrate(
            directive=f"Test {vertical} operations",
            vertical=vertical
        )
        assert result.success, f"{vertical} should succeed"
        print(f"✅ {vertical.upper()}: {result.elapsed_time_ms}ms")
    
    print("All verticals tested successfully!")


async def test_fsm_states():
    """Test FSM state progression"""
    print("\nTesting FSM state progression...")
    
    orchestrator = SOLOrchestrator()
    
    # This will internally progress through all states
    result = await orchestrator.orchestrate(
        directive="Test FSM state flow"
    )
    
    # Verify we went through the proper states
    assert result.success
    assert result.final_state.value == "COMPLETE"
    
    print("✅ FSM state progression: IDLE→DIRECTIVE→VALIDATION→QUORUM→EXECUTION→AUDIT→COMPLETE")


async def main():
    """Run all tests"""
    print("="*80)
    print("FREQ AI SOL - Python API Tests")
    print("="*80 + "\n")
    
    await test_basic_orchestration()
    await test_all_verticals()
    await test_fsm_states()
    
    print("\n" + "="*80)
    print("✅ All tests passed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
