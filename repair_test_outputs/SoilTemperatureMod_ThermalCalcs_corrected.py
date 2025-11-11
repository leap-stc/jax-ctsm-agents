"""
Corrected SoilTemperatureMod - Thermal conductivity and heat capacity calculations

This module contains the corrected implementations of soil thermal property calculations,
fixing all indexing errors and formula bugs from the original translation.
"""

import jax.numpy as jnp
from typing import Tuple


def calculate_soil_thermal_conductivity(
    h2osoi_liq: jnp.ndarray,
    h2osoi_ice: jnp.ndarray,
    watsat: jnp.ndarray,
    tkmg: jnp.ndarray,
    tkdry: jnp.ndarray,
) -> jnp.ndarray:
    """
    Calculate soil thermal conductivity using Johansen (1975) model.
    
    Implements the thermal conductivity as a function of soil saturation:
    tk = tkdry + sat * (tkmg - tkdry)
    
    where saturation is computed from liquid water and ice content.
    
    Args:
        h2osoi_liq: Liquid water content [kg/m²] shape (n_columns, n_levels)
        h2osoi_ice: Ice content [kg/m²] shape (n_columns, n_levels)
        watsat: Volumetric soil water at saturation [-] shape (n_columns, n_levels)
        tkmg: Thermal conductivity of saturated soil [W/m/K] shape (n_columns, n_levels)
        tkdry: Thermal conductivity of dry soil [W/m/K] shape (n_columns, n_levels)
        
    Returns:
        Thermal conductivity [W/m/K] shape (n_columns, n_levels)
    """
    n_columns, n_levels = h2osoi_liq.shape
    tk = jnp.zeros((n_columns, n_levels))
    
    # FIX 1: Changed from range(1, n_columns) to range(n_columns)
    # Python uses 0-based indexing, so we must start at 0 to process all columns
    for i in range(n_columns):
        for j in range(n_levels):
            # Calculate saturation
            # FIX 2: Changed from watsat[i-1, j] to watsat[i, j]
            # Correct indexing - no offset needed in Python's 0-based system
            sat = (h2osoi_liq[i, j] + h2osoi_ice[i, j]) / watsat[i, j]
            sat = jnp.clip(sat, 0.0, 1.0)
            
            # FIX 3: Corrected Johansen (1975) formula
            # Changed from: tkdry[i, j] + sat * tkmg[i, j]
            # To: tkdry[i, j] + sat * (tkmg[i, j] - tkdry[i, j])
            # This ensures: when sat=0, tk=tkdry; when sat=1, tk=tkmg
            tk = tk.at[i, j].set(tkdry[i, j] + sat * (tkmg[i, j] - tkdry[i, j]))
    
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
    Calculate volumetric heat capacity of soil layers.
    
    Computes total heat capacity as sum of contributions from:
    - Soil solids (csol * dz)
    - Liquid water (h2osoi_liq * cpliq)
    - Ice (h2osoi_ice * cpice)
    
    Args:
        h2osoi_liq: Liquid water content [kg/m²] shape (n_columns, n_levels)
        h2osoi_ice: Ice content [kg/m²] shape (n_columns, n_levels)
        csol: Soil solids heat capacity [J/m³/K] shape (n_columns, n_levels)
        dz: Layer thickness [m] shape (n_columns, n_levels)
        cpliq: Specific heat of liquid water [J/kg/K]
        cpice: Specific heat of ice [J/kg/K]
        
    Returns:
        Volumetric heat capacity [J/m²/K] shape (n_columns, n_levels)
    """
    n_columns, n_levels = h2osoi_liq.shape
    cv = jnp.zeros((n_columns, n_levels))
    
    # FIX 4: Changed from range(1, n_columns) to range(n_columns)
    # Must start at 0 to process all columns including the first one
    for i in range(n_columns):
        for j in range(n_levels):
            # FIX 5: Added dz multiplication for correct units
            # Changed from: cv_soil = csol[i, j]
            # To: cv_soil = csol[i, j] * dz[i, j]
            # csol is [J/m³/K], dz is [m], product is [J/m²/K]
            cv_soil = csol[i, j] * dz[i, j]
            
            # Water contribution [J/m²/K]
            # h2osoi_liq is [kg/m²], cpliq is [J/kg/K], product is [J/m²/K]
            cv_water = h2osoi_liq[i, j] * cpliq
            
            # Ice contribution [J/m²/K]
            # h2osoi_ice is [kg/m²], cpice is [J/kg/K], product is [J/m²/K]
            cv_ice = h2osoi_ice[i, j] * cpice
            
            # Total volumetric heat capacity
            cv = cv.at[i, j].set(cv_soil + cv_water + cv_ice)
    
    return cv


# ============================================================================
# TEST CASES - These should now PASS with the corrected implementation
# ============================================================================

def test_thermal_conductivity_basic():
    """Test basic thermal conductivity calculation."""
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
    
    assert result.shape == (n_columns, n_levels), "Shape mismatch"
    assert jnp.all(result > 0), "All values should be non-zero"
    assert jnp.all(result < 10), "Conductivity should be reasonable"


def test_thermal_conductivity_first_column():
    """Test that first column is processed correctly."""
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
    
    assert jnp.all(result[0, :] > 0), "First column values should be non-zero"
    

def test_heat_capacity_basic():
    """Test basic heat capacity calculation."""
    n_columns = 3
    n_levels = 4
    
    h2osoi_liq = jnp.ones((n_columns, n_levels)) * 20.0
    h2osoi_ice = jnp.ones((n_columns, n_levels)) * 10.0
    csol = jnp.ones((n_columns, n_levels)) * 2e6
    dz = jnp.ones((n_columns, n_levels)) * 0.1
    
    result = calculate_heat_capacity(h2osoi_liq, h2osoi_ice, csol, dz)
    
    assert result.shape == (n_columns, n_levels)
    assert jnp.all(result > 0), "All values should be non-zero"


def test_heat_capacity_first_column():
    """Test that first column has correct values."""
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
    
    assert result[0, 0] > 0, f"First element should be non-zero, got {result[0, 0]}"
    assert result[0, 1] > 0, f"First element should be non-zero, got {result[0, 1]}"


def test_thermal_conductivity_correct_formula():
    """Test that thermal conductivity uses correct Johansen formula."""
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
    
    # With zero saturation, should equal tkdry
    expected_approx = 0.5
    assert jnp.abs(result[0, 0] - expected_approx) < 0.01, \
        f"Expected ~{expected_approx}, got {result[0, 0]}"
    assert jnp.abs(result[1, 0] - expected_approx) < 0.01, \
        f"Expected ~{expected_approx}, got {result[1, 0]}"


if __name__ == "__main__":
    # Run tests to verify corrections
    print("Running corrected tests...")
    print("=" * 80)
    
    try:
        test_thermal_conductivity_basic()
        print("✓ test_thermal_conductivity_basic PASSED")
    except AssertionError as e:
        print(f"✗ test_thermal_conductivity_basic FAILED: {e}")
    
    try:
        test_thermal_conductivity_first_column()
        print("✓ test_thermal_conductivity_first_column PASSED")
    except AssertionError as e:
        print(f"✗ test_thermal_conductivity_first_column FAILED: {e}")
    
    try:
        test_heat_capacity_basic()
        print("✓ test_heat_capacity_basic PASSED")
    except AssertionError as e:
        print(f"✗ test_heat_capacity_basic FAILED: {e}")
    
    try:
        test_heat_capacity_first_column()
        print("✓ test_heat_capacity_first_column PASSED")
    except AssertionError as e:
        print(f"✗ test_heat_capacity_first_column FAILED: {e}")
    
    try:
        test_thermal_conductivity_correct_formula()
        print("✓ test_thermal_conductivity_correct_formula PASSED")
    except AssertionError as e:
        print(f"✗ test_thermal_conductivity_correct_formula FAILED: {e}")
    
    print("=" * 80)
    print("\nAll tests should now pass with corrected implementation!")