# JSON-Based Fortran to JAX Translation

## Quick Start

The translator now uses static analysis JSON files for better translations.

### Setup

JSON files should be at:
```
jax-agents/
  static_analysis_output/
    analysis_results.json      # From Fortran-Analyzer
    translation_units.json     # From Fortran-Analyzer
```

Fortran source files at:
```
CLM-ml_v1/                     # Your Fortran code location
  clm_src_biogeophys/
  clm_src_main/
  ...
```

### Usage

```python
from pathlib import Path
from jax_agents.translator import TranslatorAgent

translator = TranslatorAgent(
    analysis_results_path=Path("static_analysis_output/analysis_results.json"),
    translation_units_path=Path("static_analysis_output/translation_units.json"),
    jax_ctsm_dir=Path("../jax-ctsm"),
    fortran_root=Path("../CLM-ml_v1"),  # Path to Fortran source files
)

# Translate by module name (file path automatic)
result = translator.translate_module(
    module_name="SoilStateType",
    output_dir=Path("translated_modules/SoilStateType")
)
```

### Test It

```bash
# 1. Verify setup
python examples/verify_json_integration.py

# 2. Translate samples
python examples/translate_with_json.py

# 3. Batch translate
python examples/batch_translate_modules.py
```

## What Changed

**Before**: Manual file paths, limited context
```python
translator.translate_module(
    fortran_file=Path("SoilStateType.F90"),
    analysis=manual_analysis,
)
```

**After**: Module name, rich context from JSON
```python
translator.translate_module(
    module_name="SoilStateType",  # Automatic path resolution
)
```

## Benefits

- **Dependency aware**: Knows what modules depend on each other
- **Complexity guided**: LLM sees difficulty scores and effort estimates  
- **Line precise**: References exact Fortran source lines
- **Batch ready**: Translate entire project systematically

## JSON Structure

**analysis_results.json**: Module metadata, dependencies, entities
**translation_units.json**: 120 units with complexity scores, split functions

## Complexity Guide

- **Low** (< 5): ~5-10 min - Simple modules like `clm_varctl`
- **Medium** (5-10): ~15-30 min - Data structures like `SoilStateType`
- **High** (≥ 10): ~45+ min - Physics like `SoilTemperatureMod`

## Output

Each module generates:
```
translated_modules/
  SoilStateType/
    SoilStateType.py                    # Main physics
    SoilStateType_params.py             # Parameters (if needed)
    test_SoilStateType.py               # Tests (if generated)
    SoilStateType_translation_notes.md  # Translation notes
```

## Files Modified

- `src/jax_agents/translator.py` - Enhanced with JSON support
- `src/jax_agents/prompts/translation_prompts.py` - Enhanced prompt
- `examples/` - New verification and batch translation scripts
