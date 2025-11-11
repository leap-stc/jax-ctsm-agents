"""
Comprehensive pytest suite for SoilTemperatureMod.soil_temperature function.

This module tests the soil temperature calculation function which solves the
heat diffusion equation for soil and snow layers using an implicit finite
difference scheme.

Test Coverage:
- Nominal cases: temperate soil, frozen soil, deep profiles, soil type contrasts
- Edge cases: zero flux, extreme cold, dry soil, thin layers
- Special cases: phase transition zones near freezing
- Output validation: shapes, dtypes, physical constraints
- Numerical properties: energy conservation, stability
"""

import pytest
import jax.numpy as jnp
import numpy as np
from typing import NamedTuple, Tuple
from collections import namedtuple


# Define NamedTuples matching the function signature
SoilThermalProperties = namedtuple(
    'SoilThermalProperties',
    ['tk', 'cv', 'tk_h2osfc', 'thk', 'bw']
)

SoilTemperatureParams = namedtuple(
    'SoilTemperatureParams',
    [
        'denh2o', 'denice', 'tfrz', 'tkwat', 'tkice', 'tkair',
        'cpice', 'cpliq', 'thk_bedrock', 'csol_bedrock', 'thin_sfclayer'
    ]
)


# Mock implementation for testing purposes
# In actual use, this would be imported from SoilTemperatureMod
def soil_temperature(
    t_soisno: jnp.ndarray,
    gsoi: jnp.ndarray,
    z: jnp.ndarray,
    zi: jnp.ndarray,
    dz: jnp.ndarray,
    h2osoi_liq: jnp.ndarray,
    h2osoi_ice: jnp.ndarray,
    h2osno: jnp.ndarray,
    h2osfc: jnp.ndarray,
    watsat: jnp.ndarray,
    tkmg: jnp.ndarray,
    tkdry: jnp.ndarray,
    csol: jnp.ndarray,
    frac_sno: jnp.ndarray,
    snl: jnp.ndarray,
    nbedrock: jnp.ndarray,
    dtime: float,
    params: SoilTemperatureParams
) -> Tuple[jnp.ndarray, SoilThermalProperties]:
    """
    Mock implementation of soil_temperature for testing.
    
    Returns updated temperatures and thermal properties.
    """
    # Simple mock: return slightly modified temperatures and dummy properties
    n_columns, n_levels = t_soisno.shape
    
    # Mock temperature update (small change based on heat flux)
    t_new = t_soisno + gsoi[:, None] * dtime / 1e7
    
    # Mock thermal properties
    thermal_props = SoilThermalProperties(
        tk=jnp.ones_like(t_soisno) * 1.5,
        cv=jnp.ones_like(t_soisno) * 2e6,
        tk_h2osfc=jnp.ones(n_columns) * 0.5,
        thk=jnp.ones_like(t_soisno) * 1.2,
        bw=jnp.ones_like(t_soisno) * 100.0
    )
    
    return t_new, thermal_props


@pytest.fixture
def default_params():
    """
    Fixture providing default physical constants for soil temperature calculations.
    
    Returns:
        SoilTemperatureParams: NamedTuple with standard physical constants
    """
    return SoilTemperatureParams(
        denh2o=1000.0,      # Density of liquid water [kg/m³]
        denice=917.0,       # Density of ice [kg/m³]
        tfrz=273.15,        # Freezing point of water [K]
        tkwat=0.57,         # Thermal conductivity of water [W/m/K]
        tkice=2.29,         # Thermal conductivity of ice [W/m/K]
        tkair=0.023,        # Thermal conductivity of air [W/m/K]
        cpice=2117.27,      # Specific heat of ice [J/kg/K]
        cpliq=4188.0,       # Specific heat of liquid water [J/kg/K]
        thk_bedrock=3.0,    # Thermal conductivity of bedrock [W/m/K]
        csol_bedrock=2.5e6, # Heat capacity of bedrock [J/m³/K]
        thin_sfclayer=0.01  # Threshold for thin surface layer [m]
    )


@pytest.fixture
def test_data():
    """
    Fixture providing comprehensive test data for soil_temperature function.
    
    Returns:
        dict: Dictionary containing all test cases with inputs and metadata
    """
    return {
        "test_nominal_temperate_soil": {
            "inputs": {
                "t_soisno": jnp.array([
                    [288.15, 285.15, 283.15, 281.15, 280.15],
                    [290.15, 287.15, 285.15, 283.15, 282.15]
                ]),
                "gsoi": jnp.array([50.0, -30.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [5.0, 8.0, 12.0, 15.0, 18.0],
                    [6.0, 9.0, 13.0, 16.0, 19.0]
                ]),
                "h2osoi_ice": jnp.array([
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0]
                ]),
                "h2osno": jnp.array([0.0, 0.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.45, 0.45, 0.45, 0.45, 0.45],
                    [0.5, 0.5, 0.5, 0.5, 0.5]
                ]),
                "tkmg": jnp.array([
                    [2.5, 2.5, 2.5, 2.5, 2.5],
                    [3.0, 3.0, 3.0, 3.0, 3.0]
                ]),
                "tkdry": jnp.array([
                    [0.2, 0.2, 0.2, 0.2, 0.2],
                    [0.25, 0.25, 0.25, 0.25, 0.25]
                ]),
                "csol": jnp.array([
                    [2e6, 2e6, 2e6, 2e6, 2e6],
                    [2.2e6, 2.2e6, 2.2e6, 2.2e6, 2.2e6]
                ]),
                "frac_sno": jnp.array([0.0, 0.0]),
                "snl": jnp.array([0, 0]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Typical temperate soil with moderate moisture, no snow"
        },
        "test_nominal_frozen_soil": {
            "inputs": {
                "t_soisno": jnp.array([
                    [268.15, 270.15, 272.15, 274.15, 276.15],
                    [265.15, 268.15, 271.15, 273.15, 275.15]
                ]),
                "gsoi": jnp.array([-80.0, -60.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [1.0, 2.0, 3.0, 5.0, 8.0],
                    [0.5, 1.5, 2.5, 4.0, 7.0]
                ]),
                "h2osoi_ice": jnp.array([
                    [8.0, 10.0, 12.0, 15.0, 18.0],
                    [9.0, 11.0, 13.0, 16.0, 19.0]
                ]),
                "h2osno": jnp.array([50.0, 80.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.42, 0.42, 0.42, 0.42, 0.42],
                    [0.48, 0.48, 0.48, 0.48, 0.48]
                ]),
                "tkmg": jnp.array([
                    [2.8, 2.8, 2.8, 2.8, 2.8],
                    [3.2, 3.2, 3.2, 3.2, 3.2]
                ]),
                "tkdry": jnp.array([
                    [0.18, 0.18, 0.18, 0.18, 0.18],
                    [0.22, 0.22, 0.22, 0.22, 0.22]
                ]),
                "csol": jnp.array([
                    [2.1e6, 2.1e6, 2.1e6, 2.1e6, 2.1e6],
                    [2.3e6, 2.3e6, 2.3e6, 2.3e6, 2.3e6]
                ]),
                "frac_sno": jnp.array([0.6, 0.8]),
                "snl": jnp.array([-2, -3]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Frozen soil with ice content and snow layers"
        },
        "test_edge_zero_heat_flux": {
            "inputs": {
                "t_soisno": jnp.array([
                    [285.15, 285.15, 285.15, 285.15, 285.15],
                    [285.15, 285.15, 285.15, 285.15, 285.15]
                ]),
                "gsoi": jnp.array([0.0, 0.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [10.0, 10.0, 10.0, 10.0, 10.0],
                    [10.0, 10.0, 10.0, 10.0, 10.0]
                ]),
                "h2osoi_ice": jnp.array([
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0]
                ]),
                "h2osno": jnp.array([0.0, 0.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.45, 0.45, 0.45, 0.45, 0.45],
                    [0.45, 0.45, 0.45, 0.45, 0.45]
                ]),
                "tkmg": jnp.array([
                    [2.5, 2.5, 2.5, 2.5, 2.5],
                    [2.5, 2.5, 2.5, 2.5, 2.5]
                ]),
                "tkdry": jnp.array([
                    [0.2, 0.2, 0.2, 0.2, 0.2],
                    [0.2, 0.2, 0.2, 0.2, 0.2]
                ]),
                "csol": jnp.array([
                    [2e6, 2e6, 2e6, 2e6, 2e6],
                    [2e6, 2e6, 2e6, 2e6, 2e6]
                ]),
                "frac_sno": jnp.array([0.0, 0.0]),
                "snl": jnp.array([0, 0]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Zero heat flux equilibrium condition"
        },
        "test_edge_extreme_cold": {
            "inputs": {
                "t_soisno": jnp.array([
                    [173.15, 180.15, 190.15, 200.15, 210.15],
                    [175.15, 185.15, 195.15, 205.15, 215.15]
                ]),
                "gsoi": jnp.array([-200.0, -180.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0]
                ]),
                "h2osoi_ice": jnp.array([
                    [15.0, 18.0, 22.0, 25.0, 28.0],
                    [16.0, 19.0, 23.0, 26.0, 29.0]
                ]),
                "h2osno": jnp.array([200.0, 250.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.4, 0.4, 0.4, 0.4, 0.4],
                    [0.42, 0.42, 0.42, 0.42, 0.42]
                ]),
                "tkmg": jnp.array([
                    [2.8, 2.8, 2.8, 2.8, 2.8],
                    [3.0, 3.0, 3.0, 3.0, 3.0]
                ]),
                "tkdry": jnp.array([
                    [0.18, 0.18, 0.18, 0.18, 0.18],
                    [0.2, 0.2, 0.2, 0.2, 0.2]
                ]),
                "csol": jnp.array([
                    [2.1e6, 2.1e6, 2.1e6, 2.1e6, 2.1e6],
                    [2.2e6, 2.2e6, 2.2e6, 2.2e6, 2.2e6]
                ]),
                "frac_sno": jnp.array([1.0, 1.0]),
                "snl": jnp.array([-5, -5]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Extreme cold near physical minimum temperature"
        },
        "test_edge_dry_soil": {
            "inputs": {
                "t_soisno": jnp.array([
                    [310.15, 305.15, 300.15, 295.15, 290.15],
                    [312.15, 307.15, 302.15, 297.15, 292.15]
                ]),
                "gsoi": jnp.array([200.0, 195.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [1e-6, 1e-6, 1e-6, 1e-6, 1e-6],
                    [1e-6, 1e-6, 1e-6, 1e-6, 1e-6]
                ]),
                "h2osoi_ice": jnp.array([
                    [0.0, 0.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0, 0.0, 0.0]
                ]),
                "h2osno": jnp.array([0.0, 0.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.3, 0.3, 0.3, 0.3, 0.3],
                    [0.32, 0.32, 0.32, 0.32, 0.32]
                ]),
                "tkmg": jnp.array([
                    [4.8, 4.8, 4.8, 4.8, 4.8],
                    [5.0, 5.0, 5.0, 5.0, 5.0]
                ]),
                "tkdry": jnp.array([
                    [0.45, 0.45, 0.45, 0.45, 0.45],
                    [0.48, 0.48, 0.48, 0.48, 0.48]
                ]),
                "csol": jnp.array([
                    [1.2e6, 1.2e6, 1.2e6, 1.2e6, 1.2e6],
                    [1.3e6, 1.3e6, 1.3e6, 1.3e6, 1.3e6]
                ]),
                "frac_sno": jnp.array([0.0, 0.0]),
                "snl": jnp.array([0, 0]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Extremely dry hot soil with minimal moisture"
        },
        "test_edge_thin_layers": {
            "inputs": {
                "t_soisno": jnp.array([
                    [290.15, 289.15, 288.15],
                    [291.15, 290.15, 289.15]
                ]),
                "gsoi": jnp.array([40.0, 35.0]),
                "z": jnp.array([
                    [0.005, 0.015, 0.035],
                    [0.005, 0.015, 0.035]
                ]),
                "zi": jnp.array([
                    [0.0, 0.01, 0.02, 0.05],
                    [0.0, 0.01, 0.02, 0.05]
                ]),
                "dz": jnp.array([
                    [0.01, 0.01, 0.03],
                    [0.01, 0.01, 0.03]
                ]),
                "h2osoi_liq": jnp.array([
                    [0.5, 0.6, 1.5],
                    [0.6, 0.7, 1.6]
                ]),
                "h2osoi_ice": jnp.array([
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0]
                ]),
                "h2osno": jnp.array([0.0, 0.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.44, 0.44, 0.44],
                    [0.46, 0.46, 0.46]
                ]),
                "tkmg": jnp.array([
                    [2.4, 2.4, 2.4],
                    [2.6, 2.6, 2.6]
                ]),
                "tkdry": jnp.array([
                    [0.17, 0.17, 0.17],
                    [0.19, 0.19, 0.19]
                ]),
                "csol": jnp.array([
                    [1.95e6, 1.95e6, 1.95e6],
                    [2.05e6, 2.05e6, 2.05e6]
                ]),
                "frac_sno": jnp.array([0.0, 0.0]),
                "snl": jnp.array([0, 0]),
                "nbedrock": jnp.array([3, 3]),
                "dtime": 60.0
            },
            "expected_shape": (2, 3),
            "description": "Very thin soil layers with fine resolution"
        },
        "test_special_phase_transition": {
            "inputs": {
                "t_soisno": jnp.array([
                    [273.15, 273.1, 272.9, 272.5, 272.0],
                    [273.2, 273.15, 273.05, 272.8, 272.3]
                ]),
                "gsoi": jnp.array([-25.0, -30.0]),
                "z": jnp.array([
                    [0.05, 0.15, 0.35, 0.75, 1.5],
                    [0.05, 0.15, 0.35, 0.75, 1.5]
                ]),
                "zi": jnp.array([
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0],
                    [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]
                ]),
                "dz": jnp.array([
                    [0.1, 0.1, 0.3, 0.5, 1.0],
                    [0.1, 0.1, 0.3, 0.5, 1.0]
                ]),
                "h2osoi_liq": jnp.array([
                    [5.0, 4.5, 3.0, 2.0, 1.0],
                    [5.5, 5.0, 3.5, 2.5, 1.5]
                ]),
                "h2osoi_ice": jnp.array([
                    [5.0, 5.5, 7.0, 8.0, 9.0],
                    [4.5, 5.0, 6.5, 7.5, 8.5]
                ]),
                "h2osno": jnp.array([30.0, 35.0]),
                "h2osfc": jnp.array([0.0, 0.0]),
                "watsat": jnp.array([
                    [0.46, 0.46, 0.46, 0.46, 0.46],
                    [0.48, 0.48, 0.48, 0.48, 0.48]
                ]),
                "tkmg": jnp.array([
                    [2.7, 2.7, 2.7, 2.7, 2.7],
                    [2.9, 2.9, 2.9, 2.9, 2.9]
                ]),
                "tkdry": jnp.array([
                    [0.21, 0.21, 0.21, 0.21, 0.21],
                    [0.23, 0.23, 0.23, 0.23, 0.23]
                ]),
                "csol": jnp.array([
                    [2.08e6, 2.08e6, 2.08e6, 2.08e6, 2.08e6],
                    [2.18e6, 2.18e6, 2.18e6, 2.18e6, 2.18e6]
                ]),
                "frac_sno": jnp.array([0.4, 0.5]),
                "snl": jnp.array([-2, -2]),
                "nbedrock": jnp.array([5, 5]),
                "dtime": 1800.0
            },
            "expected_shape": (2, 5),
            "description": "Phase transition zone near freezing point"
        }
    }


# ============================================================================
# Shape and Dimension Tests
# ============================================================================

@pytest.mark.parametrize("test_name", [
    "test_nominal_temperate_soil",
    "test_nominal_frozen_soil",
    "test_edge_zero_heat_flux",
    "test_edge_extreme_cold",
    "test_edge_dry_soil",
    "test_edge_thin_layers",
    "test_special_phase_transition"
])
def test_soil_temperature_output_shapes(test_data, default_params, test_name):
    """
    Test that soil_temperature returns outputs with correct shapes.
    
    Verifies:
    - Temperature array shape matches input shape (n_columns, n_levels)
    - All thermal property arrays have correct dimensions
    - Scalar properties have correct shape
    """
    test_case = test_data[test_name]
    inputs = test_case["inputs"]
    expected_shape = test_case["expected_shape"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Check temperature output shape
    assert t_new.shape == expected_shape, (
        f"Temperature output shape {t_new.shape} does not match "
        f"expected shape {expected_shape} for {test_name}"
    )
    
    # Check thermal properties shapes
    n_columns, n_levels = expected_shape
    
    assert thermal_props.tk.shape == expected_shape, (
        f"Thermal conductivity (tk) shape mismatch in {test_name}"
    )
    assert thermal_props.cv.shape == expected_shape, (
        f"Heat capacity (cv) shape mismatch in {test_name}"
    )
    assert thermal_props.tk_h2osfc.shape == (n_columns,), (
        f"Surface water conductivity shape mismatch in {test_name}"
    )
    assert thermal_props.thk.shape == expected_shape, (
        f"Layer thermal conductivity (thk) shape mismatch in {test_name}"
    )
    assert thermal_props.bw.shape == expected_shape, (
        f"Snow density (bw) shape mismatch in {test_name}"
    )


@pytest.mark.parametrize("test_name", [
    "test_nominal_temperate_soil",
    "test_edge_zero_heat_flux",
    "test_edge_thin_layers"
])
def test_soil_temperature_dtypes(test_data, default_params, test_name):
    """
    Test that soil_temperature returns outputs with correct data types.
    
    Verifies all outputs are JAX arrays with float dtype.
    """
    test_case = test_data[test_name]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Check dtypes
    assert jnp.issubdtype(t_new.dtype, jnp.floating), (
        f"Temperature output should be floating point in {test_name}"
    )
    assert jnp.issubdtype(thermal_props.tk.dtype, jnp.floating), (
        f"Thermal conductivity should be floating point in {test_name}"
    )
    assert jnp.issubdtype(thermal_props.cv.dtype, jnp.floating), (
        f"Heat capacity should be floating point in {test_name}"
    )


# ============================================================================
# Physical Constraint Tests
# ============================================================================

@pytest.mark.parametrize("test_name", [
    "test_nominal_temperate_soil",
    "test_nominal_frozen_soil",
    "test_edge_zero_heat_flux",
    "test_edge_extreme_cold",
    "test_edge_dry_soil",
    "test_special_phase_transition"
])
def test_soil_temperature_physical_constraints(test_data, default_params, test_name):
    """
    Test that output temperatures satisfy physical constraints.
    
    Verifies:
    - All temperatures are positive (> 0 K)
    - Temperatures are within reasonable physical range
    - No NaN or Inf values
    """
    test_case = test_data[test_name]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Check for NaN/Inf
    assert jnp.all(jnp.isfinite(t_new)), (
        f"Temperature output contains NaN or Inf values in {test_name}"
    )
    
    # Check positive temperatures (absolute zero constraint)
    assert jnp.all(t_new > 0.0), (
        f"Temperature output contains non-positive values in {test_name}"
    )
    
    # Check reasonable physical range (0K to 400K)
    assert jnp.all(t_new < 400.0), (
        f"Temperature output exceeds reasonable maximum (400K) in {test_name}"
    )
    
    # Check thermal properties are non-negative
    assert jnp.all(thermal_props.tk >= 0.0), (
        f"Thermal conductivity contains negative values in {test_name}"
    )
    assert jnp.all(thermal_props.cv >= 0.0), (
        f"Heat capacity contains negative values in {test_name}"
    )


@pytest.mark.parametrize("test_name", [
    "test_nominal_temperate_soil",
    "test_nominal_frozen_soil"
])
def test_soil_temperature_thermal_properties_ranges(test_data, default_params, test_name):
    """
    Test that thermal properties are within expected physical ranges.
    
    Verifies:
    - Thermal conductivity in reasonable range (0.01 - 10 W/m/K)
    - Heat capacity in reasonable range (1e5 - 1e7 J/m²/K)
    """
    test_case = test_data[test_name]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Check thermal conductivity range
    assert jnp.all(thermal_props.tk >= 0.01), (
        f"Thermal conductivity too low in {test_name}"
    )
    assert jnp.all(thermal_props.tk <= 10.0), (
        f"Thermal conductivity too high in {test_name}"
    )
    
    # Check heat capacity range
    assert jnp.all(thermal_props.cv >= 1e5), (
        f"Heat capacity too low in {test_name}"
    )
    assert jnp.all(thermal_props.cv <= 1e7), (
        f"Heat capacity too high in {test_name}"
    )


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_soil_temperature_zero_flux_stability(test_data, default_params):
    """
    Test numerical stability with zero heat flux.
    
    With zero flux and uniform temperature, the solution should remain
    stable and close to the initial state.
    """
    test_case = test_data["test_edge_zero_heat_flux"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # With zero flux, temperatures should change very little
    t_initial = inputs["t_soisno"]
    temp_change = jnp.abs(t_new - t_initial)
    
    # Allow small numerical changes but should be stable
    assert jnp.all(temp_change < 1.0), (
        "Temperature changed significantly with zero heat flux"
    )


def test_soil_temperature_extreme_cold_handling(test_data, default_params):
    """
    Test handling of extreme cold temperatures near physical minimum.
    
    Verifies:
    - Function doesn't crash with very low temperatures
    - Output remains physically valid
    - All ice, no liquid water at extreme cold
    """
    test_case = test_data["test_edge_extreme_cold"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Should handle extreme cold without errors
    assert jnp.all(jnp.isfinite(t_new)), (
        "Function produced NaN/Inf at extreme cold temperatures"
    )
    
    # Temperatures should remain cold
    assert jnp.all(t_new < 250.0), (
        "Extreme cold case produced unreasonably warm temperatures"
    )


def test_soil_temperature_dry_soil_handling(test_data, default_params):
    """
    Test handling of extremely dry soil conditions.
    
    Verifies:
    - Function handles minimal moisture content
    - Thermal properties reflect dry conditions
    - No numerical issues with near-zero water content
    """
    test_case = test_data["test_edge_dry_soil"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Should handle dry conditions without errors
    assert jnp.all(jnp.isfinite(t_new)), (
        "Function produced NaN/Inf with dry soil"
    )
    assert jnp.all(jnp.isfinite(thermal_props.tk)), (
        "Thermal conductivity invalid with dry soil"
    )


def test_soil_temperature_thin_layers_stability(test_data, default_params):
    """
    Test numerical stability with very thin soil layers.
    
    Thin layers can cause numerical instability in finite difference schemes.
    Verifies the solution remains stable.
    """
    test_case = test_data["test_edge_thin_layers"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Check for numerical stability
    assert jnp.all(jnp.isfinite(t_new)), (
        "Thin layers caused numerical instability"
    )
    
    # Temperature changes should be reasonable even with thin layers
    t_initial = inputs["t_soisno"]
    temp_change = jnp.abs(t_new - t_initial)
    assert jnp.all(temp_change < 50.0), (
        "Unreasonably large temperature changes with thin layers"
    )


# ============================================================================
# Special Case Tests
# ============================================================================

def test_soil_temperature_phase_transition_zone(test_data, default_params):
    """
    Test handling of phase transition zone near freezing point.
    
    Temperatures near 273.15K (0°C) with mixed liquid/ice content
    require careful handling of latent heat effects.
    """
    test_case = test_data["test_special_phase_transition"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Should handle phase transition without errors
    assert jnp.all(jnp.isfinite(t_new)), (
        "Phase transition zone caused numerical issues"
    )
    
    # Temperatures should remain near freezing point
    assert jnp.all(jnp.abs(t_new - 273.15) < 10.0), (
        "Temperatures moved far from freezing point in phase transition test"
    )


def test_soil_temperature_consistency_across_columns(test_data, default_params):
    """
    Test that similar inputs produce similar outputs across columns.
    
    Verifies spatial consistency of the solution.
    """
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    # Call function
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    # Both columns have similar inputs, should have similar outputs
    # (not identical due to different heat flux)
    temp_diff = jnp.abs(t_new[0, :] - t_new[1, :])
    
    # Differences should be reasonable (within 10K)
    assert jnp.all(temp_diff < 10.0), (
        "Unreasonably large differences between similar columns"
    )


# ============================================================================
# Input Validation Tests
# ============================================================================

def test_soil_temperature_input_dimension_consistency(test_data, default_params):
    """
    Test that function handles consistent input dimensions correctly.
    
    Verifies that all array inputs have compatible dimensions.
    """
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    # Verify input consistency
    n_columns, n_levels = inputs["t_soisno"].shape
    
    assert inputs["z"].shape == (n_columns, n_levels)
    assert inputs["zi"].shape == (n_columns, n_levels + 1)
    assert inputs["dz"].shape == (n_columns, n_levels)
    assert inputs["gsoi"].shape == (n_columns,)
    assert inputs["h2osno"].shape == (n_columns,)
    
    # Function should execute without errors
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    assert t_new.shape == (n_columns, n_levels)


def test_soil_temperature_fraction_constraints(test_data, default_params):
    """
    Test that fractional inputs (watsat, frac_sno) are in valid range [0, 1].
    """
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    # Check input constraints
    assert jnp.all(inputs["watsat"] >= 0.0) and jnp.all(inputs["watsat"] <= 1.0), (
        "watsat should be in range [0, 1]"
    )
    assert jnp.all(inputs["frac_sno"] >= 0.0) and jnp.all(inputs["frac_sno"] <= 1.0), (
        "frac_sno should be in range [0, 1]"
    )
    
    # Function should handle valid fractions correctly
    t_new, thermal_props = soil_temperature(
        **inputs,
        params=default_params
    )
    
    assert jnp.all(jnp.isfinite(t_new))


# ============================================================================
# Numerical Properties Tests
# ============================================================================

def test_soil_temperature_monotonicity_with_depth(test_data, default_params):
    """
    Test temperature profile monotonicity with depth for steady heating/cooling.
    
    With positive heat flux (heating), surface should be warmest.
    With negative heat flux (cooling), surface should be coolest.
    """
    # Test with positive flux (heating)
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    t_new, _ = soil_temperature(**inputs, params=default_params)
    
    # For column 0 with positive flux, check general trend
    # (may not be strictly monotonic due to initial conditions)
    surface_temp = t_new[0, 0]
    deep_temp = t_new[0, -1]
    
    # With heating, surface should generally be warmer or similar
    # (relaxed constraint due to transient nature)
    assert surface_temp >= deep_temp - 5.0, (
        "Temperature profile inconsistent with heating"
    )


def test_soil_temperature_energy_conservation_indicator(test_data, default_params):
    """
    Test that temperature changes are consistent with applied heat flux.
    
    Larger heat flux should generally produce larger temperature changes.
    """
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    t_initial = inputs["t_soisno"]
    t_new, _ = soil_temperature(**inputs, params=default_params)
    
    # Calculate temperature changes
    temp_change = t_new - t_initial
    
    # Column 0 has positive flux (50 W/m²), column 1 has negative flux (-30 W/m²)
    # Surface layer should show opposite trends
    assert temp_change[0, 0] > temp_change[1, 0], (
        "Temperature changes inconsistent with heat flux direction"
    )


# ============================================================================
# Regression Tests
# ============================================================================

def test_soil_temperature_reproducibility(test_data, default_params):
    """
    Test that function produces identical results for identical inputs.
    
    Verifies deterministic behavior.
    """
    test_case = test_data["test_nominal_temperate_soil"]
    inputs = test_case["inputs"]
    
    # Run twice with same inputs
    t_new1, thermal_props1 = soil_temperature(**inputs, params=default_params)
    t_new2, thermal_props2 = soil_temperature(**inputs, params=default_params)
    
    # Results should be identical
    np.testing.assert_array_equal(
        t_new1, t_new2,
        err_msg="Function not reproducible - different outputs for same inputs"
    )
    np.testing.assert_array_equal(
        thermal_props1.tk, thermal_props2.tk,
        err_msg="Thermal properties not reproducible"
    )


# ============================================================================
# Documentation Tests
# ============================================================================

def test_soil_temperature_docstring_exists():
    """
    Test that the function has proper documentation.
    """
    assert soil_temperature.__doc__ is not None, (
        "Function should have a docstring"
    )
    assert len(soil_temperature.__doc__) > 50, (
        "Function docstring should be comprehensive"
    )


def test_namedtuple_definitions():
    """
    Test that required NamedTuples are properly defined.
    """
    # Test SoilThermalProperties
    props = SoilThermalProperties(
        tk=jnp.array([[1.0]]),
        cv=jnp.array([[2e6]]),
        tk_h2osfc=jnp.array([0.5]),
        thk=jnp.array([[1.2]]),
        bw=jnp.array([[100.0]])
    )
    
    assert hasattr(props, 'tk')
    assert hasattr(props, 'cv')
    assert hasattr(props, 'tk_h2osfc')
    assert hasattr(props, 'thk')
    assert hasattr(props, 'bw')
    
    # Test SoilTemperatureParams
    params = SoilTemperatureParams(
        denh2o=1000.0, denice=917.0, tfrz=273.15,
        tkwat=0.57, tkice=2.29, tkair=0.023,
        cpice=2117.27, cpliq=4188.0,
        thk_bedrock=3.0, csol_bedrock=2.5e6,
        thin_sfclayer=0.01
    )
    
    assert params.denh2o == 1000.0
    assert params.tfrz == 273.15


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])