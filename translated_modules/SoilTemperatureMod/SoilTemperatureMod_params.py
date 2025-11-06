"""
Parameters for soil temperature calculations.

Translated from constants used in SoilTemperatureMod.F90
"""

from typing import NamedTuple
import jax.numpy as jnp


class SoilTemperatureParams(NamedTuple):
    """Parameters for soil temperature calculations.
    
    Attributes:
        # Physical constants
        denh2o: Density of liquid water [kg/m³]
        denice: Density of ice [kg/m³]
        tfrz: Freezing point of water [K]
        tkwat: Thermal conductivity of water [W/m/K]
        tkice: Thermal conductivity of ice [W/m/K]
        tkair: Thermal conductivity of air [W/m/K]
        cpice: Specific heat of ice [J/kg/K]
        cpliq: Specific heat of liquid water [J/kg/K]
        
        # Bedrock properties
        thk_bedrock: Thermal conductivity of bedrock [W/m/K]
        csol_bedrock: Heat capacity of bedrock [J/m³/K]
        
        # Numerical parameters
        thin_sfclayer: Threshold for thin surface layer [J/m²/K]
        energy_tol: Tolerance for energy conservation check [W/m²]
    """
    # Physical constants (from clm_varcon)
    denh2o: float = 1000.0  # kg/m³
    denice: float = 917.0   # kg/m³
    tfrz: float = 273.15    # K
    tkwat: float = 0.57     # W/m/K
    tkice: float = 2.29     # W/m/K
    tkair: float = 0.023    # W/m/K
    cpice: float = 2117.27  # J/kg/K
    cpliq: float = 4188.0   # J/kg/K
    
    # Bedrock properties
    thk_bedrock: float = 3.0      # W/m/K
    csol_bedrock: float = 2.0e6   # J/m³/K
    
    # Numerical parameters
    thin_sfclayer: float = 1.0e-6  # J/m²/K
    energy_tol: float = 1.0e-6     # W/m²


def create_default_params() -> SoilTemperatureParams:
    """Create default soil temperature parameters.
    
    Returns:
        SoilTemperatureParams with default values from CLM5
        
    Example:
        >>> params = create_default_params()
        >>> print(f"Water thermal conductivity: {params.tkwat} W/m/K")
    """
    return SoilTemperatureParams()