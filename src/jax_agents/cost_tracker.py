"""Cost tracking utilities for JAX-CTSM agents."""

from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
import json


@dataclass
class AgentCostEntry:
    """Single cost entry for an agent operation."""
    agent_name: str
    operation: str  # e.g., "translate", "test", "repair"
    module_name: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    input_cost_usd: float = 0.0
    output_cost_usd: float = 0.0
    total_cost_usd: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CostTracker:
    """Track costs across multiple agent operations."""
    
    entries: List[AgentCostEntry] = field(default_factory=list)
    
    def add_entry(self, entry: AgentCostEntry):
        """Add a cost entry."""
        self.entries.append(entry)
    
    def add_from_agent(self, agent, operation: str, module_name: str = ""):
        """Add cost entry from an agent's current state."""
        cost_info = agent.get_cost_estimate()
        entry = AgentCostEntry(
            agent_name=agent.name,
            operation=operation,
            module_name=module_name,
            input_tokens=cost_info['input_tokens'],
            output_tokens=cost_info['output_tokens'],
            input_cost_usd=cost_info['input_cost_usd'],
            output_cost_usd=cost_info['output_cost_usd'],
            total_cost_usd=cost_info['total_cost_usd']
        )
        self.add_entry(entry)
        return entry
    
    def get_total_cost(self) -> Dict[str, float]:
        """Get total cost across all operations."""
        total_input_tokens = sum(e.input_tokens for e in self.entries)
        total_output_tokens = sum(e.output_tokens for e in self.entries)
        total_cost = sum(e.total_cost_usd for e in self.entries)
        
        return {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "total_cost_usd": total_cost
        }
    
    def get_cost_by_operation(self) -> Dict[str, Dict[str, float]]:
        """Get costs grouped by operation type."""
        by_operation = {}
        
        for entry in self.entries:
            if entry.operation not in by_operation:
                by_operation[entry.operation] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_cost_usd": 0.0
                }
            
            by_operation[entry.operation]["input_tokens"] += entry.input_tokens
            by_operation[entry.operation]["output_tokens"] += entry.output_tokens
            by_operation[entry.operation]["total_cost_usd"] += entry.total_cost_usd
        
        return by_operation
    
    def get_cost_by_module(self) -> Dict[str, Dict[str, float]]:
        """Get costs grouped by module."""
        by_module = {}
        
        for entry in self.entries:
            if not entry.module_name:
                continue
                
            if entry.module_name not in by_module:
                by_module[entry.module_name] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_cost_usd": 0.0
                }
            
            by_module[entry.module_name]["input_tokens"] += entry.input_tokens
            by_module[entry.module_name]["output_tokens"] += entry.output_tokens
            by_module[entry.module_name]["total_cost_usd"] += entry.total_cost_usd
        
        return by_module
    
    def get_cost_by_agent(self) -> Dict[str, Dict[str, float]]:
        """Get costs grouped by agent."""
        by_agent = {}
        
        for entry in self.entries:
            if entry.agent_name not in by_agent:
                by_agent[entry.agent_name] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_cost_usd": 0.0
                }
            
            by_agent[entry.agent_name]["input_tokens"] += entry.input_tokens
            by_agent[entry.agent_name]["output_tokens"] += entry.output_tokens
            by_agent[entry.agent_name]["total_cost_usd"] += entry.total_cost_usd
        
        return by_agent
    
    def print_summary(self):
        """Print a formatted cost summary."""
        print("\n" + "="*80)
        print("COST SUMMARY")
        print("="*80 + "\n")
        
        # Total costs
        total = self.get_total_cost()
        print(f"Total Cost:        ${total['total_cost_usd']:.4f}")
        print(f"Total Input Tokens: {total['total_input_tokens']:,}")
        print(f"Total Output Tokens:{total['total_output_tokens']:,}")
        print(f"Total Tokens:       {total['total_tokens']:,}\n")
        
        # By operation
        print("By Operation:")
        print("-" * 80)
        by_operation = self.get_cost_by_operation()
        for op, costs in sorted(by_operation.items()):
            print(f"  {op:20s} ${costs['total_cost_usd']:>8.4f}  "
                  f"({costs['input_tokens']:>8,} in / {costs['output_tokens']:>8,} out)")
        
        # By agent
        print("\nBy Agent:")
        print("-" * 80)
        by_agent = self.get_cost_by_agent()
        for agent, costs in sorted(by_agent.items()):
            print(f"  {agent:20s} ${costs['total_cost_usd']:>8.4f}  "
                  f"({costs['input_tokens']:>8,} in / {costs['output_tokens']:>8,} out)")
        
        # By module
        by_module = self.get_cost_by_module()
        if by_module:
            print("\nBy Module:")
            print("-" * 80)
            for module, costs in sorted(by_module.items()):
                print(f"  {module:20s} ${costs['total_cost_usd']:>8.4f}  "
                      f"({costs['input_tokens']:>8,} in / {costs['output_tokens']:>8,} out)")
        
        print("="*80 + "\n")
    
    def save_to_json(self, filepath: str):
        """Save cost tracking data to JSON file."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "entries": [
                {
                    "agent_name": e.agent_name,
                    "operation": e.operation,
                    "module_name": e.module_name,
                    "input_tokens": e.input_tokens,
                    "output_tokens": e.output_tokens,
                    "input_cost_usd": e.input_cost_usd,
                    "output_cost_usd": e.output_cost_usd,
                    "total_cost_usd": e.total_cost_usd,
                    "timestamp": e.timestamp
                }
                for e in self.entries
            ],
            "summary": {
                "total": self.get_total_cost(),
                "by_operation": self.get_cost_by_operation(),
                "by_agent": self.get_cost_by_agent(),
                "by_module": self.get_cost_by_module()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

