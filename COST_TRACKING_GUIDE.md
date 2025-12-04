# Cost Tracking Guide

This guide explains how to track and analyze costs when running the JAX-CTSM translation workflow.

## Overview

All JAX-CTSM agents now include comprehensive cost tracking that monitors:
- **Input tokens**: Tokens sent to Claude API
- **Output tokens**: Tokens received from Claude API
- **Cost**: Calculated based on Claude Sonnet 4.5 pricing ($3/M input, $15/M output)

## Cost Tracking Features

### 1. Per-Agent Tracking

Each agent (BaseAgent and its subclasses) automatically tracks:
- Total input tokens
- Total output tokens
- Estimated cost in USD

Access cost info for any agent:

```python
from jax_agents import TranslatorAgent

translator = TranslatorAgent(...)
# ... perform translations ...

cost_info = translator.get_cost_estimate()
print(f"Cost: ${cost_info['total_cost_usd']:.4f}")
print(f"Input tokens: {cost_info['input_tokens']:,}")
print(f"Output tokens: {cost_info['output_tokens']:,}")
```

### 2. CostTracker Class

The `CostTracker` class provides centralized cost tracking across multiple agents and operations:

```python
from jax_agents import CostTracker, TranslatorAgent

cost_tracker = CostTracker()
translator = TranslatorAgent(...)

# Translate a module
result = translator.translate_module("clm_varctl", output_dir)

# Track the cost
entry = cost_tracker.add_from_agent(
    translator,
    operation="translate",
    module_name="clm_varctl"
)

print(f"Module cost: ${entry.total_cost_usd:.4f}")
```

### 3. Cost Analysis

The `CostTracker` provides several analysis methods:

```python
# Total costs across all operations
total = cost_tracker.get_total_cost()
print(f"Total: ${total['total_cost_usd']:.4f}")

# Costs by operation type (translate, test, repair)
by_operation = cost_tracker.get_cost_by_operation()
for op, costs in by_operation.items():
    print(f"{op}: ${costs['total_cost_usd']:.4f}")

# Costs by module
by_module = cost_tracker.get_cost_by_module()
for module, costs in by_module.items():
    print(f"{module}: ${costs['total_cost_usd']:.4f}")

# Costs by agent
by_agent = cost_tracker.get_cost_by_agent()
for agent, costs in by_agent.items():
    print(f"{agent}: ${costs['total_cost_usd']:.4f}")
```

### 4. Saving and Reporting

Save cost details to JSON for later analysis:

```python
cost_tracker.save_to_json("workflow_costs.json")
```

Print a formatted summary:

```python
cost_tracker.print_summary()
```

## Running Workflows with Cost Tracking

### Option 1: Using the Enhanced translate_with_json.py

The updated `translate_with_json.py` now displays costs per module and totals:

```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/translate_with_json.py
```

Output will show:
```
Translating 'clm_varctl'...
✓ Translated clm_varctl successfully!
💰 Cost: $0.1234 (1,234 in / 5,678 out)

...

💰 Cost Summary by Module:
  clm_varctl               $0.1234  (  1,234 in /   5,678 out)
  SoilStateType            $0.2345  (  2,345 in /   6,789 out)
  SoilTemperatureMod       $0.3456  (  3,456 in /   7,890 out)

────────────────────────────────────────────────────────────────
Total Cost:                    $0.7035
Total Input Tokens:             7,035
Total Output Tokens:           20,357
Total Tokens:                  27,392
```

### Option 2: Using the Full Workflow Script

Run the complete workflow with comprehensive cost tracking:

```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/full_workflow_with_costs.py
```

This will:
1. Translate all modules
2. Generate tests for each module
3. (Simulate repair phase)
4. Display detailed cost breakdown by module and operation
5. Save costs to `workflow_costs.json`

### Option 3: Using the Shell Script Workflow

The `run_translation_workflow.sh` script now tracks costs:

```bash
cd /burg-archive/home/mck2199/jax-agents
./run_translation_workflow.sh --all
```

Cost information will be:
- Displayed during execution
- Shown in final summary
- Saved to `workflow_costs.log`

## Per-Module Cost Tracking

To track costs per translation unit (individual module):

```python
translator = TranslatorAgent(...)

# Reset counts before translating each module
translator.total_input_tokens = 0
translator.total_output_tokens = 0

result = translator.translate_module("clm_varctl", output_dir)

cost = translator.get_cost_estimate()
print(f"clm_varctl cost: ${cost['total_cost_usd']:.4f}")
```

## Cost Breakdown Examples

### Translation Only

Typical costs for translating a module:
- **Simple module** (clm_varctl): ~$0.10-0.30
- **Medium complexity** (SoilStateType): ~$0.30-0.60
- **High complexity** (SoilTemperatureMod): ~$0.60-1.50

### Complete Workflow

For a complete workflow (translate + test + repair):
- **Translation**: 40-50% of total cost
- **Test Generation**: 30-40% of total cost
- **Repair** (if needed): 10-30% of total cost

### Example Full Workflow Costs

For 3 modules (clm_varctl, SoilStateType, SoilTemperatureMod):
- **Translation**: ~$1.00-2.50
- **Test Generation**: ~$0.75-2.00
- **Repair** (if needed): ~$0.50-1.50
- **Total**: ~$2.25-6.00

*Note: Actual costs vary based on module complexity, code size, and number of repair iterations needed.*

## Pricing Reference

**Claude Sonnet 4.5 (as of 2025):**
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

## Best Practices

1. **Reset Token Counts**: Reset `total_input_tokens` and `total_output_tokens` between modules for accurate per-module tracking.

2. **Use CostTracker**: For multi-module workflows, use `CostTracker` to aggregate and analyze costs.

3. **Save Cost Data**: Always save cost data to JSON for audit trails and optimization analysis.

4. **Monitor Trends**: Track costs over time to identify expensive operations and optimize prompts.

5. **Batch Operations**: Process multiple modules in a single workflow run to amortize initialization costs.

## Troubleshooting

### Cost Seems Too High

- Check for repeated API calls (retry logic)
- Review conversation history size
- Consider reducing `max_tokens` if possible
- Use more specific prompts to reduce output verbosity

### Cost Not Being Tracked

- Ensure you're using the latest version of agents
- Check that `total_input_tokens` and `total_output_tokens` are being updated
- Verify API responses include usage information

### Cost Calculations Don't Match

- Verify pricing in `base_agent.py` (should be $3/M input, $15/M output for Sonnet 4.5)
- Check for currency conversion issues
- Ensure all agents are being tracked

## Integration with Existing Code

To add cost tracking to existing workflows:

```python
from jax_agents import CostTracker

# At the start of your workflow
cost_tracker = CostTracker()

# After each agent operation
cost_tracker.add_from_agent(agent, operation="translate", module_name="my_module")

# At the end
cost_tracker.print_summary()
cost_tracker.save_to_json("costs.json")
```

## Advanced Usage

### Custom Cost Analysis

```python
# Get detailed entry-level data
for entry in cost_tracker.entries:
    print(f"{entry.timestamp}: {entry.agent_name} {entry.operation} "
          f"{entry.module_name} - ${entry.total_cost_usd:.4f}")

# Calculate average cost per module
by_module = cost_tracker.get_cost_by_module()
avg_cost = sum(c['total_cost_usd'] for c in by_module.values()) / len(by_module)
print(f"Average cost per module: ${avg_cost:.4f}")
```

### Filtering Costs

```python
# Get only translation costs
translation_entries = [e for e in cost_tracker.entries if e.operation == "translate"]
translation_cost = sum(e.total_cost_usd for e in translation_entries)
print(f"Total translation cost: ${translation_cost:.4f}")
```

## Questions?

For more information, see:
- `src/jax_agents/base_agent.py` - Base cost tracking implementation
- `src/jax_agents/cost_tracker.py` - CostTracker class
- `examples/full_workflow_with_costs.py` - Complete example
- `examples/translate_with_json.py` - Translation example with costs

