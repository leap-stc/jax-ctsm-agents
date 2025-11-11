# JAX-CTSM Agents Architecture

Detailed architecture documentation for the multi-agent translation system.

## System Overview

The JAX-CTSM translation system is a multi-agent architecture that uses specialized LLM agents to convert Fortran CTSM code to JAX. Each agent has a specific role and collaborates through the orchestrator.

## Core Components

### 1. Base Agent (`base_agent.py`)

**Purpose**: Foundation class for all agents

**Key Features**:
- Claude API integration with retry logic
- Conversation history management
- Cost tracking
- Logging and state persistence

**API**:
```python
class BaseAgent:
    def query_claude(prompt: str, system_prompt: str = None) -> str
    def multi_turn_conversation(initial_prompt: str) -> str
    def continue_conversation(prompt: str) -> str
    def get_cost_estimate() -> Dict[str, float]
    def save_state(output_path: Path) -> None
    def reset() -> None
```

**Design Decisions**:
- Uses `tenacity` for automatic retries on API failures
- Tracks token usage for cost management
- Saves all interactions to log files for debugging
- Supports both single-turn and multi-turn conversations

### 2. Static Analysis Agent (`static_analysis.py`)

**Purpose**: Analyze Fortran code structure and extract information

**Responsibilities**:
- Parse Fortran modules
- Extract dependencies (use statements, includes)
- Identify data types and derived types
- Map subroutines and functions
- Detect spatial hierarchy patterns
- Analyze loop structures for vectorization

**Output**: `AnalysisResult` containing:
- Module metadata (name, description)
- Dependencies (modules, includes, external types)
- Data types (fields, descriptions)
- Subroutines (signatures, operations, patterns)
- Spatial hierarchy information
- JAX translation notes

**Example Usage**:
```python
analyzer = StaticAnalysisAgent()
analysis = analyzer.analyze_module(fortran_file)

print(f"Found {len(analysis.subroutines)} subroutines")
print(f"Dependencies: {analysis.dependencies.modules}")
```

### 3. Translator Agent (`translator.py`)

**Purpose**: Convert Fortran code to JAX

**Responsibilities**:
- Convert Fortran syntax to Python/JAX
- Apply JAX patterns (pure functions, immutable state)
- Generate type hints and docstrings
- Create parameter classes
- Vectorize loops
- Handle conditionals with `jnp.where`

**Output**: `TranslationResult` containing:
- Physics module code (main translation)
- Parameters file (if applicable)
- Test file (if generated)
- Translation notes (decisions made)

**Key Patterns Applied**:
1. **Pure Functions**: No side effects, no mutations
2. **Immutable State**: NamedTuples instead of classes
3. **JIT-Compatible**: `jnp.where` instead of Python `if`
4. **Vectorized**: Array operations instead of loops
5. **Type Hints**: Full type annotations
6. **Documentation**: Google-style docstrings with Fortran references

**Example Usage**:
```python
translator = TranslatorAgent(jax_ctsm_dir=jax_dir)
translation = translator.translate_module(fortran_file, analysis)

# Access generated code
print(translation.physics_code)
print(translation.params_code)
```

### 4. Orchestrator Agent (`orchestrator.py`)

**Purpose**: Coordinate the overall conversion workflow

**Responsibilities**:
- Plan conversion strategies
- Coordinate Static Analysis and Translator agents
- Manage dependencies between modules
- Synthesize results
- Generate comprehensive reports
- Track progress and costs

**Workflow**:
```
1. Plan Conversion
   ↓
2. Static Analysis
   ↓
3. Translation
   ↓
4. Synthesis & Reporting
```

**Output**: `ConversionResult` containing:
- Conversion plan
- Analysis results
- Translation results
- Saved file paths
- Cost summary
- Comprehensive report

**Example Usage**:
```python
orchestrator = OrchestratorAgent(ctsm_dir, jax_ctsm_dir)
result = orchestrator.convert_module("CNGRespMod.F90")

# Access all results
print(result.status)
print(result.saved_files)
print(result.cost_summary)
```

## Data Flow

```
┌─────────────────┐
│ Fortran Module  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Orchestrator Agent     │
│  • Creates plan         │
└─────────┬───────────────┘
          │
          ├──────────────────────────────┐
          │                              │
          ▼                              ▼
┌──────────────────────┐    ┌────────────────────────┐
│ Static Analysis      │    │                        │
│ • Parse structure    │    │                        │
│ • Extract patterns   │    │                        │
│ • Identify loops     │    │                        │
└──────────┬───────────┘    │                        │
           │                │                        │
           │ AnalysisResult │                        │
           ├────────────────┤                        │
           │                │                        │
           ▼                ▼                        │
           ┌────────────────────────┐                │
           │  Translator Agent      │                │
           │  • Convert to JAX      │                │
           │  • Apply patterns      │                │
           │  • Generate docs       │                │
           └────────────┬───────────┘                │
                        │                            │
                        │ TranslationResult          │
                        ├────────────────────────────┤
                        │                            │
                        ▼                            ▼
              ┌──────────────────────────────────────┐
              │  Orchestrator Synthesis              │
              │  • Combine results                   │
              │  • Generate report                   │
              │  • Track costs                       │
              └────────────┬─────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ ConversionResult│
                  │ • JAX files     │
                  │ • Reports       │
                  │ • Costs         │
                  └─────────────────┘
```

## Prompt Templates

Each agent uses structured prompts in the `prompts/` directory:

### Analysis Prompts (`analysis_prompts.py`)

- `system`: Sets up the Static Analysis agent role
- `analyze_module`: Main module analysis
- `extract_dependencies`: Dependency extraction
- `identify_physics`: Physics equation extraction
- `analyze_loops`: Loop vectorization analysis

### Translation Prompts (`translation_prompts.py`)

- `system`: Sets up the Translator agent role
- `translate_module`: Full module translation
- `translate_function`: Single function translation
- `convert_data_structure`: Data type conversion
- `vectorize_loop`: Loop vectorization
- `handle_conditional`: Conditional conversion
- `create_parameters`: Parameter class generation

### Orchestrator Prompts (`orchestrator_prompts.py`)

- `system`: Sets up the Orchestrator agent role
- `plan_conversion`: Conversion strategy planning
- `synthesize_results`: Result synthesis
- `manage_dependencies`: Dependency management
- `generate_report`: Report generation

## Error Handling

### Retry Logic
- Uses `tenacity` library for exponential backoff
- Retries up to 3 times on API failures
- Waits 4-10 seconds between retries

### Validation
- Syntax validation of generated Python code
- Type hint checking
- JAX pattern validation (via `utils/validation.py`)

### Logging
- All interactions logged to `logs/` directory
- Separate log file per agent per session
- Includes prompts, responses, and timing

## Cost Management

### Token Tracking
- Tracks input/output tokens per agent
- Aggregates across all agents
- Real-time cost calculation

### Cost Estimation
Based on Claude Sonnet 4.5 pricing:
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

### Example
```python
cost = agent.get_cost_estimate()
# {
#   'input_tokens': 12500,
#   'output_tokens': 3200,
#   'input_cost_usd': 0.0375,
#   'output_cost_usd': 0.048,
#   'total_cost_usd': 0.0855
# }
```

## Extension Points

### Adding New Agents

1. **Inherit from `BaseAgent`**:
```python
from jax_agents.base_agent import BaseAgent

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Validation",
            role="JAX code validator",
        )
```

2. **Add prompts** to `prompts/` directory

3. **Implement specialized methods**:
```python
def validate_against_fortran(self, jax_code, fortran_output):
    # Implementation
    pass
```

4. **Integrate with Orchestrator**:
```python
# In orchestrator.py
self.validator = ValidationAgent()
validation_result = self.validator.validate_against_fortran(...)
```

### Future Agents

Planned extensions:

1. **Validation Agent**
   - Compare JAX output with Fortran
   - Numerical accuracy checks
   - Conservation law validation

2. **Repair Agent**
   - Fix translation errors
   - Optimize generated code
   - Improve type hints

3. **Test Generation Agent**
   - Create comprehensive unit tests
   - Generate validation tests
   - Create integration tests

4. **Documentation Agent**
   - Generate user documentation
   - Create API references
   - Write tutorials

## Configuration

### `config.yaml` Structure

```yaml
llm:
  model: "claude-sonnet-4-20250514"
  temperature: 0.0
  max_tokens: 4000

paths:
  ctsm_root: "../CTSM"
  jax_ctsm_root: "../jax-ctsm"

agents:
  orchestrator:
    enabled: true
  static_analysis:
    enabled: true
  translator:
    enabled: true

jax_patterns:
  use_immutable_state: true
  use_pure_functions: true
  add_type_hints: true
```

## Performance Considerations

### Response Times
- First API call: 1-5 seconds (depending on prompt size)
- Subsequent calls: 1-3 seconds
- Module conversion: 30-120 seconds total

### Token Usage
- Simple module (< 500 lines): ~5,000-15,000 tokens
- Medium module (500-1500 lines): ~15,000-40,000 tokens
- Complex module (> 1500 lines): ~40,000-100,000 tokens

### Optimization Strategies
1. **Chunking**: Break large modules into smaller pieces
2. **Caching**: Cache analysis results for reuse
3. **Parallel Processing**: Process independent modules in parallel
4. **Incremental Updates**: Only re-translate changed code

## Security Considerations

1. **API Key Protection**
   - Store in `.env` file (not in version control)
   - Use environment variables
   - Rotate keys regularly

2. **Code Validation**
   - Always review generated code
   - Run security scans
   - Test thoroughly before deployment

3. **Cost Limits**
   - Set maximum cost per module in config
   - Monitor token usage
   - Alert on unusual patterns

## Testing Strategy

### Unit Tests
- Test individual agent methods
- Mock Claude API responses
- Validate data structures

### Integration Tests
- Test full conversion workflow
- Verify agent coordination
- Check output files

### Validation Tests
- Compare with known good translations
- Verify JAX patterns
- Check cost estimates

## Deployment

### Development
```bash
pip install -e .  # Editable install
```

### Production
```bash
pip install .  # Standard install
```

### Docker (future)
```dockerfile
FROM python:3.11
COPY . /app
RUN pip install /app
CMD ["python", "-m", "jax_agents.cli"]
```

## Monitoring & Debugging

### Logs
- Location: `logs/` directory
- Format: `{agent_name}_{timestamp}.log`
- Contents: Prompts, responses, errors

### Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check agent state
agent.save_state("debug_state.json")

# Review conversation history
print(agent.conversation_history)
```

## Best Practices

1. **Start Simple**: Test with small modules first
2. **Review Output**: Always inspect generated code
3. **Validate Results**: Compare with Fortran behavior
4. **Track Costs**: Monitor token usage
5. **Iterate**: Refine prompts based on results
6. **Document**: Keep notes on conversion decisions

## References

- **JAX Documentation**: https://jax.readthedocs.io/
- **Anthropic API**: https://docs.anthropic.com/
- **CTSM Documentation**: https://escomp.github.io/ctsm-docs/
- **JAX-CTSM Examples**: `../jax-ctsm/`

---

Last Updated: October 2025

