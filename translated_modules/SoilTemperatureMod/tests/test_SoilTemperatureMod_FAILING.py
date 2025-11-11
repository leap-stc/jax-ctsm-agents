"""
INTENTIONALLY FAILING test for SoilTemperatureMod - FOR REPAIR AGENT TESTING

This test file contains intentional bugs to test the repair agent's ability to:
1. Detect indexing errors (Fortran 1-based vs Python 0-based)
2. Identify incorrect array operations
3. Fix logic errors
4. Generate correct code

DO NOT USE THIS IN PRODUCTION - This is for testing the repair agent only!
"""

import pytest
import jax.numpy as jnp
import numpy as np
from typing import Tuple


def calculate_soil_thermal_conductivity(
    h2osoi_liq: jnp.ndarray,
    h2osoi_ice: jnp.ndarray,
    watsat: jnp.ndarray,
    tkmg: jnp.ndarray,
    tkdry: jnp.ndarray,
) -> jnp.ndarray:
    """
    Calculate soil thermal conductivity (BUGGY VERSION for repair agent testing).
    
    This function has INTENTIONAL BUGS:
    - BUG 1: Off-by-one error in loop indexing (line 35)
    - BUG 2: Wrong array indexing (line 39)
    - BUG 3: Incorrect computation formula (line 42)
    
    Args:
        h2osoi_liq: Liquid water content [kg/m²] shape (n_columns, n_levels)
        h2osoi_ice: Ice content [kg/m²] shape (n_columns, n_levels)
        watsat: Volumetric soil water at saturation [-] shape (n_columns, n_levels)
        tkmg: Thermal conductivity of soil minerals [W/m/K] shape (n_columns, n_levels)
        tkdry: Thermal conductivity of dry soil [W/m/K] shape (n_columns, n_levels)
        
    Returns:
        Thermal conductivity [W/m/K] shape (n_columns, n_levels)
    """
    n_columns, n_levels = h2osoi_liq.shape
    tk = jnp.zeros((n_columns, n_levels))
    
    # BUG 1: Starting loop from 1 instead of 0 (Fortran-style indexing in Python)
    for i in range(1, n_columns):  # WRONG: Should be range(n_columns)
        for j in range(n_levels):
            # Calculate saturation
            # BUG 2: Using wrong index for watsat (should be [i, j] not [i-1, j])
            sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i-1, j]  # WRONG INDEX
            sat = jnp.clip(sat, 0.0, 1.0)
            
            # BUG 3: Wrong formula (using addition instead of proper Johansen formula)
            tk = tk.at[i, j].set(tkdry[i, j] + sat * tkmg[i, j])  # WRONG FORMULA
    
    return tk


def calculate_heat_capacity(
    h2osoi_liq: jnp.ndarray,
    h2osoi_ice: jnp.ndarray,
    csol: jnp.ndarray,
    dz: jnp.ndarray,
    cpliq: float = 4188.0,
    cpice: float = 2117.27,
) -> jnp.ndarray:
    """
    Calculate volumetric heat capacity (BUGGY VERSION).
    
    INTENTIONAL BUGS:
    - BUG 4: Missing first column in calculation
    - BUG 5: Wrong units conversion
    
    Args:
        h2osoi_liq: Liquid water content [kg/m²]
        h2osoi_ice: Ice content [kg/m²]
        csol: Soil solids heat capacity [J/m³/K]
        dz: Layer thickness [m]
        cpliq: Specific heat of liquid water [J/kg/K]
        cpice: Specific heat of ice [J/kg/K]
        
    Returns:
        Volumetric heat capacity [J/m²/K]
    """
    n_columns, n_levels = h2osoi_liq.shape
    cv = jnp.zeros((n_columns, n_levels))
    
    # BUG 4: Starting from column 1 instead of 0
    for i in range(1, n_columns):  # WRONG: Skips first column
        for j in range(n_levels):
            # BUG 5: Wrong formula - missing dz multiplication for csol
            cv_soil = csol[i, j]  # WRONG: Should be csol[i, j] * dz[i, j]
            cv_water = h2osoi_liq[i, j] * cpliq
            cv_ice = h2osoi_ice[i, j] * cpice
            
            cv = cv.at[i, j].set(cv_soil + cv_water + cv_ice)
    
    return cv


# ============================================================================
# TEST CASES - These will FAIL due to the bugs above
# ============================================================================

def test_thermal_conductivity_basic():
    """Test basic thermal conductivity calculation - WILL FAIL."""
    n_columns = 3
    n_levels = 5
    
    # Create test data
    h2osoi_liq = jnp.ones((n_columns, n_levels)) * 10.0
    h2osoi_ice = jnp.ones((n_columns, n_levels)) * 5.0
    watsat = jnp.ones((n_columns, n_levels)) * 0.5
    tkmg = jnp.ones((n_columns, n_levels)) * 2.0
    tkdry = jnp.ones((n_columns, n_levels)) * 0.3
    
    result = calculate_soil_thermal_conductivity(
        h2osoi_liq, h2osoi_ice, watsat, tkmg, tkdry
    )
    
    # This will FAIL because first column is all zeros (bug 1)
    assert result.shape == (n_columns, n_levels), "Shape mismatch"
    assert jnp.all(result > 0), "First column should not be zero!"  # FAILS HERE
    assert jnp.all(result < 10), "Conductivity should be reasonable"


def test_thermal_conductivity_first_column():
    """Test that first column is processed - WILL FAIL."""
    n_columns = 2
    n_levels = 3
    
    h2osoi_liq = jnp.array([[10.0, 10.0, 10.0],
                             [10.0, 10.0, 10.0]])
    h2osoi_ice = jnp.array([[5.0, 5.0, 5.0],
                             [5.0, 5.0, 5.0]])
    watsat = jnp.array([[0.5, 0.5, 0.5],
                        [0.5, 0.5, 0.5]])
    tkmg = jnp.array([[2.0, 2.0, 2.0],
                      [2.0, 2.0, 2.0]])
    tkdry = jnp.array([[0.3, 0.3, 0.3],
                       [0.3, 0.3, 0.3]])
    
    result = calculate_soil_thermal_conductivity(
        h2osoi_liq, h2osoi_ice, watsat, tkmg, tkdry
    )
    
    # This will FAIL - first row is all zeros due to bug 1
    assert jnp.all(result[0, :] > 0), "First column values should be non-zero!"  # FAILS
    

def test_heat_capacity_basic():
    """Test basic heat capacity calculation - WILL FAIL."""
    n_columns = 3
    n_levels = 4
    
    h2osoi_liq = jnp.ones((n_columns, n_levels)) * 20.0
    h2osoi_ice = jnp.ones((n_columns, n_levels)) * 10.0
    csol = jnp.ones((n_columns, n_levels)) * 2e6
    dz = jnp.ones((n_columns, n_levels)) * 0.1
    
    result = calculate_heat_capacity(h2osoi_liq, h2osoi_ice, csol, dz)
    
    # This will FAIL because first column is zeros (bug 4)
    assert result.shape == (n_columns, n_levels)
    assert jnp.all(result > 0), "First column should not be zero!"  # FAILS HERE


def test_heat_capacity_first_column():
    """Test that first column has correct values - WILL FAIL."""
    n_columns = 2
    n_levels = 2
    
    h2osoi_liq = jnp.array([[20.0, 20.0],
                             [20.0, 20.0]])
    h2osoi_ice = jnp.array([[10.0, 10.0],
                             [10.0, 10.0]])
    csol = jnp.array([[2e6, 2e6],
                      [2e6, 2e6]])
    dz = jnp.array([[0.1, 0.1],
                    [0.1, 0.1]])
    
    result = calculate_heat_capacity(h2osoi_liq, h2osoi_ice, csol, dz)
    
    # First column should have non-zero values
    assert result[0, 0] > 0, f"First element should be non-zero, got {result[0, 0]}"  # FAILS
    assert result[0, 1] > 0, f"First element should be non-zero, got {result[0, 1]}"  # FAILS


def test_thermal_conductivity_correct_formula():
    """Test that thermal conductivity uses correct formula - WILL FAIL."""
    n_columns = 2
    n_levels = 2
    
    # Setup where we know the answer
    h2osoi_liq = jnp.array([[0.0, 0.0], [0.0, 0.0]])
    h2osoi_ice = jnp.array([[0.0, 0.0], [0.0, 0.0]])
    watsat = jnp.array([[0.5, 0.5], [0.5, 0.5]])
    tkmg = jnp.array([[2.0, 2.0], [2.0, 2.0]])
    tkdry = jnp.array([[0.5, 0.5], [0.5, 0.5]])
    
    result = calculate_soil_thermal_conductivity(
        h2osoi_liq, h2osoi_ice, watsat, tkmg, tkdry
    )
    
    # With zero saturation, should be approximately tkdry
    # But due to bug 3, it will be wrong
    expected_approx = 0.5  # Should be close to tkdry when dry
    assert jnp.abs(result[1, 0] - expected_approx) < 0.1, \
        f"Expected ~{expected_approx}, got {result[1, 0]}"  # WILL FAIL due to wrong formula


if __name__ == "__main__":
    # Run tests to see failures
    print("Running intentionally failing tests...")
    print("=" * 80)
    
    try:
        test_thermal_conductivity_basic()
        print("✗ test_thermal_conductivity_basic PASSED (should have failed!)")
    except AssertionError as e:
        print(f"✓ test_thermal_conductivity_basic FAILED as expected: {e}")
    
    try:
        test_thermal_conductivity_first_column()
        print("✗ test_thermal_conductivity_first_column PASSED (should have failed!)")
    except AssertionError as e:
        print(f"✓ test_thermal_conductivity_first_column FAILED as expected: {e}")
    
    try:
        test_heat_capacity_basic()
        print("✗ test_heat_capacity_basic PASSED (should have failed!)")
    except AssertionError as e:
        print(f"✓ test_heat_capacity_basic FAILED as expected: {e}")
    
    try:
        test_heat_capacity_first_column()
        print("✗ test_heat_capacity_first_column PASSED (should have failed!)")
    except AssertionError as e:
        print(f"✓ test_heat_capacity_first_column FAILED as expected: {e}")
    
    try:
        test_thermal_conductivity_correct_formula()
        print("✗ test_thermal_conductivity_correct_formula PASSED (should have failed!)")
    except AssertionError as e:
        print(f"✓ test_thermal_conductivity_correct_formula FAILED as expected: {e}")
    
    print("=" * 80)
    print("\nAll tests failed as expected! Ready for repair agent testing.")

