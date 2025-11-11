# Repair Agent Documentation

## Overview

The **Repair Agent** is a specialized agent in the JAX-CTSM translation system that automatically debugs and fixes failed Python/JAX translations. It analyzes test failures, identifies root causes, generates corrected code, and iteratively refines the solution until tests pass.

## Key Features

- **Automatic Root Cause Analysis**: Analyzes test failures and error messages to identify the underlying issues
- **Iterative Repair**: Automatically runs tests and refines fixes until they pass
- **Comprehensive Reporting**: Generates detailed root cause analysis reports
- **Fortran-Aware**: Compares Python code with original Fortran to ensure semantic correctness
- **JAX-Compatible**: Ensures all fixes maintain JAX compatibility (pure functions, immutability, JIT-compatibility)

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Repair Agent Workflow                     │
└─────────────────────────────────────────────────────────────┘

Input:
  1. Original Fortran code
  2. Failed Python translation
  3. Test report (failures, error messages)
  4. (Optional) pytest file path

Step 1: Failure Analysis
  - Identify failed tests
  - Extract error messages
  - Compare Python vs Fortran semantics
  - Identify root causes
  
Step 2: Generate Fix
  - Create corrected Python code
  - Address all identified issues
  - Maintain JAX compatibility
  
Step 3: Verify & Test (if pytest file provided)
  - Run tests with corrected code
  - Capture new test results
  
Step 4: Iterate (if tests still fail)
  - Re-analyze with new test results
  - Generate improved fix
  - Repeat until tests pass or max iterations
  
Output:
  1. Corrected Python code
  2. Root cause analysis report (markdown)
  3. Failure analysis (JSON)
  4. Final test report
```

## Installation

The Repair Agent is included in the `jax-agents` package:

```python
from jax_agents import RepairAgent, RepairResult
```

## Basic Usage

```python
from pathlib import Path
from jax_agents import RepairAgent

# Initialize agent
repair_agent = RepairAgent(
    max_repair_iterations=5,  # Maximum repair attempts
    model="claude-sonnet-4-5",  # Optional: specify model
    temperature=0.0,  # Optional: set temperature
)

# Repair a failed translation
result = repair_agent.repair_translation(
    module_name="SoilTemperatureMod",
    fortran_code=fortran_code_string,
    failed_python_code=failed_python_string,
    test_report=test_report_string,
    test_file_path=Path("tests/test_module.py"),  # Optional
    output_dir=Path("repair_outputs"),  # Optional
)

# Access results
print(f"Iterations: {result.iterations}")
print(f"Tests passed: {result.all_tests_passed}")
print(f"Corrected code:\n{result.corrected_python_code}")
print(f"Root cause analysis:\n{result.root_cause_analysis}")
```

## Input Requirements

### 1. Fortran Code
The original Fortran subroutine/function that was translated to Python.

```fortran
subroutine calculate_something(input, output, n)
    implicit none
    integer, intent(in) :: n
    real(r8), intent(in) :: input(n)
    real(r8), intent(out) :: output(n)
    ! ... implementation
end subroutine
```

### 2. Failed Python Code
The Python/JAX translation that failed tests.

```python
import jax.numpy as jnp
from jax import jit

@jit
def calculate_something(input_array):
    # ... implementation with bugs
    return output_array
```

### 3. Test Report
Test results showing failures, typically from pytest output.

```
============================= test session starts ==============================
test_module.py::test_basic FAILED                                        [ 33%]
test_module.py::test_edge_case FAILED                                    [ 66%]
test_module.py::test_performance PASSED                                  [100%]

=================================== FAILURES ===================================
______________________________ test_basic _______________________________
...
```

### 4. Test File Path (Optional)
Path to the pytest file. If provided, the agent will automatically run tests after each fix.

```python
test_file_path = Path("tests/test_SoilTemperatureMod.py")
```

## Output Structure

The `RepairResult` object contains:

| Field | Type | Description |
|-------|------|-------------|
| `module_name` | `str` | Name of the repaired module |
| `original_python_code` | `str` | Original failed Python code |
| `corrected_python_code` | `str` | Fixed Python code |
| `root_cause_analysis` | `str` | Comprehensive RCA report (markdown) |
| `failure_analysis` | `Dict` | JSON structure with root causes |
| `iterations` | `int` | Number of repair iterations |
| `final_test_report` | `str` | Final test results |
| `all_tests_passed` | `bool` | Whether all tests passed |

## Saving Results

Results are automatically saved if `output_dir` is provided:

```python
result = repair_agent.repair_translation(
    # ... inputs ...
    output_dir=Path("repair_outputs"),
)

# Saves:
# - repair_outputs/SoilTemperatureMod_corrected.py
# - repair_outputs/root_cause_analysis_SoilTemperatureMod.md
# - repair_outputs/failure_analysis_SoilTemperatureMod.json
# - repair_outputs/final_test_report_SoilTemperatureMod.txt
```

## Advanced Usage

### Custom Configuration

```python
repair_agent = RepairAgent(
    model="claude-sonnet-4-5",
    temperature=0.0,
    max_tokens=32000,
    max_repair_iterations=10,  # More iterations for complex issues
)
```

### Without Automatic Testing

If you don't have a pytest file or want to manually verify fixes:

```python
result = repair_agent.repair_translation(
    module_name="MyModule",
    fortran_code=fortran_code,
    failed_python_code=python_code,
    test_report=test_report,
    test_file_path=None,  # Skip automatic test execution
    output_dir=Path("outputs"),
)

# The agent will generate one fix based on the test report
# You can then manually test and re-run if needed
```

### Integration with Test Agent

Use the Test Agent to generate tests, then the Repair Agent to fix failures:

```python
from jax_agents import TestAgent, RepairAgent

# Step 1: Generate tests
test_agent = TestAgent()
test_result = test_agent.generate_tests(
    module_name="SoilTemp",
    python_code=initial_python_code,
    output_dir=Path("tests"),
)

# Step 2: Run tests (outside agent)
# Run pytest and capture failures...

# Step 3: If tests fail, repair
if tests_failed:
    repair_agent = RepairAgent()
    repair_result = repair_agent.repair_translation(
        module_name="SoilTemp",
        fortran_code=original_fortran,
        failed_python_code=initial_python_code,
        test_report=pytest_output,
        test_file_path=Path("tests/test_SoilTemp.py"),
        output_dir=Path("repairs"),
    )
```

## Root Cause Analysis Report

The agent generates a comprehensive markdown report including:

1. **Executive Summary**
   - Overview of the issue
   - Impact assessment
   - Severity classification

2. **Failure Analysis**
   - Which tests failed
   - Error messages and symptoms
   - Failure patterns

3. **Root Cause Identification**
   - Detailed analysis of each issue
   - Why the translation was incorrect
   - Comparison with Fortran semantics
   - Code differences highlighted

4. **Fix Implementation**
   - What changes were made
   - Why these changes resolve the issues
   - Before/after code snippets

5. **Test Results**
   - Test results after each iteration
   - Verification that issues are resolved

6. **Lessons Learned**
   - Key takeaways for future translations
   - Common pitfalls identified
   - Recommendations

## Common Issues Detected

The Repair Agent can identify and fix various issues:

### Array Indexing
- **Issue**: Fortran uses 1-based indexing, Python uses 0-based
- **Detection**: Boundary tests failing, off-by-one errors
- **Fix**: Adjust loop ranges and array accesses

### Type Mismatches
- **Issue**: Integer vs float operations
- **Detection**: Type errors, precision loss
- **Fix**: Explicit type conversions, proper JAX dtypes

### In-Place Operations
- **Issue**: Python code uses in-place modifications (not JAX-compatible)
- **Detection**: JIT compilation errors
- **Fix**: Use immutable operations (`.at[].set()`)

### Logic Errors
- **Issue**: Incorrect translation of Fortran logic
- **Detection**: Incorrect outputs, failing assertions
- **Fix**: Correct logic to match Fortran semantics

### Shape Mismatches
- **Issue**: Array dimensions don't match
- **Detection**: Shape errors, broadcasting issues
- **Fix**: Reshape operations, correct dimension handling

## Limitations

1. **Test Dependency**: Quality of repairs depends on quality of tests and test reports
2. **Iteration Limit**: May not fix all issues if max iterations is too low
3. **Complex Bugs**: Some issues may require human intervention
4. **Runtime Errors**: Works best with clear error messages; harder with silent failures

## Best Practices

1. **Provide Good Test Coverage**: More comprehensive tests lead to better repairs
2. **Clear Error Messages**: Include full stack traces and assertions in test reports
3. **Set Appropriate Iterations**: Use 3-5 iterations for simple issues, 10+ for complex ones
4. **Review Fixes**: Always review the corrected code before using in production
5. **Iterate if Needed**: If initial repair fails, try running again with updated test report

## Cost Estimation

Track API usage costs:

```python
result = repair_agent.repair_translation(...)

cost_info = repair_agent.get_cost_estimate()
print(f"Total cost: ${cost_info['total_cost_usd']:.4f}")
print(f"Input tokens: {cost_info['input_tokens']:,}")
print(f"Output tokens: {cost_info['output_tokens']:,}")
```

## Logging

The agent logs all interactions to `logs/`:

```
logs/
  repairagent_20250111_143025.log
  repairagent_20250111_143127.log
```

## Examples

See `examples/repair_agent_example.py` for complete working examples.

## Troubleshooting

### Issue: Agent can't parse test report
**Solution**: Ensure test report is complete and includes error messages. Use `pytest -v --tb=short` for best results.

### Issue: Tests still fail after max iterations
**Solution**: 
- Increase `max_repair_iterations`
- Review the root cause analysis to understand the issue
- Manually review the code
- Ensure test report is accurate

### Issue: Agent makes changes to unrelated code
**Solution**: The agent tries to fix only relevant code, but if test reports are ambiguous, it may make broader changes. Provide more specific test cases.

### Issue: Fixed code is not JAX-compatible
**Solution**: The agent is trained to maintain JAX compatibility, but review the corrected code. Report issues if this persists.

## API Reference

### RepairAgent Class

```python
class RepairAgent(BaseAgent):
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_repair_iterations: int = 5,
    )
```

### repair_translation Method

```python
def repair_translation(
    self,
    module_name: str,
    fortran_code: str,
    failed_python_code: str,
    test_report: str,
    test_file_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> RepairResult
```

### RepairResult Class

```python
@dataclass
class RepairResult:
    module_name: str
    original_python_code: str
    corrected_python_code: str
    root_cause_analysis: str
    failure_analysis: Dict[str, Any]
    iterations: int
    final_test_report: str
    all_tests_passed: bool
    
    def save(self, output_dir: Path) -> Dict[str, Path]
```

## See Also

- [Test Agent Documentation](test_agent.md)
- [Translator Agent Documentation](translator.md)
- [Orchestrator Documentation](orchestrator.md)

