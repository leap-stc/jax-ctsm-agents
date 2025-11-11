# Complete Commands to Run Each Example

## Prerequisites

```bash
# Set up environment
cd /burg-archive/home/mck2199/jax-agents
export PYTHONPATH="/burg-archive/home/mck2199/jax-agents/src:$PYTHONPATH"

# Ensure API key is set
export ANTHROPIC_API_KEY="your-key-here"  # Replace with your actual key
```

---

## 1. analyze_module.py
**Analyzes a Fortran module structure without translation**

```bash
# Run with default module (CNMRespMod - Maintenance Respiration)
python examples/analyze_module.py
```

**Module Used:** `CNMRespMod.F90` (from CTSM biogeochem)

**Output:**
- `analysis_result.json` - Can be used with translate_from_analysis.py

**What It Does:**
- Analyzes module structure, subroutines, dependencies
- Shows translation challenges
- Saves complete analysis for later use

---

## 2. translate_from_analysis.py
**Translates using pre-saved analysis**

```bash
# Step 1: First run analyze_module.py
python examples/analyze_module.py

# Step 2: Then translate from the saved analysis
python examples/translate_from_analysis.py
```

**Module Used:** `CNMRespMod.F90` (Maintenance Respiration)

**Prerequisites:** 
- Must run `analyze_module.py` first to create `analysis_result.json`

**Output:**
- `output/CNMRespMod.py` - Physics module
- `output/CNMRespMod_params.py` - Parameters (if any)
- `output/CNMRespMod_translation_notes.md` - Translation notes

---

## 3. translate_with_context.py
**Two-step conversion (analyze + translate) in one script**

```bash
# Runs analysis and translation together
python examples/translate_with_context.py
```

**Module Used:** `CNGRespMod.F90` (Growth Respiration)

**Output:**
- `output/analysis.json` - Analysis results
- `output/CNGRespMod.py` - Physics module
- `output/CNGRespMod_params.py` - Parameters
- `output/CNGRespMod_translation_notes.md` - Notes

---

## 4. convert_single_module.py
**Full orchestrated conversion with comprehensive report**

```bash
# Orchestrator manages everything
python examples/convert_single_module.py
```

**Module Used:** `CNGRespMod.F90` (Growth Respiration)

**Output:**
- Complete module in `jax-ctsm/src/jax_ctsm/physics/`
- Comprehensive conversion report

---

## 5. batch_conversion.py
**Convert multiple modules in sequence**

```bash
# Converts 2 biogeochemistry modules
python examples/batch_conversion.py
```

**Modules Used:**
1. `CNGRespMod.F90` (Growth Respiration - simple)
2. `CNAllocationMod.F90` (Allocation - medium complexity)

**Note:** You can uncomment more modules in the script to translate additional ones.

**Output:**
- Multiple translated modules
- Progress tracking
- Total cost summary

---

## 6. translate_with_json.py
**Translate using static analysis JSON files**

```bash
# Translates 3 modules of different complexity
python examples/translate_with_json.py
```

**Modules Used:**
1. `clm_varctl` - Simple module (low complexity)
2. `SoilStateType` - Medium complexity
3. `SoilTemperatureMod` - High complexity (physics module)

**Prerequisites:**
- `static_analysis_output/analysis_results.json`
- `static_analysis_output/translation_units.json`

**Output:**
- `translated_modules/clm_varctl/clm_varctl.py`
- `translated_modules/SoilStateType/SoilStateType.py`
- `translated_modules/SoilTemperatureMod/SoilTemperatureMod.py`

---

## 7. batch_translate_modules.py
**Batch translate ALL modules from JSON analysis**

```bash
# Translates all modules in dependency order
python examples/batch_translate_modules.py
```

**Modules Used:** ALL modules from `analysis_results.json` (120+ translation units)

**Prerequisites:**
- `static_analysis_output/analysis_results.json`
- `static_analysis_output/translation_units.json`

**Configuration Options** (edit the script to change):
```python
# In main() function:
skip_existing=True,   # Change to False to re-translate
max_modules=None,     # Set to 5 for testing first 5 modules
```

**Output:**
- All modules in `translated_modules/`
- Detailed progress table
- Timing statistics
- Success/failure summary

---

## 8. verify_json_integration.py
**Verify the JSON-based translation system is set up correctly**

```bash
# Run verification before translating
python examples/verify_json_integration.py
```

**Sample Modules Checked:**
- `clm_varctl`
- `SoilStateType`
- `SoilTemperatureMod`

**Prerequisites:**
- `static_analysis_output/analysis_results.json`
- `static_analysis_output/translation_units.json`

**What It Verifies:**
1. JSON files exist and can be loaded
2. Module information can be extracted
3. Enhanced context can be built
4. Translator initializes correctly

**Output:**
- Verification report with pass/fail for each check
- Module extraction table
- Context summary

---

## 9. generate_tests.py
**Generate comprehensive test suites**

### Option A: Generate for Specific Module
```bash
python examples/generate_tests.py \
  --module SoilTemperatureMod \
  --python ./translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --output ./translated_modules/SoilTemperatureMod/tests \
  --num-cases 10
```

**Module Used:** `SoilTemperatureMod` (or any translated module)

### Option B: Generate for ALL Translated Modules
```bash
# Auto-discovers all modules in translated_modules/
python examples/generate_tests.py --all
```

**Modules Used:** All modules in `translated_modules/` directory

### Option C: Interactive Mode
```bash
python examples/generate_tests.py --interactive
```

Then follow the prompts to enter:
- Module name
- Path to Python file
- Output directory
- Number of test cases

**Output (for each module):**
- `tests/test_<module>.py` - pytest file
- `tests/test_data_<module>.json` - Test data
- `tests/test_documentation_<module>.md` - Documentation

---

## 10. repair_agent_example.py
**Automatically debug and fix failed translations**

```bash
# Runs the basic repair example with a sample bug
python examples/repair_agent_example.py
```

**Module Used:** `SoilTemperatureMod` (sample example with intentional bug)

**What It Does:**
- Creates a sample Python function with an indexing bug
- Analyzes the failure
- Generates corrected code
- Creates root cause analysis report

**Output:**
- `repair_outputs/SoilTemperatureMod_corrected.py` - Fixed code
- `repair_outputs/root_cause_analysis_SoilTemperatureMod.md` - RCA report
- `repair_outputs/failure_analysis_SoilTemperatureMod.json` - Structured data
- `repair_outputs/final_test_report_SoilTemperatureMod.txt` - Test results

---

## Complete Workflow Examples

### Workflow 1: Single Module Translation (Manual Steps)

```bash
cd /burg-archive/home/mck2199/jax-agents

# Step 1: Analyze CNMRespMod
python examples/analyze_module.py

# Step 2: Review analysis_result.json (optional)
cat analysis_result.json | head -50

# Step 3: Translate from analysis
python examples/translate_from_analysis.py

# Step 4: Generate tests
python examples/generate_tests.py \
  --module CNMRespMod \
  --python ./output/CNMRespMod.py \
  --output ./output/tests

# Step 5: Run tests
cd output/tests
pytest test_CNMRespMod.py -v

# Step 6: If tests fail, repair (use actual test output)
cd ../..
# Edit repair_agent_example.py to use your actual failed code and test report
python examples/repair_agent_example.py
```

### Workflow 2: Quick JSON-Based Translation

```bash
cd /burg-archive/home/mck2199/jax-agents

# Step 1: Verify setup
python examples/verify_json_integration.py

# Step 2: Translate sample modules
python examples/translate_with_json.py

# Step 3: Generate tests for all
python examples/generate_tests.py --all

# Step 4: Run all tests
pytest translated_modules/*/tests/test_*.py -v

# Step 5: If any fail, repair
python examples/repair_agent_example.py
```

### Workflow 3: Batch Translate Everything

```bash
cd /burg-archive/home/mck2199/jax-agents

# Step 1: Verify setup
python examples/verify_json_integration.py

# Step 2: Test with first 5 modules (edit script: max_modules=5)
# Edit batch_translate_modules.py line 274: max_modules=5
python examples/batch_translate_modules.py

# Step 3: If working well, translate all (edit script: max_modules=None)
# Edit batch_translate_modules.py line 274: max_modules=None
python examples/batch_translate_modules.py

# Step 4: Generate tests for all
python examples/generate_tests.py --all

# Step 5: Run tests
pytest translated_modules/*/tests/test_*.py -v --tb=short
```

---

## Testing Individual Modules

### Test clm_varctl (Simple)
```bash
# Translate
python -c "
from pathlib import Path
from jax_agents.translator import TranslatorAgent

translator = TranslatorAgent(
    analysis_results_path=Path('static_analysis_output/analysis_results.json'),
    translation_units_path=Path('static_analysis_output/translation_units.json'),
    jax_ctsm_dir=Path('../jax-ctsm'),
    fortran_root=Path('../CLM-ml_v1'),
)

result = translator.translate_module(
    module_name='clm_varctl',
    output_dir=Path('translated_modules/clm_varctl')
)
print(f'✓ Translated clm_varctl: {len(result.physics_code)} chars')
"

# Generate tests
python examples/generate_tests.py \
  --module clm_varctl \
  --python translated_modules/clm_varctl/clm_varctl.py \
  --output translated_modules/clm_varctl/tests

# Run tests
pytest translated_modules/clm_varctl/tests/test_clm_varctl.py -v
```

### Test SoilStateType (Medium)
```bash
# Translate
python -c "
from pathlib import Path
from jax_agents.translator import TranslatorAgent

translator = TranslatorAgent(
    analysis_results_path=Path('static_analysis_output/analysis_results.json'),
    translation_units_path=Path('static_analysis_output/translation_units.json'),
    jax_ctsm_dir=Path('../jax-ctsm'),
    fortran_root=Path('../CLM-ml_v1'),
)

result = translator.translate_module(
    module_name='SoilStateType',
    output_dir=Path('translated_modules/SoilStateType')
)
print(f'✓ Translated SoilStateType: {len(result.physics_code)} chars')
"

# Generate tests
python examples/generate_tests.py \
  --module SoilStateType \
  --python translated_modules/SoilStateType/SoilStateType.py \
  --output translated_modules/SoilStateType/tests

# Run tests
pytest translated_modules/SoilStateType/tests/test_SoilStateType.py -v
```

### Test SoilTemperatureMod (High Complexity)
```bash
# Translate
python -c "
from pathlib import Path
from jax_agents.translator import TranslatorAgent

translator = TranslatorAgent(
    analysis_results_path=Path('static_analysis_output/analysis_results.json'),
    translation_units_path=Path('static_analysis_output/translation_units.json'),
    jax_ctsm_dir=Path('../jax-ctsm'),
    fortran_root=Path('../CLM-ml_v1'),
)

result = translator.translate_module(
    module_name='SoilTemperatureMod',
    output_dir=Path('translated_modules/SoilTemperatureMod')
)
print(f'✓ Translated SoilTemperatureMod: {len(result.physics_code)} chars')
"

# Generate tests
python examples/generate_tests.py \
  --module SoilTemperatureMod \
  --python translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --output translated_modules/SoilTemperatureMod/tests

# Run tests
pytest translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod.py -v
```

---

## Troubleshooting

### If "ModuleNotFoundError: No module named 'jax_agents'"
```bash
export PYTHONPATH="/burg-archive/home/mck2199/jax-agents/src:$PYTHONPATH"
```

### If "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### If JSON files not found
```bash
# Check they exist
ls -la static_analysis_output/
# Should show:
# - analysis_results.json
# - translation_units.json
```

### If Fortran files not found
```bash
# Verify paths
ls -la /burg-archive/home/mck2199/CLM-ml_v1/
ls -la /burg-archive/home/mck2199/CTSM/
```

---

## Quick Reference

| Example | Command | Module(s) | Time |
|---------|---------|-----------|------|
| analyze_module.py | `python examples/analyze_module.py` | CNMRespMod | ~30s |
| translate_from_analysis.py | `python examples/translate_from_analysis.py` | CNMRespMod | ~45s |
| translate_with_context.py | `python examples/translate_with_context.py` | CNGRespMod | ~60s |
| convert_single_module.py | `python examples/convert_single_module.py` | CNGRespMod | ~90s |
| batch_conversion.py | `python examples/batch_conversion.py` | CNGRespMod, CNAllocationMod | ~3min |
| translate_with_json.py | `python examples/translate_with_json.py` | clm_varctl, SoilStateType, SoilTemperatureMod | ~5min |
| batch_translate_modules.py | `python examples/batch_translate_modules.py` | All modules | varies |
| verify_json_integration.py | `python examples/verify_json_integration.py` | clm_varctl, SoilStateType, SoilTemperatureMod | ~10s |
| generate_tests.py | `python examples/generate_tests.py --all` | All translated | ~2min |
| repair_agent_example.py | `python examples/repair_agent_example.py` | SoilTemperatureMod (sample) | ~45s |

---

## Copy-Paste Scripts

### Script 1: Quick Test (Runs in ~2 minutes)
```bash
#!/bin/bash
cd /burg-archive/home/mck2199/jax-agents
export PYTHONPATH="/burg-archive/home/mck2199/jax-agents/src:$PYTHONPATH"

echo "1. Verifying setup..."
python examples/verify_json_integration.py

echo "2. Translating sample modules..."
python examples/translate_with_json.py

echo "3. Testing repair agent..."
python examples/repair_agent_example.py

echo "✓ Complete!"
```

### Script 2: Full Translation + Tests (Runs in ~10 minutes)
```bash
#!/bin/bash
cd /burg-archive/home/mck2199/jax-agents
export PYTHONPATH="/burg-archive/home/mck2199/jax-agents/src:$PYTHONPATH"

echo "1. Verifying setup..."
python examples/verify_json_integration.py

echo "2. Translating 3 sample modules..."
python examples/translate_with_json.py

echo "3. Generating tests..."
python examples/generate_tests.py --all

echo "4. Running tests..."
pytest translated_modules/*/tests/test_*.py -v --tb=short

echo "✓ Complete!"
```

---

## Summary

All examples are ready to run! Just:
1. Set `PYTHONPATH` and `ANTHROPIC_API_KEY`
2. Copy-paste any command above
3. Watch the magic happen! 🚀

