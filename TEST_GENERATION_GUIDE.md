# Test Generation Guide

The Test Agent automatically generates comprehensive pytest files and test data for your Python/JAX translations.

## Quick Start

### Generate tests for a module:

```bash
cd examples
./generate_tests.py --module SoilTemperatureMod \
  --python ../translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --output ../translated_modules/SoilTemperatureMod/tests
```

### Generate for all modules:

```bash
./generate_tests.py --all
```

### Interactive mode:

```bash
./generate_tests.py --interactive
```

## What Gets Generated

For each module, you get:

1. **`test_<module>.py`** - Comprehensive pytest file with:
   - Fixtures for test data
   - Parametrized tests
   - Shape, value, and edge case tests
   - Clear assertions and error messages

2. **`test_data_<module>.json`** - Synthetic test data covering:
   - Nominal/typical cases (50%)
   - Edge cases (30%): zeros, negatives, boundaries
   - Special cases (20%): different array sizes, extreme conditions

3. **`test_documentation_<module>.md`** - Documentation explaining:
   - How to run tests
   - What each test does
   - How to extend tests

## Usage Examples

### Python API

```python
from jax_agents import TestAgent
from pathlib import Path

# Initialize
test_agent = TestAgent()

# Read Python code
with open("my_module.py") as f:
    python_code = f.read()

# Generate tests
result = test_agent.generate_tests(
    module_name="MyModule",
    python_code=python_code,
    output_dir=Path("tests"),
    num_test_cases=10,
    include_edge_cases=True,
    include_performance_tests=False,
)

print(f"Generated: {result.pytest_file}")
```

### Command Line

```bash
# Basic
python examples/generate_tests.py \
  --module MyModule \
  --python ./MyModule.py \
  --output ./tests

# With more test cases
python examples/generate_tests.py \
  --module MyModule \
  --python ./MyModule.py \
  --output ./tests \
  --num-cases 20
```

## Generated Test Structure

```python
"""Tests for SoilTemperatureMod"""
import pytest
import jax.numpy as jnp
from soil_temperature_mod import soil_temperature

@pytest.fixture
def test_data():
    """Load test data from JSON file."""
    with open("test_data_SoilTemperatureMod.json") as f:
        return json.load(f)

def test_soil_temperature_shapes(test_data):
    """Test output shapes match expected dimensions."""
    for case in test_data["test_cases"]:
        result = soil_temperature(**case["inputs"])
        assert result.shape == (n_columns, n_levels)

def test_soil_temperature_values(test_data):
    """Test output values are physically reasonable."""
    for case in test_data["test_cases"]:
        result = soil_temperature(**case["inputs"])
        # Temperature should be positive Kelvin
        assert jnp.all(result > 0)
        assert jnp.all(result < 400)  # < 127°C

@pytest.mark.parametrize("test_case", test_data["test_cases"])
def test_soil_temperature_edge_cases(test_case):
    """Test edge cases like zero flux, boundary conditions."""
    result = soil_temperature(**test_case["inputs"])
    # Assertions based on test case metadata
    ...
```

## Test Data Format

```json
{
  "function_name": "soil_temperature",
  "test_cases": [
    {
      "name": "nominal_conditions",
      "inputs": {
        "t_soisno": [[283.15, 283.0, 282.5]],
        "dtime": 1800.0,
        "gsoi": [50.0]
      },
      "metadata": {
        "type": "nominal",
        "description": "Typical soil temperature conditions",
        "edge_cases": []
      }
    },
    {
      "name": "zero_heat_flux",
      "inputs": {
        "t_soisno": [[273.15, 273.15, 273.15]],
        "dtime": 1800.0,
        "gsoi": [0.0]
      },
      "metadata": {
        "type": "edge",
        "description": "No heat flux boundary condition",
        "edge_cases": ["zero_flux"]
      }
    }
  ]
}
```

## Running Tests

```bash
# Basic run
cd tests
pytest test_SoilTemperatureMod.py

# Verbose output
pytest test_SoilTemperatureMod.py -v

# With coverage
pytest test_SoilTemperatureMod.py --cov=SoilTemperatureMod

# Specific test
pytest test_SoilTemperatureMod.py::test_soil_temperature_shapes

# Stop on first failure
pytest test_SoilTemperatureMod.py -x
```

## Test Types

### 1. Shape Tests
Verify output arrays have correct dimensions:
```python
def test_shapes(test_data):
    result = my_function(**test_data["test_cases"][0]["inputs"])
    assert result.shape == (n_columns, n_levels)
```

### 2. Value Tests
Check outputs are physically reasonable:
```python
def test_values(test_data):
    result = my_function(**test_data["test_cases"][0]["inputs"])
    assert jnp.all(result > 0)  # Temperatures positive
    assert jnp.all(result < 400)  # Reasonable range
```

### 3. Edge Case Tests
Test boundary conditions:
```python
def test_edge_cases(test_data):
    # Zero input
    result = my_function(input_array=jnp.zeros((10,)))
    assert jnp.allclose(result, expected_zero_output)
    
    # Negative (if valid)
    result = my_function(input_array=-jnp.ones((10,)))
    # ...
```

### 4. Type Tests
Verify data types:
```python
def test_dtypes(test_data):
    result = my_function(**test_data["test_cases"][0]["inputs"])
    assert result.dtype == jnp.float64
```

## Customization

### Add More Test Cases

Edit `test_data_<module>.json`:
```json
{
  "test_cases": [
    ...existing cases...,
    {
      "name": "my_custom_test",
      "inputs": {
        "param1": [...],
        "param2": [...]
      },
      "metadata": {
        "type": "special",
        "description": "Tests specific scenario"
      }
    }
  ]
}
```

### Modify Tolerances

Edit generated pytest file:
```python
# Change from default
assert jnp.allclose(result, expected, atol=1e-6, rtol=1e-6)

# To custom
assert jnp.allclose(result, expected, atol=1e-4, rtol=1e-5)
```

### Add Performance Tests

Regenerate with performance flag:
```python
result = test_agent.generate_tests(
    ...,
    include_performance_tests=True,
)
```

This adds timing tests:
```python
def test_performance(benchmark, test_data):
    """Benchmark function performance."""
    result = benchmark(my_function, **test_data["test_cases"][0]["inputs"])
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest translated_modules/*/tests/test_*.py -v
```

## Common Issues

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**: Add module to PYTHONPATH or install:
```bash
export PYTHONPATH=/path/to/jax-ctsm/src:$PYTHONPATH
# or
pip install -e /path/to/jax-ctsm
```

### Shape Mismatches

**Problem**: `AssertionError: arrays have different shapes`

**Solution**: Check array dimensions in test data match function expectations

### Numerical Precision

**Problem**: Small differences in floating-point results

**Solution**: Adjust tolerances:
```python
assert jnp.allclose(result, expected, atol=1e-5, rtol=1e-5)
```

## Best Practices

1. ✅ **Generate tests early** - Create tests as soon as translation is done
2. ✅ **Review test data** - Check generated data makes physical sense
3. ✅ **Add custom cases** - Extend with domain-specific test scenarios
4. ✅ **Run regularly** - Integrate into development workflow
5. ✅ **Update tests** - When code changes, regenerate or update tests
6. ✅ **Document assumptions** - Note any constraints or assumptions in tests
7. ✅ **Version control** - Commit tests alongside code

## Advanced Usage

### Custom Test Data Generator

```python
# Create custom test data
custom_data = {
    "function_name": "my_function",
    "test_cases": [
        {
            "name": "winter_conditions",
            "inputs": {
                "temperature": [[250.0, 251.0, 252.0]],
                "time_step": 1800.0
            },
            "metadata": {
                "type": "special",
                "description": "Cold winter scenario"
            }
        }
    ]
}

# Save to JSON
with open("test_data_custom.json", "w") as f:
    json.dump(custom_data, f, indent=2)
```

### Parametrize Tests

```python
@pytest.mark.parametrize("case_name,inputs,expected", [
    ("nominal", {...}, {...}),
    ("edge_zero", {...}, {...}),
    ("edge_negative", {...}, {...}),
])
def test_parametrized(case_name, inputs, expected):
    result = my_function(**inputs)
    assert jnp.allclose(result, expected)
```

## API Reference

### TestAgent

```python
class TestAgent:
    def generate_tests(
        self,
        module_name: str,
        python_code: str,
        output_dir: Optional[Path] = None,
        num_test_cases: int = 10,
        include_edge_cases: bool = True,
        include_performance_tests: bool = False,
    ) -> TestGenerationResult
```

### TestGenerationResult

```python
@dataclass
class TestGenerationResult:
    module_name: str
    pytest_file: str
    test_data_file: str
    test_documentation: str
    
    def save(self, output_dir: Path) -> Dict[str, Path]
```

## Getting Help

- Check generated `test_documentation_<module>.md` for module-specific info
- Run tests with `-v` flag for detailed output
- Use pytest `--pdb` to drop into debugger on failures

## Cost

Test generation costs approximately:
- $0.01-0.05 per module (depending on complexity)
- Uses Claude Sonnet 4.5 via Anthropic API
- Costs tracked automatically and displayed after generation

