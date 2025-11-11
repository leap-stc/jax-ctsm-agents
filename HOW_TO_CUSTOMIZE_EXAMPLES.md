# How to Customize Examples for Your Own Modules

## Understanding the Examples

The examples fall into **three categories**:

### 1. ✅ **Fully Customizable** (CLI Arguments)
These accept command-line arguments - no editing needed!

- **generate_tests.py** - Fully customizable with `--module`, `--python`, `--output` arguments

### 2. 📝 **Edit Required** (Hardcoded Demo Scripts)
These have hardcoded module paths - edit the file to use your module.

- **analyze_module.py**
- **translate_from_analysis.py**
- **translate_with_context.py**
- **convert_single_module.py**
- **batch_conversion.py**

### 3. 🔧 **Config-Based** (Uses JSON Files)
These work with JSON analysis files - works for any module in the JSON.

- **translate_with_json.py**
- **batch_translate_modules.py**
- **verify_json_integration.py**

### 4. 🎯 **Self-Contained Demo** (Uses Sample Data)
- **repair_agent_example.py** - Uses built-in sample bug

---

## How to Customize Each Example

### 1. generate_tests.py ✅ (Already Customizable!)

**No editing needed!** Use command-line arguments:

```bash
# For your specific module
python examples/generate_tests.py \
  --module YourModuleName \
  --python /path/to/your/YourModuleName.py \
  --output /path/to/output/dir \
  --num-cases 15

# Interactive mode (it will ask you for inputs)
python examples/generate_tests.py --interactive
```

**Example for a custom module:**
```bash
python examples/generate_tests.py \
  --module WaterFluxMod \
  --python /burg-archive/home/mck2199/jax-agents/translated_modules/WaterFluxMod/WaterFluxMod.py \
  --output /burg-archive/home/mck2199/jax-agents/translated_modules/WaterFluxMod/tests \
  --num-cases 20
```

---

### 2. analyze_module.py 📝 (Edit Required)

**What to change:** Line 21 - the `fortran_file` path

**Original:**
```python
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNMRespMod.F90")
```

**Change to your module:**
```python
# Example 1: Different biogeochem module
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNPhenologyMod.F90")

# Example 2: Biogeophys module
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeophys/WaterFluxType.F90")

# Example 3: CLM-ml_v1 module
fortran_file = Path("/burg-archive/home/mck2199/CLM-ml_v1/clm_src_biogeophys/CanopyFluxesMod.F90")
```

**Steps:**
1. Open `examples/analyze_module.py` in an editor
2. Find line 21: `fortran_file = Path(...)`
3. Replace the path with your Fortran file
4. Save and run: `python examples/analyze_module.py`

---

### 3. translate_from_analysis.py 📝 (Edit Required)

**What to change:** Lines 24 and 25 - file paths

**Original:**
```python
analysis_file = Path("analysis_result.json")
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNMRespMod.F90")
```

**Change to your module:**
```python
# Use the analysis you created with analyze_module.py
analysis_file = Path("analysis_result.json")  # Keep this if you ran analyze_module.py
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/YourModule.F90")
```

**Steps:**
1. First run `analyze_module.py` (with your module) to create `analysis_result.json`
2. Edit `examples/translate_from_analysis.py` line 25
3. Update the `fortran_file` path to match your module
4. Run: `python examples/translate_from_analysis.py`

---

### 4. translate_with_context.py 📝 (Edit Required)

**What to change:** Line 20 - the `fortran_file` path

**Original:**
```python
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/CNGRespMod.F90")
```

**Change to your module:**
```python
fortran_file = Path("/burg-archive/home/mck2199/CTSM/src/biogeochem/YourModule.F90")
```

---

### 5. convert_single_module.py 📝 (Edit Required)

**What to change:** Line 32 - the `fortran_file` path

**Original:**
```python
fortran_file = "src/biogeochem/CNGRespMod.F90"
```

**Change to your module:**
```python
# Relative to CTSM directory
fortran_file = "src/biogeochem/YourModule.F90"

# Or different directory
fortran_file = "src/biogeophys/YourModule.F90"
```

---

### 6. batch_conversion.py 📝 (Edit Required)

**What to change:** Lines 25-29 - the list of modules

**Original:**
```python
modules_to_convert = [
    "src/biogeochem/CNGRespMod.F90",
    "src/biogeochem/CNAllocationMod.F90",
    # "src/biogeochem/CNPhenologyMod.F90",  # Uncommented
]
```

**Change to your modules:**
```python
modules_to_convert = [
    "src/biogeophys/SoilTemperatureMod.F90",
    "src/biogeophys/WaterFluxType.F90",
    "src/biogeochem/CNVegStructUpdateMod.F90",
    # Add as many as you want
]
```

---

### 7. translate_with_json.py 🔧 (Works for Any Module in JSON!)

**No editing needed if your module is in the JSON files!**

The script tries to translate 3 example modules. To use your own:

**Option 1: Edit the example modules (Lines 62-95)**

**Original:**
```python
# Example 1: Translate a simple module (low complexity)
result1 = translator.translate_module(
    module_name="clm_varctl",
    output_dir=output_dir / "clm_varctl"
)
```

**Change to your module:**
```python
# Example 1: Your module
result1 = translator.translate_module(
    module_name="YourModuleName",  # Must be in JSON files
    output_dir=output_dir / "YourModuleName"
)
```

**Option 2: Use it as a library in Python:**

```python
from pathlib import Path
from jax_agents.translator import TranslatorAgent

project_root = Path("/burg-archive/home/mck2199")

translator = TranslatorAgent(
    analysis_results_path=project_root / "jax-agents/static_analysis_output/analysis_results.json",
    translation_units_path=project_root / "jax-agents/static_analysis_output/translation_units.json",
    jax_ctsm_dir=project_root / "jax-ctsm",
    fortran_root=project_root / "CLM-ml_v1",
)

# Translate YOUR module
result = translator.translate_module(
    module_name="YourModuleName",  # Any module from JSON
    output_dir=Path("translated_modules/YourModuleName")
)

print(f"Success! Generated {len(result.physics_code)} chars")
```

---

### 8. batch_translate_modules.py 🔧 (Translates ALL modules!)

**No editing needed!** It reads ALL modules from the JSON file.

**To customize:**

**Lines 273-275** - Control which modules to translate:

```python
translate_all_modules(
    translator=translator,
    translation_order=translation_order,
    translation_units=translation_units,
    output_dir=output_dir,
    skip_existing=True,   # Set to False to re-translate
    max_modules=None,     # Set to 5 to test with first 5 modules
)
```

**Customize it:**
```python
# Translate only first 10 modules (for testing)
max_modules=10,

# Re-translate everything (don't skip existing)
skip_existing=False,

# Translate specific subset (edit translation_order list)
```

---

### 9. verify_json_integration.py 🔧 (Tests Sample Modules)

**No editing needed for verification!**

To test different modules, edit **line 219**:

**Original:**
```python
sample_modules = ["clm_varctl", "SoilStateType", "SoilTemperatureMod"]
```

**Change to your modules:**
```python
sample_modules = ["YourModule1", "YourModule2", "YourModule3"]
```

---

### 10. repair_agent_example.py 🎯 (Self-Contained Demo)

**Two ways to use:**

#### Option 1: Run the demo (no changes needed)
```bash
python examples/repair_agent_example.py
```
Uses built-in sample bug to demonstrate repair.

#### Option 2: Customize for your actual failed code

**Edit the `repair_failed_translation()` function:**

**Lines 26-40** - Your Fortran code:
```python
fortran_code = """
YOUR ACTUAL FORTRAN CODE HERE
"""
```

**Lines 43-65** - Your failed Python code:
```python
failed_python_code = """
YOUR FAILED PYTHON CODE HERE
"""
```

**Lines 68-97** - Your actual test report:
```python
test_report = """
PASTE YOUR PYTEST OUTPUT HERE
"""
```

**Lines 100-101** - Your test file (optional):
```python
test_file_path = Path("path/to/your/test_file.py")  # For automatic re-testing
```

---

## Creating Fully Customizable Scripts

### Template: Customizable Analysis Script

Create `custom_analyze.py`:

```python
#!/usr/bin/env python3
"""Custom analysis script with user input."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jax_agents import StaticAnalysisAgent
from rich.console import Console

console = Console()

def main():
    # Get module path from user
    if len(sys.argv) < 2:
        console.print("[yellow]Usage: python custom_analyze.py <fortran_file>[/yellow]")
        console.print("\nExample:")
        console.print("  python custom_analyze.py /path/to/YourModule.F90")
        sys.exit(1)
    
    fortran_file = Path(sys.argv[1])
    
    if not fortran_file.exists():
        console.print(f"[red]Error: File not found: {fortran_file}[/red]")
        sys.exit(1)
    
    console.print(f"[cyan]Analyzing {fortran_file.name}...[/cyan]\n")
    
    # Analyze
    analyzer = StaticAnalysisAgent()
    analysis = analyzer.analyze_module(fortran_file)
    
    # Display results
    console.print(f"[green]✓ Analysis complete![/green]")
    console.print(f"Module: {analysis.module_name}")
    console.print(f"Subroutines: {len(analysis.subroutines)}")
    
    # Save
    output_file = Path(f"analysis_{analysis.module_name}.json")
    analysis.save(output_file)
    console.print(f"\n[green]Saved to: {output_file}[/green]")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python custom_analyze.py /burg-archive/home/mck2199/CTSM/src/biogeochem/YourModule.F90
```

---

### Template: Customizable Translation Script

Create `custom_translate.py`:

```python
#!/usr/bin/env python3
"""Custom translation script with arguments."""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jax_agents.translator import TranslatorAgent
from rich.console import Console

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Translate a Fortran module to JAX")
    parser.add_argument("module_name", help="Module name (must be in JSON files)")
    parser.add_argument("--output", default="translated_modules", help="Output directory")
    parser.add_argument("--analysis", default="static_analysis_output/analysis_results.json")
    parser.add_argument("--units", default="static_analysis_output/translation_units.json")
    
    args = parser.parse_args()
    
    # Initialize translator
    translator = TranslatorAgent(
        analysis_results_path=Path(args.analysis),
        translation_units_path=Path(args.units),
        jax_ctsm_dir=Path("../jax-ctsm"),
        fortran_root=Path("../CLM-ml_v1"),
    )
    
    # Translate
    console.print(f"[cyan]Translating {args.module_name}...[/cyan]")
    result = translator.translate_module(
        module_name=args.module_name,
        output_dir=Path(args.output) / args.module_name
    )
    
    console.print(f"[green]✓ Success! {len(result.physics_code)} chars generated[/green]")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python custom_translate.py SoilTemperatureMod
python custom_translate.py WaterFluxType --output my_translations
```

---

## Quick Reference: Which Examples Need Editing?

| Example | Customization | How |
|---------|--------------|-----|
| analyze_module.py | ❌ Edit file | Line 21: `fortran_file` path |
| translate_from_analysis.py | ❌ Edit file | Line 24-25: paths |
| translate_with_context.py | ❌ Edit file | Line 20: `fortran_file` path |
| convert_single_module.py | ❌ Edit file | Line 32: `fortran_file` path |
| batch_conversion.py | ❌ Edit file | Lines 25-29: module list |
| translate_with_json.py | ✅ Works as-is | Or edit lines 62-95 for different modules |
| batch_translate_modules.py | ✅ Works as-is | Optional: edit line 274 for limits |
| verify_json_integration.py | ✅ Works as-is | Optional: edit line 219 for different samples |
| generate_tests.py | ✅ CLI args! | Use `--module`, `--python`, `--output` |
| repair_agent_example.py | ✅ Demo works | Optional: edit lines 26-101 for real code |

---

## Recommendation: Make Them All Customizable

Would you like me to **update all examples to accept command-line arguments** like `generate_tests.py` does?

This would allow:
```bash
# Instead of editing files
python examples/analyze_module.py YourModule.F90
python examples/translate_with_context.py YourModule.F90
python examples/convert_single_module.py YourModule.F90

# With interactive prompts
python examples/analyze_module.py --interactive
```

Let me know if you want me to create these improved versions! 🚀

