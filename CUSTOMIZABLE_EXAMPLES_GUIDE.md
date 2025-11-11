# 🎉 All Examples Are Now Customizable!

## What Changed

**Before:** Most examples had hardcoded module paths - you had to edit the Python files  
**After:** All examples now accept command-line arguments - just run them with your module!

## ✅ Updated Examples

| Example | Status | Modes Available |
|---------|--------|----------------|
| analyze_module.py | ✅ **UPDATED** | CLI, Interactive, Example |
| translate_with_context.py | ✅ **UPDATED** | CLI, Interactive, Example |
| convert_single_module.py | ✅ **UPDATED** | CLI, Interactive, Example |
| repair_agent_example.py | ✅ **UPDATED** | CLI, Interactive, Example |
| generate_tests.py | ✅ Already had CLI | CLI, Interactive, All |
| batch_translate_modules.py | ✅ Already flexible | Batch mode |
| translate_with_json.py | ✅ Already flexible | Works with any JSON module |
| verify_json_integration.py | ✅ Already flexible | Verification mode |

---

## Quick Start Guide

### 1. analyze_module.py - NEW! 🎯

**Analyze ANY Fortran module with command-line arguments:**

```bash
# Analyze your specific module
python examples/analyze_module.py /path/to/YourModule.F90

# With detailed physics extraction
python examples/analyze_module.py /path/to/YourModule.F90 --extract-physics

# Custom output file
python examples/analyze_module.py /path/to/YourModule.F90 -o my_analysis.json

# Interactive mode (asks you for inputs)
python examples/analyze_module.py --interactive

# Run with default example module
python examples/analyze_module.py --example
```

**Example Commands:**

```bash
# Analyze SoilTemperatureMod
python examples/analyze_module.py \
  /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90

# Analyze WaterFluxType with physics extraction
python examples/analyze_module.py \
  /burg-archive/home/mck2199/CTSM/src/biogeophys/WaterFluxType.F90 \
  --extract-physics \
  -o water_flux_analysis.json

# Interactive mode (it will prompt you)
python examples/analyze_module.py --interactive
```

**All Options:**
```
positional arguments:
  fortran_file          Path to Fortran module file

optional arguments:
  -h, --help            Show help message
  -o, --output OUTPUT   Output JSON file (default: analysis_<module>.json)
  --extract-physics     Extract detailed physics (uses more tokens)
  --interactive         Interactive mode - prompts for inputs
  --example             Run with default example (CNMRespMod.F90)
```

---

### 2. translate_with_context.py - NEW! 🎯

**Translate ANY module with two-step process:**

```bash
# Translate your module
python examples/translate_with_context.py /path/to/YourModule.F90

# Specify output directory
python examples/translate_with_context.py /path/to/YourModule.F90 -o ./my_output

# Skip detailed physics (faster)
python examples/translate_with_context.py /path/to/YourModule.F90 --no-physics

# Interactive mode
python examples/translate_with_context.py --interactive

# Run with default example
python examples/translate_with_context.py --example
```

**Example Commands:**

```bash
# Translate SoilTemperatureMod
python examples/translate_with_context.py \
  /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90 \
  -o translated_modules/SoilTemperatureMod

# Translate CNPhenologyMod (fast mode, no detailed physics)
python examples/translate_with_context.py \
  /burg-archive/home/mck2199/CTSM/src/biogeochem/CNPhenologyMod.F90 \
  --no-physics \
  -o output/CNPhenologyMod

# Interactive mode
python examples/translate_with_context.py --interactive
```

**All Options:**
```
positional arguments:
  fortran_file          Path to Fortran module file

optional arguments:
  -h, --help            Show help message
  -o, --output OUTPUT   Output directory (default: ./output)
  --jax-ctsm-dir DIR    Path to jax-ctsm directory
  --no-physics          Skip detailed physics extraction (faster)
  --no-save-analysis    Don't save analysis JSON file
  --interactive         Interactive mode
  --example             Run with default example (CNGRespMod.F90)
```

---

### 3. convert_single_module.py - NEW! 🎯

**Convert with orchestrator (full automated workflow):**

```bash
# Convert a biogeochem module
python examples/convert_single_module.py src/biogeochem/CNGRespMod.F90

# Convert a biogeophys module
python examples/convert_single_module.py src/biogeophys/SoilTemperatureMod.F90

# Specify output directory
python examples/convert_single_module.py src/biogeochem/CNGRespMod.F90 \
  --output /path/to/output

# Skip report generation (faster)
python examples/convert_single_module.py src/biogeochem/CNGRespMod.F90 --no-report

# Interactive mode
python examples/convert_single_module.py --interactive

# Run with default example
python examples/convert_single_module.py --example
```

**Example Commands:**

```bash
# Convert SoilTemperatureMod from CLM-ml_v1
python examples/convert_single_module.py \
  src/biogeophys/SoilTemperatureMod.F90 \
  --ctsm-dir /burg-archive/home/mck2199/CLM-ml_v1 \
  --output converted_modules/SoilTemperatureMod

# Convert CNAllocationMod with custom paths
python examples/convert_single_module.py \
  src/biogeochem/CNAllocationMod.F90 \
  --ctsm-dir /burg-archive/home/mck2199/CTSM \
  --jax-ctsm-dir /burg-archive/home/mck2199/jax-ctsm \
  --output custom_output

# Interactive mode
python examples/convert_single_module.py --interactive
```

**All Options:**
```
positional arguments:
  fortran_file          Relative path to Fortran file (from CTSM directory)

optional arguments:
  -h, --help            Show help message
  --ctsm-dir DIR        Path to CTSM root directory
  --jax-ctsm-dir DIR    Path to jax-ctsm root directory
  -o, --output OUTPUT   Output directory
  --no-report           Skip conversion report generation
  --interactive         Interactive mode
  --example             Run with default example (CNGRespMod.F90)
```

---

### 4. repair_agent_example.py - NEW! 🎯

**Repair ANY failed translation:**

```bash
# Run with built-in example (sample bug)
python examples/repair_agent_example.py --example

# Repair with your own code files
python examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran /path/to/original.F90 \
  --python /path/to/failed.py \
  --test-report /path/to/pytest_output.txt

# With automatic test execution
python examples/repair_agent_example.py \
  --module MyModule \
  --fortran /path/to/original.F90 \
  --python /path/to/failed.py \
  --test-report /path/to/pytest_output.txt \
  --test-file /path/to/test_MyModule.py

# Interactive mode
python examples/repair_agent_example.py --interactive

# Increase max iterations for complex issues
python examples/repair_agent_example.py --example --max-iterations 10
```

**Example Commands:**

```bash
# Repair SoilTemperatureMod with actual files
python examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90 \
  --python translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --test-report test_failures.txt \
  --test-file translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod.py \
  --max-iterations 10

# Interactive mode (it will prompt for all inputs)
python examples/repair_agent_example.py --interactive
```

**All Options:**
```
optional arguments:
  -h, --help            Show help message
  --module MODULE       Module name
  --fortran PATH        Path to original Fortran code file
  --python PATH         Path to failed Python code file
  --test-report PATH    Path to test report file (pytest output)
  --test-file PATH      Path to pytest file (for automatic re-testing)
  -o, --output OUTPUT   Output directory (default: repair_outputs)
  --max-iterations N    Maximum repair iterations (default: 5)
  --interactive         Interactive mode
  --example             Run with built-in example (sample bug)
```

---

### 5. generate_tests.py - Already Had CLI! ✅

**Generate tests for ANY module:**

```bash
# For specific module
python examples/generate_tests.py \
  --module YourModuleName \
  --python /path/to/YourModuleName.py \
  --output /path/to/output \
  --num-cases 15

# For all translated modules
python examples/generate_tests.py --all

# Interactive mode
python examples/generate_tests.py --interactive
```

---

## Complete Workflows

### Workflow 1: From Scratch - Custom Module

```bash
# Step 1: Analyze your module
python examples/analyze_module.py \
  /path/to/YourModule.F90 \
  --extract-physics \
  -o analysis_YourModule.json

# Step 2: Translate your module
python examples/translate_with_context.py \
  /path/to/YourModule.F90 \
  -o translated_modules/YourModule

# Step 3: Generate tests
python examples/generate_tests.py \
  --module YourModule \
  --python translated_modules/YourModule/YourModule.py \
  --output translated_modules/YourModule/tests

# Step 4: Run tests
pytest translated_modules/YourModule/tests/test_YourModule.py -v

# Step 5: If tests fail, repair
python examples/repair_agent_example.py \
  --module YourModule \
  --fortran /path/to/YourModule.F90 \
  --python translated_modules/YourModule/YourModule.py \
  --test-report test_output.txt \
  --test-file translated_modules/YourModule/tests/test_YourModule.py
```

### Workflow 2: Quick Translation - Any Module

```bash
# Just translate directly (one command!)
python examples/convert_single_module.py \
  src/biogeophys/YourModule.F90 \
  --ctsm-dir /path/to/ctsm \
  --output my_translations
```

### Workflow 3: Interactive - Beginner Friendly

```bash
# Let the tool guide you through each step
python examples/analyze_module.py --interactive
python examples/translate_with_context.py --interactive
python examples/generate_tests.py --interactive
python examples/repair_agent_example.py --interactive
```

---

## Real-World Examples

### Example 1: Translate SoilTemperatureMod

```bash
cd /burg-archive/home/mck2199/jax-agents

# Analyze
python examples/analyze_module.py \
  /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90 \
  --extract-physics \
  -o soil_temp_analysis.json

# Translate
python examples/translate_with_context.py \
  /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90 \
  -o translated_modules/SoilTemperatureMod

# Generate tests
python examples/generate_tests.py \
  --module SoilTemperatureMod \
  --python translated_modules/SoilTemperatureMod/SoilTemperatureMod.py \
  --output translated_modules/SoilTemperatureMod/tests \
  --num-cases 20
```

### Example 2: Translate WaterFluxType

```bash
# All-in-one with orchestrator
python examples/convert_single_module.py \
  src/biogeophys/WaterFluxType.F90 \
  --ctsm-dir /burg-archive/home/mck2199/CTSM \
  --output translated_modules/WaterFluxType

# Generate tests
python examples/generate_tests.py \
  --module WaterFluxType \
  --python translated_modules/WaterFluxType/WaterFluxType.py \
  --output translated_modules/WaterFluxType/tests
```

### Example 3: Repair CNPhenologyMod

```bash
# Assuming you have a failed translation and test report

python examples/repair_agent_example.py \
  --module CNPhenologyMod \
  --fortran /burg-archive/home/mck2199/CTSM/src/biogeochem/CNPhenologyMod.F90 \
  --python translated_modules/CNPhenologyMod/CNPhenologyMod.py \
  --test-report pytest_failures.txt \
  --test-file translated_modules/CNPhenologyMod/tests/test_CNPhenologyMod.py \
  --max-iterations 10 \
  -o repairs/CNPhenologyMod
```

---

## Interactive Mode Examples

### Interactive Analysis

```bash
$ python examples/analyze_module.py --interactive

Interactive Module Analysis

Enter path to Fortran module:
> /burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/SoilTemperatureMod.F90

Extract detailed physics? (y/n, default: n):
> y

Output file (press Enter for default):
> 

[Analysis runs...]
```

### Interactive Translation

```bash
$ python examples/translate_with_context.py --interactive

Interactive Module Translation

Enter path to Fortran module:
> /burg-archive/home/mck2199/CTSM/src/biogeochem/CNGRespMod.F90

Output directory (default: ./output):
> my_translations

Extract detailed physics? (y/n, default: y):
> y

Path to jax-ctsm (default: /burg-archive/home/mck2199/jax-ctsm):
> 

[Translation runs...]
```

### Interactive Repair

```bash
$ python examples/repair_agent_example.py --interactive

Interactive Repair Agent

Module name:
> SoilTemperatureMod

Path to original Fortran code file:
> /path/to/original.F90

Path to failed Python code file:
> /path/to/failed.py

Path to test report file (pytest output):
> /path/to/test_output.txt

Path to pytest file (optional, press Enter to skip):
> 

Output directory (default: repair_outputs):
> 

Max iterations (default: 5):
> 10

[Repair runs...]
```

---

## Quick Reference

### Get Help for Any Example

```bash
# Show all options
python examples/analyze_module.py --help
python examples/translate_with_context.py --help
python examples/convert_single_module.py --help
python examples/repair_agent_example.py --help
python examples/generate_tests.py --help
```

### Run Default Examples

```bash
# All support --example flag to run with demo module
python examples/analyze_module.py --example
python examples/translate_with_context.py --example
python examples/convert_single_module.py --example
python examples/repair_agent_example.py --example
```

### Interactive Mode for Everything

```bash
# All support --interactive flag
python examples/analyze_module.py --interactive
python examples/translate_with_context.py --interactive
python examples/convert_single_module.py --interactive
python examples/repair_agent_example.py --interactive
python examples/generate_tests.py --interactive
```

---

## Summary of Changes

### Before (Required Editing)
```bash
# Had to edit the Python file
# Line 21: fortran_file = Path("/hardcoded/path/CNMRespMod.F90")
python examples/analyze_module.py
```

### After (Just Use CLI)
```bash
# Just pass your module as argument!
python examples/analyze_module.py /your/path/YourModule.F90
```

---

## Benefits

✅ **No more editing Python files**  
✅ **Works with ANY module** (just pass the path)  
✅ **Interactive mode** for beginners  
✅ **Example mode** to see how it works  
✅ **Flexible options** for advanced users  
✅ **Consistent interface** across all examples  

---

## Next Steps

1. **Try the examples:**
   ```bash
   python examples/analyze_module.py --example
   python examples/translate_with_context.py --example
   python examples/repair_agent_example.py --example
   ```

2. **Use with your modules:**
   ```bash
   python examples/analyze_module.py /path/to/YourModule.F90
   ```

3. **Use interactive mode if unsure:**
   ```bash
   python examples/analyze_module.py --interactive
   ```

🎉 **All examples are now fully customizable and user-friendly!**

