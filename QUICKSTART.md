# JAX-CTSM Agents Quickstart Guide

Get started with the JAX-CTSM translation agents in 5 minutes.

## Prerequisites

- Python 3.9+
- Anthropic API key ([get one here](https://console.anthropic.com/))
- Access to CTSM and jax-ctsm repositories

## Installation

```bash
cd jax-agents

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

## Setup

1. **Create `.env` file with your API key:**

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

2. **Verify installation:**

```bash
python -c "from jax_agents import OrchestratorAgent; print('✓ Installation successful!')"
```

## Quick Examples

### Example 1: Convert a Single Module

```python
from pathlib import Path
from jax_agents import OrchestratorAgent

# Initialize
orchestrator = OrchestratorAgent(
    ctsm_dir=Path("/path/to/CTSM"),
    jax_ctsm_dir=Path("/path/to/jax-ctsm"),
)

# Convert
result = orchestrator.convert_module(
    fortran_file="src/biogeochem/CNGRespMod.F90",
)

print(f"Generated {len(result.saved_files)} files")
print(f"Cost: ${result.cost_summary['total_cost_usd']:.4f}")
```

### Example 2: Analyze Before Translating

```python
from pathlib import Path
from jax_agents import StaticAnalysisAgent

# Analyze
analyzer = StaticAnalysisAgent()
analysis = analyzer.analyze_module(
    Path("/path/to/CTSM/src/biogeochem/CNGRespMod.F90")
)

# Inspect results
print(f"Module: {analysis.module_name}")
print(f"Subroutines: {[s.name for s in analysis.subroutines]}")
print(f"Dependencies: {analysis.dependencies.modules}")

# Save for review
analysis.save(Path("analysis.json"))
```

### Example 3: Run from Command Line

```bash
# Run the included examples
python examples/convert_single_module.py
python examples/analyze_module.py
python examples/translate_with_context.py
```

## Architecture Overview

```
┌─────────────────────┐
│  Orchestrator Agent │  ← Main coordinator
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐  ┌────────────┐
│ Static  │  │ Translator │  ← Specialized agents
│ Analysis│  │   Agent    │
└─────────┘  └────────────┘
```

### Agent Roles

- **Orchestrator**: Coordinates workflow, manages dependencies, generates reports
- **Static Analysis**: Analyzes Fortran structure, extracts patterns
- **Translator**: Converts Fortran to JAX following best practices

## Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  model: "claude-sonnet-4-20250514"
  temperature: 0.0  # Deterministic output
  max_tokens: 4000

jax_patterns:
  use_immutable_state: true
  use_pure_functions: true
  add_type_hints: true
```

## Workflow

1. **Plan**: Orchestrator analyzes module and creates conversion plan
2. **Analyze**: Static Analysis agent extracts Fortran structure
3. **Translate**: Translator agent generates JAX code
4. **Report**: Orchestrator synthesizes results and generates report

## Output Files

For a module named `CNGRespMod`, you'll get:

```
output/
├── cngresp.py                    # Main physics module
├── cngresp_params.py             # Parameters (if needed)
├── test_cngresp.py               # Unit tests (if generated)
├── cngresp_translation_notes.md  # Translation decisions
└── cngresp_conversion_report.md  # Full conversion report
```

## Cost Estimation

Typical costs per module (using Claude Sonnet 4.5):

- **Simple module** (< 500 lines): $0.10 - $0.30
- **Medium module** (500-1500 lines): $0.30 - $1.00
- **Complex module** (> 1500 lines): $1.00 - $3.00

Track costs in real-time:

```python
cost = orchestrator.get_cost_estimate()
print(f"Current cost: ${cost['total_cost_usd']:.4f}")
```

## Best Practices

1. **Start small**: Begin with simple modules to verify setup
2. **Review analysis**: Check the static analysis before translating
3. **Validate output**: Review generated code, don't just trust it
4. **Test thoroughly**: Add validation tests comparing to Fortran
5. **Iterate**: Use agent feedback to refine prompts if needed

## Common Issues

### API Key Error
```
ValueError: ANTHROPIC_API_KEY not found
```
**Solution**: Create `.env` file with your API key

### Module Not Found
```
FileNotFoundError: Fortran file not found
```
**Solution**: Check paths in `config.yaml` or provide absolute paths

### High Costs
```
Warning: Token usage high
```
**Solution**: Start with smaller modules, adjust `max_tokens` in config

## Next Steps

1. **Try the examples**: Run scripts in `examples/` directory
2. **Read the docs**: See detailed documentation in `README.md`
3. **Convert a module**: Start with a simple module like `CNGRespMod.F90`
4. **Validate output**: Compare generated code with Fortran behavior
5. **Extend**: Add new agents (validation, repair) as needed

## Getting Help

- 📖 **Documentation**: See `README.md` for complete documentation
- 🐛 **Issues**: Check logs in `logs/` directory
- 💬 **Examples**: Review `examples/` for common patterns

## What's Next?

After successful conversion:

1. **Validate**: Compare JAX output with Fortran
2. **Test**: Add comprehensive unit tests
3. **Optimize**: Profile and optimize JAX code
4. **Integrate**: Connect with existing jax-ctsm modules
5. **Document**: Add examples and usage documentation

---

**Ready to convert CTSM to JAX! 🚀**

