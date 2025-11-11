# Quick Start: Repair Agent

## 🎉 What's New

A new **Repair Agent** has been added to the JAX-CTSM translation system! It automatically debugs and fixes failed Python/JAX translations.

## 🚀 Quick Start

### 1. Basic Usage

```python
from pathlib import Path
from jax_agents import RepairAgent

# Initialize agent
repair_agent = RepairAgent(max_repair_iterations=5)

# Repair a failed translation
result = repair_agent.repair_translation(
    module_name="SoilTemperatureMod",
    fortran_code=your_fortran_code,
    failed_python_code=your_failed_code,
    test_report=your_test_output,
    test_file_path=Path("tests/test_module.py"),  # Optional
    output_dir=Path("repair_outputs"),
)

# Check results
print(f"Tests passed: {result.all_tests_passed}")
print(f"Iterations: {result.iterations}")
```

### 2. Run the Example

```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/repair_agent_example.py
```

### 3. Complete Workflow

```bash
# Translate Fortran → Python/JAX
python examples/translate_with_context.py

# Generate tests
python examples/generate_tests.py

# Run tests
pytest output/test_ModuleName.py -v

# If tests fail, repair automatically
python examples/repair_agent_example.py

# Verify fix
pytest output/test_ModuleName.py -v
```

## 📦 What Was Created

### Core Files
- ✅ `src/jax_agents/repair_agent.py` - Main agent implementation
- ✅ `src/jax_agents/prompts/repair_prompts.py` - Prompt templates
- ✅ `examples/repair_agent_example.py` - Usage example

### Documentation
- ✅ `docs/repair_agent.md` - Comprehensive documentation
- ✅ `docs/repair_agent_workflow.md` - Workflow diagrams
- ✅ `REPAIR_AGENT_SUMMARY.md` - Implementation summary
- ✅ `README.md` - Updated with Repair Agent section
- ✅ `examples/README.md` - Updated with examples

### Integration
- ✅ Updated `src/jax_agents/__init__.py` to export `RepairAgent` and `RepairResult`

## 🔧 Key Features

### 1. Automatic Root Cause Analysis
Identifies why translations failed by comparing with Fortran code:
- Array indexing issues (1-based vs 0-based)
- Type mismatches
- In-place operations (not JAX-compatible)
- Logic errors
- Shape mismatches

### 2. Iterative Repair
- Generates fix based on analysis
- Runs tests automatically (if pytest file provided)
- If tests still fail, re-analyzes and iterates
- Continues until tests pass or max iterations reached

### 3. Comprehensive Reporting
Generates detailed reports including:
- Failure analysis (JSON)
- Corrected Python code
- Root cause analysis (markdown)
- Test results

## 📊 Workflow

```
Fortran Code + Failed Python + Test Report
                 │
                 ▼
        ┌────────────────┐
        │ Analyze Failure│
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Generate Fix   │
        └────────┬───────┘
                 │
                 ▼
        ┌────────────────┐
        │ Run Tests      │
        └────────┬───────┘
                 │
            ┌────┴────┐
           Pass      Fail
            │          │
            │     ┌────▼────┐
            │     │ Iterate │
            │     └────┬────┘
            │          │
            │          └──→ Back to Analyze
            │
            ▼
     ┌──────────────┐
     │ Generate RCA │
     └──────────────┘
            │
            ▼
        Success!
```

## 🎯 Use Cases

### Use Case 1: Simple Bug Fix
```python
# You have a failed translation with test failures
repair_agent = RepairAgent()
result = repair_agent.repair_translation(
    module_name="SimpleModule",
    fortran_code=fortran,
    failed_python_code=failed_python,
    test_report=pytest_output,
)
# Usually fixes in 1-2 iterations
```

### Use Case 2: Complex Bug with Iteration
```python
# More complex issue requiring multiple iterations
repair_agent = RepairAgent(max_repair_iterations=10)
result = repair_agent.repair_translation(
    module_name="ComplexModule",
    fortran_code=fortran,
    failed_python_code=failed_python,
    test_report=initial_test_report,
    test_file_path=Path("tests/test_ComplexModule.py"),
)
# Automatically runs tests and iterates until fixed
```

### Use Case 3: Understanding Failures
```python
# Even if you don't want automatic fixing,
# you can use the agent to understand what went wrong
result = repair_agent.repair_translation(
    module_name="MyModule",
    fortran_code=fortran,
    failed_python_code=failed_python,
    test_report=test_report,
    test_file_path=None,  # Don't run tests
)
# Read the root cause analysis to understand the issue
print(result.root_cause_analysis)
```

## 📋 Output Files

When you provide `output_dir`, the agent saves:

```
repair_outputs/
├── ModuleName_corrected.py              # ✅ Fixed code
├── root_cause_analysis_ModuleName.md    # 📝 Detailed RCA
├── failure_analysis_ModuleName.json     # 📊 Structured data
└── final_test_report_ModuleName.txt     # 🧪 Test results
```

## 💰 Cost Estimation

Track costs:
```python
result = repair_agent.repair_translation(...)
cost = repair_agent.get_cost_estimate()
print(f"Total: ${cost['total_cost_usd']:.4f}")
```

Typical costs:
- Simple fix (1-2 iterations): ~$0.10 - $0.30
- Medium (3-5 iterations): ~$0.30 - $0.80
- Complex (5-10 iterations): ~$0.80 - $2.00

## 📚 Documentation

Full documentation available at:
- `docs/repair_agent.md` - Complete guide
- `docs/repair_agent_workflow.md` - Visual workflows
- `REPAIR_AGENT_SUMMARY.md` - Implementation details

## 🔍 Example: Fixing an Indexing Bug

```python
# Fortran code (1-based indexing)
fortran_code = """
subroutine process_array(arr, n)
    real(r8), intent(inout) :: arr(n)
    integer :: i
    do i = 1, n
        arr(i) = arr(i) * 2.0
    end do
end subroutine
"""

# Failed Python translation (bug: starts at 1 instead of 0)
failed_python = """
def process_array(arr):
    for i in range(1, len(arr)):  # BUG!
        arr = arr.at[i].set(arr[i] * 2.0)
    return arr
"""

# Test report
test_report = """
test_process_array FAILED
AssertionError: First element not processed
Expected: [2.0, 4.0, 6.0]
Got:      [1.0, 4.0, 6.0]
"""

# Repair automatically
repair_agent = RepairAgent()
result = repair_agent.repair_translation(
    module_name="ArrayProcessor",
    fortran_code=fortran_code,
    failed_python_code=failed_python,
    test_report=test_report,
)

# Corrected code:
# for i in range(len(arr)):  # FIXED!
#     arr = arr.at[i].set(arr[i] * 2.0)
```

## 🤝 Integration with Other Agents

```python
from jax_agents import (
    TranslatorAgent,
    TestAgent,
    RepairAgent,
)

# 1. Translate
translator = TranslatorAgent()
translation = translator.translate_module("SoilTemp")

# 2. Generate tests
test_agent = TestAgent()
tests = test_agent.generate_tests("SoilTemp", translation.code)

# 3. If tests fail, repair
repair_agent = RepairAgent()
repair = repair_agent.repair_translation(
    module_name="SoilTemp",
    fortran_code=fortran_source,
    failed_python_code=translation.code,
    test_report=pytest_output,
)
```

## 🎓 Best Practices

1. **Provide Good Tests**: The better your tests, the better the repair
2. **Include Full Error Messages**: Include stack traces in test reports
3. **Set Appropriate Iterations**: 
   - Simple issues: 3-5 iterations
   - Complex issues: 10+ iterations
4. **Review Fixes**: Always review corrected code before production
5. **Save RCA Reports**: Keep for future reference and learning

## 🐛 Troubleshooting

### Issue: Tests still fail after max iterations
**Solution**: Increase `max_repair_iterations` or review the RCA report

### Issue: Agent makes unrelated changes
**Solution**: Provide more specific test cases and error messages

### Issue: Can't run tests automatically
**Solution**: Ensure pytest file path is correct and pytest is installed

## ✅ Verification

Check that everything is working:

```bash
# 1. Check files exist
ls -la src/jax_agents/repair_agent.py
ls -la src/jax_agents/prompts/repair_prompts.py
ls -la examples/repair_agent_example.py

# 2. Verify syntax
python -m py_compile src/jax_agents/repair_agent.py
python -m py_compile src/jax_agents/prompts/repair_prompts.py

# 3. Run example (if dependencies installed)
python examples/repair_agent_example.py
```

## 🚀 Next Steps

1. Try the example: `python examples/repair_agent_example.py`
2. Read full docs: `docs/repair_agent.md`
3. Integrate into your workflow
4. Report any issues or feedback

## 📞 Support

For issues or questions:
- Check `docs/repair_agent.md` for detailed documentation
- Review `REPAIR_AGENT_SUMMARY.md` for implementation details
- See `docs/repair_agent_workflow.md` for visual workflows

---

**The Repair Agent is ready to use!** 🎉

It completes the translation pipeline with automated debugging and fixing capabilities, saving time and improving code quality.

