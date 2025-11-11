# ✅ Repair Agent Test Setup Complete!

## What Was Created

A complete testing environment for the Repair Agent with intentionally failing SoilTemperatureMod code.

### Files Created

| File | Location | Purpose |
|------|----------|---------|
| **test_SoilTemperatureMod_FAILING.py** | `translated_modules/SoilTemperatureMod/tests/` | Python code with 5 intentional bugs |
| **FORTRAN_REFERENCE.F90** | `translated_modules/SoilTemperatureMod/tests/` | Correct Fortran reference implementation |
| **REPAIR_AGENT_TEST_GUIDE.md** | `translated_modules/SoilTemperatureMod/tests/` | Complete testing guide |
| **test_repair_agent.sh** | Root directory | Automated test script |

---

## The 5 Intentional Bugs

### Bug 1: Off-by-One Indexing (Fortran → Python)
```python
# WRONG:
for i in range(1, n_columns):  # Skips first column!

# CORRECT:
for i in range(n_columns):  # Processes all columns
```

### Bug 2: Wrong Array Index
```python
# WRONG:
sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i-1, j]

# CORRECT:
sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i, j]
```

### Bug 3: Incorrect Formula
```python
# WRONG:
tk = tkdry[i, j] + sat * tkmg[i, j]

# CORRECT (Johansen formula):
tk = tkdry[i, j] + sat * (tkmg[i, j] - tkdry[i, j])
```

### Bug 4: Skipping First Column (Heat Capacity)
```python
# WRONG:
for i in range(1, n_columns):  # Skips column 0

# CORRECT:
for i in range(n_columns)  # All columns
```

### Bug 5: Missing Depth Multiplication
```python
# WRONG:
cv_soil = csol[i, j]  # Missing layer thickness

# CORRECT:
cv_soil = csol[i, j] * dz[i, j]  # Include depth
```

---

## Quick Start (3 Commands!)

### Option 1: Automated Script (Easiest!)

```bash
cd /burg-archive/home/mck2199/jax-agents
./test_repair_agent.sh
```

That's it! The script does everything automatically.

---

### Option 2: Manual Steps

```bash
cd /burg-archive/home/mck2199/jax-agents

# Step 1: Generate test failures
python translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  > translated_modules/SoilTemperatureMod/tests/test_failure_output.txt 2>&1

# Step 2: Run repair agent
python examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90 \
  --python translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  --test-report translated_modules/SoilTemperatureMod/tests/test_failure_output.txt \
  --max-iterations 5 \
  -o repair_test_outputs

# Step 3: Check results
cat repair_test_outputs/root_cause_analysis_SoilTemperatureMod.md
```

---

### Option 3: Interactive Mode

```bash
cd /burg-archive/home/mck2199/jax-agents
python examples/repair_agent_example.py --interactive
```

Then enter:
- Module: `SoilTemperatureMod`
- Fortran: `translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90`
- Python: `translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py`
- Test report: `translated_modules/SoilTemperatureMod/tests/test_failure_output.txt`
- Max iterations: `5`

---

## What to Expect

### Test Failures (Step 1)
```
✓ test_thermal_conductivity_basic FAILED as expected
✓ test_thermal_conductivity_first_column FAILED as expected
✓ test_heat_capacity_basic FAILED as expected
✓ test_heat_capacity_first_column FAILED as expected
✓ test_thermal_conductivity_correct_formula FAILED as expected
```

All 5 tests should fail! ✓

### Repair Agent Output (Step 2)

The repair agent will:
1. **Analyze** the failures
2. **Identify** the 5 bugs
3. **Generate** corrected code
4. **Create** root cause analysis
5. **Save** all outputs

### Final Results (Step 3)

Check these files in `repair_test_outputs/`:

```bash
# Corrected Python code
cat repair_test_outputs/SoilTemperatureMod_corrected.py

# Root Cause Analysis (markdown)
cat repair_test_outputs/root_cause_analysis_SoilTemperatureMod.md

# Failure Analysis (JSON)
cat repair_test_outputs/failure_analysis_SoilTemperatureMod.json

# Final test report
cat repair_test_outputs/final_test_report_SoilTemperatureMod.txt
```

---

## Expected Repair Agent Behavior

### Iteration 1: Identify Indexing Issues
- Detects `range(1, n_columns)` problem
- Sees first column is all zeros
- Identifies missing array elements

### Iteration 2: Fix Formulas
- Corrects thermal conductivity formula
- Adds missing `dz` multiplication
- Fixes array index offsets

### Iteration 3: Verify (if needed)
- All tests should pass
- Generates final RCA report

---

## Success Criteria

The repair is successful when:

✅ **All 5 tests pass** in corrected code  
✅ **First column** has non-zero values  
✅ **Thermal conductivity** uses Johansen formula  
✅ **Heat capacity** includes depth multiplication  
✅ **No index errors** (`i-1` fixed to `i`)  

---

## Root Cause Analysis Expected Content

The RCA report should include:

1. **Executive Summary**
   - 5 bugs found and fixed
   - Primary issue: Fortran 1-based → Python 0-based indexing

2. **Failure Analysis**
   - Which tests failed
   - Error messages (first column zeros, wrong values)

3. **Root Causes**
   - Off-by-one indexing (most critical)
   - Wrong array index with offset
   - Incorrect formula implementation
   - Missing depth multiplication

4. **Fix Implementation**
   - Changed `range(1, n)` to `range(n)`
   - Fixed `watsat[i-1, j]` to `watsat[i, j]`
   - Corrected Johansen formula
   - Added `dz` multiplication

5. **Lessons Learned**
   - Always use `range(n)` in Python (not `range(1, n+1)`)
   - Never use `array[i-1]` unless there's a specific reason
   - Verify formulas match Fortran exactly
   - Test boundary conditions (first/last elements)

---

## Detailed Guide

For complete instructions, see:
```
translated_modules/SoilTemperatureMod/tests/REPAIR_AGENT_TEST_GUIDE.md
```

This contains:
- Detailed explanations of each bug
- Step-by-step manual process
- Troubleshooting tips
- Success verification steps
- Common translation error patterns

---

## Quick Command Reference

```bash
# Method 1: Automated (recommended)
./test_repair_agent.sh

# Method 2: Step-by-step
cd translated_modules/SoilTemperatureMod/tests
python test_SoilTemperatureMod_FAILING.py > test_failure_output.txt 2>&1
cd -
python examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90 \
  --python translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  --test-report translated_modules/SoilTemperatureMod/tests/test_failure_output.txt \
  --max-iterations 5

# Method 3: Interactive
python examples/repair_agent_example.py --interactive
```

---

## Verification

After repair, verify the fix:

```bash
# Extract just the functions from corrected code
# (The test file has the test cases at the bottom)

# Or copy corrected code and run it
python repair_test_outputs/SoilTemperatureMod_corrected.py
```

All tests should **PASS**! ✓

---

## Cost Estimate

Expected costs for this repair:
- **Simple bugs** (iterations 1-2): ~$0.20 - $0.40
- **All bugs fixed** (iterations 3-5): ~$0.40 - $0.80

This is a great value for automated debugging! 💰

---

## What Makes This a Good Test Case

✅ **Realistic bugs** - Common Fortran → Python translation errors  
✅ **Multiple bug types** - Indexing, formulas, logic  
✅ **Clear reference** - Fortran code shows correct implementation  
✅ **Verifiable fixes** - Tests confirm when bugs are fixed  
✅ **Educational** - Demonstrates common pitfalls  

---

## Next Steps

1. **Run the test:**
   ```bash
   ./test_repair_agent.sh
   ```

2. **Review the results:**
   ```bash
   ls -lh repair_test_outputs/
   ```

3. **Read the RCA:**
   ```bash
   cat repair_test_outputs/root_cause_analysis_SoilTemperatureMod.md
   ```

4. **Verify the fix:**
   - Compare buggy vs corrected code
   - Check that all 5 bugs are fixed
   - Verify tests would pass

---

## Troubleshooting

### If script fails:
```bash
# Check Python path
which python

# Check if files exist
ls -l translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py

# Check API key
echo $ANTHROPIC_API_KEY
```

### If repair doesn't fix all bugs:
- Increase `--max-iterations` to 10
- Check if test failure report is complete
- Review intermediate outputs

---

## Summary

✅ **Failing test created** with 5 intentional bugs  
✅ **Fortran reference** provided for comparison  
✅ **Complete guide** with detailed instructions  
✅ **Automated script** for easy testing  
✅ **All files verified** and ready to use  

🎉 **Everything is ready! Just run `./test_repair_agent.sh`**

---

**Happy Testing!** 🚀

The repair agent will demonstrate its ability to:
- 🔍 Analyze complex test failures
- 🐛 Identify multiple bug types
- 🔧 Generate correct fixes
- 📝 Explain root causes
- ✅ Verify solutions work

