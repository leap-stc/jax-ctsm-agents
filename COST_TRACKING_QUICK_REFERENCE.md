# Cost Tracking Quick Reference

## 🚀 Quick Commands

### Run Translation with Cost Tracking
```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/translate_with_json.py
```

### Run Full Workflow with Cost Tracking
```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/full_workflow_with_costs.py
```

### Run Shell Script Workflow
```bash
cd /burg-archive/home/mck2199/jax-agents
./run_translation_workflow.sh --all
```

## 📊 What You'll See

### During Execution
```
Translating: clm_varctl
✓ Translated clm_varctl successfully!
💰 Cost: $0.1234 (1,234 in / 5,678 out)
```

### Final Summary
```
╔══════════════════════════════════════════════════════════╗
║              COMPLETE WORKFLOW COST SUMMARY              ║
╚══════════════════════════════════════════════════════════╝

Translation:                   $1.2500
Test Generation:               $0.8750
Repair:                        $0.4250
────────────────────────────────────────────────────────────
TOTAL COST:                    $2.5500
```

## 💻 Code Snippets

### Get Cost from Any Agent
```python
cost = agent.get_cost_estimate()
print(f"${cost['total_cost_usd']:.4f}")
```

### Track Multiple Operations
```python
from jax_agents import CostTracker

tracker = CostTracker()
tracker.add_from_agent(translator, "translate", "module_name")
tracker.print_summary()
```

### Per-Module Tracking
```python
# Reset before each module
translator.total_input_tokens = 0
translator.total_output_tokens = 0

# Translate
result = translator.translate_module("module_name", output_dir)

# Get cost
cost = translator.get_cost_estimate()
```

## 💰 Pricing Reference

**Claude Sonnet 4.5**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Typical Module Costs**
- Simple: $0.10-0.30
- Medium: $0.30-0.60
- Complex: $0.60-1.50

**Complete Workflow (3 modules)**
- Total: $2.25-6.00

## 📁 Output Files

- `workflow_costs.log` - Shell script cost log
- `workflow_costs.json` - Detailed JSON cost data

## 🔍 Analysis Methods

```python
# Total costs
tracker.get_total_cost()

# By operation (translate/test/repair)
tracker.get_cost_by_operation()

# By module
tracker.get_cost_by_module()

# By agent
tracker.get_cost_by_agent()

# Print summary
tracker.print_summary()

# Save to JSON
tracker.save_to_json("costs.json")
```

## 📖 Full Documentation

- `COST_TRACKING_GUIDE.md` - Complete guide
- `COST_TRACKING_IMPLEMENTED.md` - Implementation details
- `examples/full_workflow_with_costs.py` - Example code

## ✅ Ready to Use

All cost tracking is now integrated and ready! Just run any workflow and costs will be displayed automatically.

