#!/usr/bin/env python3
"""
Quick test script to verify cost tracking is working.
This doesn't make real API calls, just demonstrates the tracking infrastructure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from jax_agents.cost_tracker import CostTracker, AgentCostEntry

def test_cost_tracker():
    """Test cost tracking functionality."""
    
    print("="*80)
    print("COST TRACKING TEST")
    print("="*80 + "\n")
    
    # Create cost tracker
    tracker = CostTracker()
    
    # Simulate some cost entries
    print("Simulating translation costs...\n")
    
    # Module 1: clm_varctl
    entry1 = AgentCostEntry(
        agent_name="TranslatorAgent",
        operation="translate",
        module_name="clm_varctl",
        input_tokens=1234,
        output_tokens=5678,
        input_cost_usd=0.003702,  # 1234 * $3/M
        output_cost_usd=0.085170,  # 5678 * $15/M
        total_cost_usd=0.088872
    )
    tracker.add_entry(entry1)
    print(f"✓ Added: clm_varctl translation - ${entry1.total_cost_usd:.4f}")
    
    # Module 2: SoilStateType
    entry2 = AgentCostEntry(
        agent_name="TranslatorAgent",
        operation="translate",
        module_name="SoilStateType",
        input_tokens=2345,
        output_tokens=6789,
        input_cost_usd=0.007035,
        output_cost_usd=0.101835,
        total_cost_usd=0.108870
    )
    tracker.add_entry(entry2)
    print(f"✓ Added: SoilStateType translation - ${entry2.total_cost_usd:.4f}")
    
    # Test generation for module 1
    entry3 = AgentCostEntry(
        agent_name="TestAgent",
        operation="test",
        module_name="clm_varctl",
        input_tokens=987,
        output_tokens=3456,
        input_cost_usd=0.002961,
        output_cost_usd=0.051840,
        total_cost_usd=0.054801
    )
    tracker.add_entry(entry3)
    print(f"✓ Added: clm_varctl test generation - ${entry3.total_cost_usd:.4f}")
    
    # Repair for module 2
    entry4 = AgentCostEntry(
        agent_name="RepairAgent",
        operation="repair",
        module_name="SoilStateType",
        input_tokens=1500,
        output_tokens=4000,
        input_cost_usd=0.004500,
        output_cost_usd=0.060000,
        total_cost_usd=0.064500
    )
    tracker.add_entry(entry4)
    print(f"✓ Added: SoilStateType repair - ${entry4.total_cost_usd:.4f}")
    
    print("\n" + "="*80)
    
    # Display summary
    tracker.print_summary()
    
    # Test individual analysis methods
    print("\n" + "="*80)
    print("DETAILED ANALYSIS")
    print("="*80 + "\n")
    
    total = tracker.get_total_cost()
    print(f"Total workflow cost: ${total['total_cost_usd']:.4f}\n")
    
    print("By Operation:")
    by_op = tracker.get_cost_by_operation()
    for op, costs in by_op.items():
        print(f"  {op}: ${costs['total_cost_usd']:.4f}")
    
    print("\nBy Module:")
    by_mod = tracker.get_cost_by_module()
    for mod, costs in by_mod.items():
        print(f"  {mod}: ${costs['total_cost_usd']:.4f}")
    
    print("\nBy Agent:")
    by_agent = tracker.get_cost_by_agent()
    for agent, costs in by_agent.items():
        print(f"  {agent}: ${costs['total_cost_usd']:.4f}")
    
    # Save to JSON
    output_file = Path(__file__).parent / "test_costs.json"
    tracker.save_to_json(str(output_file))
    print(f"\n✓ Cost data saved to: {output_file}")
    
    print("\n" + "="*80)
    print("✅ COST TRACKING TEST PASSED")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_cost_tracker()

