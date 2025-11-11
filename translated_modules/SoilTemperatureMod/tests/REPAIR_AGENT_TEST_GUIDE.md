# Testing the Repair Agent with SoilTemperatureMod

This guide shows you how to test the Repair Agent using the intentionally failing SoilTemperatureMod tests.

## What We Created

### 1. `test_SoilTemperatureMod_FAILING.py`
A test file with **intentional bugs** to demonstrate repair agent capabilities:

**Bugs Included:**
- **Bug 1**: Off-by-one indexing (starts loop at 1 instead of 0) - Fortran vs Python indexing
- **Bug 2**: Wrong array index (`[i-1, j]` instead of `[i, j]`)
- **Bug 3**: Incorrect thermal conductivity formula
- **Bug 4**: Skipping first column in heat capacity calculation  
- **Bug 5**: Missing depth (`dz`) multiplication in heat capacity

### 2. `FORTRAN_REFERENCE.F90`
Reference Fortran code showing the CORRECT implementation

### 3. This Guide
Step-by-step instructions for testing the repair agent

---

## Quick Start

### Step 1: Run the Failing Tests

```bash
cd /burg-archive/home/mck2199/jax-agents/translated_modules/SoilTemperatureMod/tests

# Run tests and save output
pytest test_SoilTemperatureMod_FAILING.py -v --tb=short > test_failure_output.txt 2>&1

# Or run the Python file directly
python test_SoilTemperatureMod_FAILING.py > test_failure_output.txt 2>&1
```

Expected output: **All 5 tests should FAIL**

### Step 2: Use Repair Agent to Fix

```bash
cd /burg-archive/home/mck2199/jax-agents

# Run repair agent with the failing code
python examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90 \
  --python translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  --test-report translated_modules/SoilTemperatureMod/tests/test_failure_output.txt \
  --test-file translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  --max-iterations 5 \
  -o repair_test_outputs
```

### Step 3: Review the Repair

Check the repair agent's outputs:

```bash
cd repair_test_outputs

# View corrected code
cat SoilTemperatureMod_corrected.py

# View root cause analysis
cat root_cause_analysis_SoilTemperatureMod.md

# View failure analysis
cat failure_analysis_SoilTemperatureMod.json
```

---

## Detailed Instructions

### Option 1: Manual Step-by-Step

#### 1. Generate Test Failure Report

```bash
cd /burg-archive/home/mck2199/jax-agents/translated_modules/SoilTemperatureMod/tests

# Run with pytest
pytest test_SoilTemperatureMod_FAILING.py -v --tb=short > test_failure_output.txt 2>&1

# Verify failures
cat test_failure_output.txt
```

You should see output like:
```
test_SoilTemperatureMod_FAILING.py::test_thermal_conductivity_basic FAILED
test_SoilTemperatureMod_FAILING.py::test_thermal_conductivity_first_column FAILED
test_SoilTemperatureMod_FAILING.py::test_heat_capacity_basic FAILED
test_SoilTemperatureMod_FAILING.py::test_heat_capacity_first_column FAILED
test_SoilTemperatureMod_FAILING.py::test_thermal_conductivity_correct_formula FAILED
```

#### 2. Read the Files

```bash
# Original Fortran (correct implementation)
cat FORTRAN_REFERENCE.F90

# Buggy Python code (to be fixed)
cat test_SoilTemperatureMod_FAILING.py

# Test failures
cat test_failure_output.txt
```

#### 3. Run Repair Agent

```bash
cd /burg-archive/home/mck2199/jax-agents

python examples/repair_agent_example.py \
  --module SoilTemperatureMod_ThermalCalcs \
  --fortran translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90 \
  --python translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py \
  --test-report translated_modules/SoilTemperatureMod/tests/test_failure_output.txt \
  --max-iterations 10 \
  -o repair_test_outputs
```

#### 4. Examine Repair Results

```bash
cd repair_test_outputs

# See what the agent fixed
head -100 SoilTemperatureMod_ThermalCalcs_corrected.py

# Read the root cause analysis
less root_cause_analysis_SoilTemperatureMod_ThermalCalcs.md

# See structured failure data
cat failure_analysis_SoilTemperatureMod_ThermalCalcs.json | python -m json.tool
```

---

### Option 2: Interactive Mode

```bash
cd /burg-archive/home/mck2199/jax-agents

python examples/repair_agent_example.py --interactive
```

Then enter when prompted:
- **Module name**: `SoilTemperatureMod_ThermalCalcs`
- **Fortran file**: `translated_modules/SoilTemperatureMod/tests/FORTRAN_REFERENCE.F90`
- **Python file**: `translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py`
- **Test report**: `translated_modules/SoilTemperatureMod/tests/test_failure_output.txt`
- **Test file** (optional): `translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FAILING.py`
- **Output dir**: `repair_test_outputs`
- **Max iterations**: `10`

---

## What the Repair Agent Should Fix

The repair agent should identify and fix these issues:

### Bug 1: Off-by-One Indexing
**Wrong:**
```python
for i in range(1, n_columns):  # Skips first column!
```
**Correct:**
```python
for i in range(n_columns):  # Process all columns
```

### Bug 2: Wrong Array Index
**Wrong:**
```python
sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i-1, j]  # Wrong index!
```
**Correct:**
```python
sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i, j]  # Correct index
```

### Bug 3: Wrong Formula
**Wrong:**
```python
tk = tk.at[i, j].set(tkdry[i, j] + sat * tkmg[i, j])  # Wrong formula
```
**Correct:**
```python
tk = tk.at[i, j].set(tkdry[i, j] + sat * (tkmg[i, j] - tkdry[i, j]))  # Johansen formula
```

### Bug 4: Skipping First Column (Heat Capacity)
**Wrong:**
```python
for i in range(1, n_columns):  # Skips first column
```
**Correct:**
```python
for i in range(n_columns):  # All columns
```

### Bug 5: Missing Depth Multiplication
**Wrong:**
```python
cv_soil = csol[i, j]  # Missing dz multiplication
```
**Correct:**
```python
cv_soil = csol[i, j] * dz[i, j]  # Include layer thickness
```

---

## Expected Repair Agent Behavior

### Iteration 1
- Analyzes test failures
- Identifies off-by-one indexing errors
- Recognizes first column is all zeros
- Generates initial fix

### Iteration 2 (if needed)
- Re-analyzes remaining failures
- Identifies formula errors
- Fixes thermal conductivity calculation

### Iteration 3 (if needed)
- Fixes any remaining issues
- Verifies all tests pass

### Final Output
- **Corrected Python code** with all bugs fixed
- **Root Cause Analysis** explaining:
  - What went wrong
  - Why it went wrong (Fortran vs Python indexing)
  - How it was fixed
  - Lessons learned
- **Test verification** showing all tests now pass

---

## Verification

After repair, verify the fix:

```bash
cd repair_test_outputs

# Copy corrected code
cp SoilTemperatureMod_ThermalCalcs_corrected.py \
   ../translated_modules/SoilTemperatureMod/tests/test_SoilTemperatureMod_FIXED.py

# Run tests on corrected code
cd ../translated_modules/SoilTemperatureMod/tests
python test_SoilTemperatureMod_FIXED.py
```

All tests should now **PASS**!

---

## Understanding the Bugs

### Common Translation Errors

1. **Fortran 1-based vs Python 0-based indexing**
   - Fortran: `do i = 1, n` processes indices 1 to n
   - Python: `for i in range(n)` processes indices 0 to n-1
   - **Never** use `range(1, n)` unless you intentionally want to skip the first element!

2. **Array indexing offsets**
   - When translating `array(i)` from Fortran to Python
   - If Fortran loop is `do i = 1, n`, Python should be `for i in range(n)` with `array[i]`
   - NOT `for i in range(1, n+1)` with `array[i-1]`

3. **Formula translation**
   - Carefully check mathematical formulas
   - Fortran: `tk = tkdry + sat * (tkmg - tkdry)`
   - Python: Same formula, but watch operator precedence

4. **Unit conversions**
   - Check if layer thickness (dz) should be included
   - Volumetric vs areal quantities

---

## Expected Root Cause Analysis

The repair agent should generate an RCA report explaining:

1. **Executive Summary**
   - 5 tests failed due to indexing and formula errors
   - Critical: First column not processed (all zeros)
   - Root cause: Direct translation from Fortran without index adjustment

2. **Failure Analysis**
   - `test_thermal_conductivity_basic`: First column all zeros
   - `test_thermal_conductivity_first_column`: Explicit check for first column values failed
   - Formula tests: Wrong thermal conductivity values

3. **Root Cause**
   - **Primary**: Loop starts at 1 instead of 0 (Fortran → Python translation error)
   - **Secondary**: Wrong array indexing with offset
   - **Tertiary**: Incorrect formula implementation

4. **Fix Implementation**
   - Changed `range(1, n_columns)` to `range(n_columns)`
   - Fixed array index from `watsat[i-1, j]` to `watsat[i, j]`
   - Corrected thermal conductivity formula
   - Added `dz` multiplication for heat capacity

5. **Lessons Learned**
   - Always start Python loops at 0
   - Never use `i-1` indexing unless there's a specific reason
   - Verify formulas match Fortran exactly
   - Test first column/row explicitly to catch indexing bugs

---

## Success Criteria

The repair is successful when:

✅ All 5 tests pass  
✅ First column values are non-zero  
✅ Thermal conductivity formula is correct  
✅ Heat capacity includes all components  
✅ No indexing errors remain  

---

## Troubleshooting

### If repair agent doesn't fix all bugs in first iteration:

1. **Check max iterations** - Increase to 10-15 for complex issues
2. **Review failure analysis** - See if agent identified all bugs
3. **Run again** - Sometimes needs multiple passes

### If tests still fail after repair:

1. **Check the corrected code** - Manually review changes
2. **Compare with Fortran reference** - Line by line comparison
3. **Run individual tests** - Isolate which bugs remain

### If repair agent makes wrong changes:

1. **Improve test report** - Add more specific error messages
2. **Add more test cases** - Cover edge cases explicitly
3. **Review Fortran reference** - Ensure it's accurate

---

## Files Summary

| File | Purpose | Contains |
|------|---------|----------|
| `test_SoilTemperatureMod_FAILING.py` | Buggy code | 5 intentional bugs |
| `FORTRAN_REFERENCE.F90` | Reference | Correct Fortran implementation |
| `test_failure_output.txt` | Test results | Pytest failure output |
| `REPAIR_AGENT_TEST_GUIDE.md` | This file | Complete testing guide |

---

## Next Steps

1. **Run the test** to generate failure output
2. **Use repair agent** to fix the bugs
3. **Review RCA report** to understand what was fixed
4. **Verify fix** by running tests again
5. **Compare** original buggy vs corrected code

This provides a complete end-to-end test of the repair agent's capabilities!

---

## Quick Command Reference

```bash
# Generate failures
pytest test_SoilTemperatureMod_FAILING.py -v --tb=short > test_failure_output.txt 2>&1

# Repair with agent
python ../../examples/repair_agent_example.py \
  --module SoilTemperatureMod \
  --fortran FORTRAN_REFERENCE.F90 \
  --python test_SoilTemperatureMod_FAILING.py \
  --test-report test_failure_output.txt \
  --max-iterations 10

# Verify repair
python repair_outputs/SoilTemperatureMod_corrected.py
```

🎉 **Happy Testing!**

