#!/bin/bash
# Quick script to test the Repair Agent with intentionally failing SoilTemperatureMod tests

set -e  # Exit on error

echo "=========================================="
echo "Testing Repair Agent with SoilTemperatureMod"
echo "=========================================="
echo ""

# Set paths
TEST_DIR="translated_modules/SoilTemperatureMod/tests"
FAILING_TEST="$TEST_DIR/test_SoilTemperatureMod_FAILING.py"
FORTRAN_REF="$TEST_DIR/FORTRAN_REFERENCE.F90"
FAILURE_OUTPUT="$TEST_DIR/test_failure_output.txt"
REPAIR_OUTPUT="repair_test_outputs"

# Step 1: Run failing tests
echo "Step 1: Running failing tests to generate failure report..."
echo "----------------------------------------"
cd "$TEST_DIR"
python test_SoilTemperatureMod_FAILING.py > test_failure_output.txt 2>&1 || true
cd - > /dev/null
echo "✓ Test failure report generated"
echo ""

# Show some failures
echo "Sample failures (first 30 lines):"
echo "----------------------------------------"
head -30 "$FAILURE_OUTPUT"
echo "..."
echo ""

# Step 2: Run repair agent
echo "Step 2: Running repair agent..."
echo "----------------------------------------"
python examples/repair_agent_example.py \
  --module SoilTemperatureMod_ThermalCalcs \
  --fortran "$FORTRAN_REF" \
  --python "$FAILING_TEST" \
  --test-report "$FAILURE_OUTPUT" \
  --max-iterations 5 \
  -o "$REPAIR_OUTPUT"

echo ""
echo "=========================================="
echo "Repair Complete!"
echo "=========================================="
echo ""
echo "Results saved to: $REPAIR_OUTPUT/"
echo ""
echo "Files created:"
ls -lh "$REPAIR_OUTPUT/"
echo ""
echo "View results:"
echo "  - Corrected code:      cat $REPAIR_OUTPUT/SoilTemperatureMod_ThermalCalcs_corrected.py"
echo "  - Root cause analysis: cat $REPAIR_OUTPUT/root_cause_analysis_SoilTemperatureMod_ThermalCalcs.md"
echo "  - Failure analysis:    cat $REPAIR_OUTPUT/failure_analysis_SoilTemperatureMod_ThermalCalcs.json"
echo ""
echo "✓ Test complete!"

