# Test Agent - Simplified for Python/JAX Only

## What Changed

The Test Agent has been **completely redesigned** to focus **only on generating tests for Python/JAX code**. 

We removed all Fortran compilation and validation logic to avoid the complexity of dealing with CTSM's interdependent modules.

## New Approach

### ✅ What It Does Now

1. **Analyzes Python/JAX functions** - Extracts signatures, types, shapes
2. **Generates comprehensive test data** - Covering nominal, edge, and special cases  
3. **Creates pytest files** - With fixtures, parametrized tests, and good assertions
4. **Provides documentation** - Explains how to run and extend tests

### ❌ What It No Longer Does

- ~~Compiles Fortran code~~
- ~~Runs Fortran implementations~~
- ~~Compares Fortran vs Python outputs~~
- ~~Generates Fortran test harnesses~~

## Why This Is Better

1. **No dependency issues** - Avoid CTSM module interdependencies
2. **Simpler workflow** - Just Python → tests
3. **Faster** - No Fortran compilation
4. **More practical** - Focus on what you actually need

## Quick Start

```bash
# Generate tests for a module
cd examples
./generate_tests.py \
  --module SoilTemperatureMod \
  --python ../translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --output ../translated_modules/SoilTemperatureMod/tests

# Run the generated tests
cd ../translated_modules/SoilTemperatureMod/tests
pytest test_SoilTemperatureMod.py -v
```

## What You Get

Three files per module:

1. **test_<module>.py** - Pytest file with comprehensive tests
2. **test_data_<module>.json** - Synthetic test data (10+ cases)
3. **test_documentation_<module>.md** - How to run and extend

## Validation Strategy

Instead of validating against Fortran during testing, we recommend:

### Option 1: Reference Data (Recommended)
- Run CTSM once on test cases
- Save outputs
- Compare Python against saved CTSM outputs
- This is what CLM does for their tests

### Option 2: Property-Based Testing
- Test mathematical properties (conservation laws, monotonicity, etc.)
- Test physical constraints (temps > 0K, valid ranges)
- Test consistency (reversibility, symmetry)

### Option 3: Integration Tests
- Test full workflows
- Compare end-to-end results with known good outputs
- This catches system-level issues

## Documentation

See **[TEST_GENERATION_GUIDE.md](TEST_GENERATION_GUIDE.md)** for:
- Complete usage examples
- Test data format
- Customization options
- CI/CD integration
- Troubleshooting

## Files

### Core Implementation
- `src/jax_agents/test_agent.py` - Main Test Agent (simplified)
- `src/jax_agents/prompts/test_prompts_simplified.py` - LLM prompts

### Example Script
- `examples/generate_tests.py` - Command-line tool

### Documentation
- `TEST_GENERATION_GUIDE.md` - Complete guide

### Removed
- ❌ `src/jax_agents/utils/fortran_runner.py` - Not needed anymore
- ❌ `src/jax_agents/utils/comparison.py` - Not needed anymore  
- ❌ Old test_translation.py script
- ❌ Old Fortran-focused documentation

## Example Usage

```python
from jax_agents import TestAgent
from pathlib import Path

# Initialize
test_agent = TestAgent()

# Read Python code
with open("SoilTemperatureMod.py") as f:
    python_code = f.read()

# Generate tests
result = test_agent.generate_tests(
    module_name="SoilTemperatureMod",
    python_code=python_code,
    output_dir=Path("tests"),
    num_test_cases=10,
    include_edge_cases=True,
)

# Tests are ready to run!
# cd tests && pytest test_SoilTemperatureMod.py -v
```

## Cost

Much cheaper than before (no long Fortran harness generation):
- ~$0.01-0.05 per module
- Completes in ~30 seconds

## Migration

If you were using the old Test Agent:

**Old way (complex):**
```python
test_agent.generate_tests(
    fortran_code=fortran_code,  # ← Not needed anymore
    python_code=python_code,
    fortran_file=fortran_file,  # ← Not needed anymore
)
```

**New way (simple):**
```python
test_agent.generate_tests(
    python_code=python_code,  # Just this!
)
```

## Next Steps

1. Generate tests for your modules: `./generate_tests.py --all`
2. Run the tests: `pytest translated_modules/*/tests/test_*.py`
3. Review and customize as needed
4. Add to CI/CD pipeline

## Questions?

See [TEST_GENERATION_GUIDE.md](TEST_GENERATION_GUIDE.md) for detailed documentation.

