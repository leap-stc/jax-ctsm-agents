# 🚀 Translation Workflow - Quick Start

## One Command to Run Everything!

```bash
cd /burg-archive/home/mck2199/jax-agents
./run_translation_workflow.sh --all
```

That's it! This will:
1. ✅ Translate Fortran → JAX Python
2. ✅ Generate comprehensive tests
3. ✅ Run tests
4. ✅ Offer to repair failures

---

## Quick Commands

| What You Want | Command |
|---------------|---------|
| **Run everything** | `./run_translation_workflow.sh --all` |
| **Run with auto-repair** | `./run_translation_workflow.sh --all --auto-repair` |
| **Interactive menu** | `./run_translation_workflow.sh --interactive` |
| **Just translate** | `./run_translation_workflow.sh --translate` |
| **Just test** | `./run_translation_workflow.sh --test` |
| **Just repair** | `./run_translation_workflow.sh --repair` |
| **Custom modules** | `./run_translation_workflow.sh --all --modules "m1,m2"` |
| **Help** | `./run_translation_workflow.sh --help` |

---

## The Three Components

### 1. Translation (`translate_with_json.py`)
Converts Fortran modules to JAX Python

**Input:** JSON analysis files  
**Output:** `translated_modules/<module>/<module>.py`

### 2. Test Generation (`generate_tests.py`)
Creates comprehensive test suites

**Input:** Translated Python code  
**Output:** `translated_modules/<module>/tests/test_<module>.py`

### 3. Repair (`repair_agent_example.py`)
Fixes failing tests automatically

**Input:** Failed tests, Fortran reference  
**Output:** `repair_outputs/<module>/<module>_corrected.py`

---

## Examples

### Example 1: Default Modules
```bash
./run_translation_workflow.sh --all
```
Translates: `clm_varctl`, `SoilStateType`, `SoilTemperatureMod`

### Example 2: One Module
```bash
./run_translation_workflow.sh --all --modules "WaterFluxType"
```

### Example 3: Multiple Custom Modules
```bash
./run_translation_workflow.sh --all \
  --modules "clm_varctl,WaterFluxType,CanopyFluxesMod" \
  --auto-repair
```

### Example 4: Interactive (Guided)
```bash
./run_translation_workflow.sh --interactive
```
Choose from menu options!

---

## Workflow Diagram

```
┌─────────────────────────────────────────────┐
│  ./run_translation_workflow.sh --all       │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────▼──────────┐
        │  1. TRANSLATE       │
        │  Fortran → Python   │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  2. TEST            │
        │  Generate tests     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  3. RUN TESTS       │
        │  pytest -v          │
        └──────────┬──────────┘
                   │
              ┌────┴────┐
              │         │
            PASS      FAIL
              │         │
              │    ┌────▼────┐
              │    │ 4. REPAIR│
              │    │ Fix bugs │
              │    └─────────┘
              │         │
              ▼         ▼
         ✓ SUCCESS ✓ SUCCESS
```

---

## Requirements

1. **Python 3.9+** installed
2. **API Key** set:
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   ```
3. **JSON files** in `static_analysis_output/`:
   - `analysis_results.json`
   - `translation_units.json`

---

## Output Files

```
translated_modules/
├── ModuleName/
│   ├── ModuleName.py              # Translated code
│   └── tests/
│       ├── test_ModuleName.py     # Test file
│       └── test_data_ModuleName.json

repair_outputs/
└── ModuleName/
    ├── ModuleName_corrected.py    # Fixed code
    └── root_cause_analysis_ModuleName.md  # RCA report
```

---

## Common Issues

### "ANTHROPIC_API_KEY not set"
```bash
export ANTHROPIC_API_KEY="sk-..."
```

### "analysis_results.json not found"
```bash
# Check files exist
ls static_analysis_output/
```

### "Python not found"
```bash
# Activate environment
source venv/bin/activate
```

---

## Tips

💡 **Start with one module** to test the workflow  
💡 **Use `--auto-repair`** for batch processing  
💡 **Check repair reports** to understand fixes  
💡 **Save logs** with `2>&1 | tee log.txt`  

---

## Need More Help?

- **Detailed Guide:** `WORKFLOW_SCRIPT_GUIDE.md`
- **Script Help:** `./run_translation_workflow.sh --help`
- **Examples:** `examples/README.md`

---

## Quick Test

```bash
# Test with defaults (takes ~5-10 minutes)
./run_translation_workflow.sh --all

# If everything works, you'll see:
# ✓ Translation completed
# ✓ Test generation completed
# ✓ Tests running...
# ✓ All tests passed (or repair offered)
```

---

**That's it! One script, three steps, complete automation!** 🎉

