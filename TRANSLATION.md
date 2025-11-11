# Testing Iterative Translation

## Overview
The translator now processes each translation unit individually (unit-by-unit) and then assembles them into a complete module. The entire module is still translated in one run.

## Quick Test

```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/translate_with_json.py
```

This will translate `SoilStateType` using the new iterative approach.

## What to Observe

The output should show:
```
🔄 Translating SoilStateType to JAX
Reading from: /burg-archive/home/mck2199/CLM-ml_v1/...
Found N translation units
Translating unit 1/N: unit_id (unit_type)
Translating unit 2/N: unit_id (unit_type)
...
Assembling complete module...
✓ Translation complete!
```

## Expected Files

After translation, check `translated_modules/SoilStateType/`:
- `SoilStateType.py` - Main physics module (assembled from all units)
- `SoilStateType_params.py` - Parameters (if needed)
- `SoilStateType_translation_notes.md` - Assembly notes

## Testing Different Modules

Edit `examples/translate_with_json.py`, change module name:

```python
result = translator.translate_module(
    module_name="SoilTemperatureMod",  # Change this
    output_dir=output_dir
)
```

Available modules (see `static_analysis_output/analysis_results.json`):
- SoilStateType
- SoilTemperatureMod
- WaterFluxType
- TemperatureType
- CanopyFluxesMod
- ...and more

## Batch Translation Test

```bash
python examples/batch_translate_modules.py
```

Translates multiple modules sequentially using iterative approach.

## Verification

1. **Check unit count**: Verify the number of units matches `translation_units.json`
2. **Inspect output**: Look for proper imports, NamedTuples, vectorized code
3. **Assembly quality**: Ensure assembled module is cohesive (no duplicate imports, proper organization)

## Debugging

If translation fails or produces poor results:

1. **Check unit extraction**: Look for "Found N translation units" message
2. **Fallback mode**: If "No translation units found", it uses legacy (full module) translation
3. **Unit boundaries**: Verify line ranges in `translation_units.json` are correct
4. **API limits**: Large modules may hit token limits per unit

## Configuration

In `examples/translate_with_json.py`:

```python
translator = TranslatorAgent(
    analysis_results_path=analysis_results_json,
    translation_units_path=translation_units_json,
    jax_ctsm_dir=jax_ctsm_dir,
    fortran_root=fortran_root,
    model="claude-sonnet-4-5",  # Adjust if needed
    temperature=0.0,
    max_tokens=48000,  # Increase if units are large
)
```

## Comparing Old vs New Approach

**Old** (before changes):
- Sent all units at once in single prompt
- Single LLM call per module
- Large prompt size

**New** (iterative):
- Process each unit separately
- N+1 LLM calls per module (N units + 1 assembly)
- Smaller prompt per unit
- Better for large modules
- More context-aware (previous units visible)

## Success Criteria

✅ Translation completes without errors
✅ Generated Python code is syntactically valid
✅ Physics equations preserved (compare with Fortran)
✅ JAX best practices followed (pure functions, NamedTuples, vectorization)
✅ Proper Fortran line references in docstrings

