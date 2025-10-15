# JAX-CTSM Translation Agents

Multi-agent system for converting Fortran CTSM code to JAX using Claude 4.5 Sonnet.

## Overview

This project provides an AI-powered multi-agent architecture to automate the conversion of CTSM's Fortran codebase to JAX. The system consists of specialized LLM agents that work together to analyze, translate, and validate the conversion.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                     │
│  • Coordinates overall workflow                         │
│  • Manages agent communication                          │
│  • Tracks conversion progress                           │
└─────────────┬───────────────────────────────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌─────────────┐  ┌──────────────┐
│   Static    │  │  Translator  │
│  Analysis   │  │    Agent     │
│   Agent     │  │              │
│             │  │  • Fortran → │
│ • Analyze   │  │    JAX       │
│   Fortran   │  │  • Apply     │
│   structure │  │    patterns  │
│ • Extract   │  │  • Generate  │
│   deps      │  │    code      │
│ • Map data  │  │              │
│   types     │  │              │
└─────────────┘  └──────────────┘
```

### Future Agents (extensible):
- **Validation Agent**: Compares outputs with Fortran
- **Repair Agent**: Fixes issues in generated code

## Agents

### 1. Orchestrator Agent
**Role**: Project manager and coordinator
- Plans the conversion strategy for a module
- Delegates tasks to specialized agents
- Synthesizes results from multiple agents
- Tracks progress and dependencies
- Generates final reports

### 2. Static Analysis Agent
**Role**: Code archaeologist and cartographer
- Analyzes Fortran module structure
- Extracts dependencies (uses, includes, modules)
- Identifies data structures and types
- Maps subroutines and functions
- Detects control flow patterns
- Identifies parameters and constants

### 3. Translator Agent
**Role**: Code converter and pattern matcher
- Converts Fortran syntax to JAX
- Applies JAX-specific patterns (pure functions, immutable state)
- Handles spatial hierarchy mapping
- Generates type hints and docstrings
- Creates parameter classes
- Converts loops to vectorized operations

## Installation

```bash
cd jax-agents
pip install -e .
```

## Environment Setup

Create a `.env` file with your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

## Quick Start

```python
from jax_agents import OrchestratorAgent
from pathlib import Path

# Initialize orchestrator
orchestrator = OrchestratorAgent(
    ctsm_dir=Path("/path/to/CTSM"),
    jax_ctsm_dir=Path("/path/to/jax-ctsm"),
)

# Convert a Fortran module
result = orchestrator.convert_module(
    fortran_file="CTSM/src/biogeochem/CNGRespMod.F90",
    output_dir="jax-ctsm/src/jax_ctsm/physics/",
)

print(f"Conversion Status: {result.status}")
print(f"Generated Files: {result.files}")
print(f"Analysis: {result.analysis}")
```

## Example Workflow

```python
# Step 1: Analyze a Fortran module
from jax_agents import StaticAnalysisAgent

analyzer = StaticAnalysisAgent()
analysis = analyzer.analyze_fortran_module("CTSM/src/biogeochem/CNGRespMod.F90")

print("Dependencies:", analysis.dependencies)
print("Data Types:", analysis.data_types)
print("Subroutines:", analysis.subroutines)

# Step 2: Translate to JAX
from jax_agents import TranslatorAgent

translator = TranslatorAgent()
jax_code = translator.translate_module(
    fortran_code=analysis.source_code,
    analysis=analysis,
)

print("Generated JAX code:")
print(jax_code)

# Step 3: Use orchestrator for full workflow
orchestrator = OrchestratorAgent()
result = orchestrator.convert_module("CNGRespMod.F90")
```

## Configuration

The agents can be configured via `config.yaml`:

```yaml
# Agent configuration
claude_model: "claude-sonnet-4-20250514"
temperature: 0.0  # Deterministic for code generation
max_tokens: 4000

# Conversion settings
output_format:
  add_docstrings: true
  add_type_hints: true
  add_tests: true
  validation_level: "strict"

# JAX patterns
jax_patterns:
  use_jit: true
  use_vmap: true
  immutable_state: true
  pure_functions: true
```

## Project Structure

```
jax-agents/
├── src/
│   └── jax_agents/
│       ├── __init__.py
│       ├── base_agent.py          # Base agent class with Claude integration
│       ├── orchestrator.py         # Orchestrator agent
│       ├── static_analysis.py      # Static analysis agent
│       ├── translator.py           # Translator agent
│       ├── prompts/                # Agent prompt templates
│       │   ├── orchestrator_prompts.py
│       │   ├── analysis_prompts.py
│       │   └── translation_prompts.py
│       └── utils/
│           ├── fortran_parser.py   # Fortran parsing utilities
│           ├── jax_templates.py    # JAX code templates
│           └── validation.py       # Code validation utilities
├── examples/
│   ├── convert_single_module.py
│   └── batch_conversion.py
├── tests/
│   ├── test_static_analysis.py
│   ├── test_translator.py
│   └── test_orchestrator.py
├── config.yaml
├── pyproject.toml
└── README.md
```

## Features

- **Multi-agent collaboration**: Specialized agents work together
- **Claude 4.5 Sonnet**: State-of-the-art LLM for code conversion
- **Pattern-based translation**: Uses proven JAX patterns from existing conversions
- **Incremental conversion**: Handle modules one at a time
- **Dependency tracking**: Understand module relationships
- **Validation ready**: Extensible to add validation agents

## Design Principles

1. **Separation of Concerns**: Each agent has a specific role
2. **Extensible**: Easy to add new agents (validation, repair, etc.)
3. **Context-aware**: Agents learn from existing jax-ctsm examples
4. **Transparent**: All agent interactions are logged
5. **Iterative**: Support for refinement based on feedback

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Adding a New Agent
```python
from jax_agents.base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            role="Agent description",
        )
    
    def process(self, input_data):
        # Your agent logic
        response = self.query_claude(prompt)
        return response
```

## Examples

See `examples/` directory for:
- Single module conversion
- Batch conversion of multiple modules
- Custom analysis workflows
- Integration with validation

## References

- **JAX-CTSM Implementation**: `../jax-ctsm/`
- **Original CTSM**: `../CTSM/`
- **Claude API**: https://docs.anthropic.com/
- **JAX Documentation**: https://jax.readthedocs.io/

## License

BSD-3-Clause (same as CTSM)

## Contributing

Contributions welcome! Please follow the existing agent patterns and add tests.

## Future Work

- [ ] Add validation agent for comparing outputs
- [ ] Add repair agent for fixing conversion issues
- [ ] Add test generation agent
- [ ] Support for incremental updates
- [ ] Integration with CI/CD
- [ ] Performance optimization agent

