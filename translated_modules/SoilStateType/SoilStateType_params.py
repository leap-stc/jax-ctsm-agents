"""
Soil state constants and default parameters.

Defines standard vertical discretization and physical constants
used in soil state initialization and calculations.
"""

from typing import NamedTuple


class SoilVerticalDiscretization(NamedTuple):
    """Standard vertical discretization for soil columns.
    
    Attributes:
        nlevsoi: Number of soil layers (hydrologically active)
        nlevgrnd: Total number of ground layers (soil + bedrock)
        nlevsno: Maximum number of snow layers
        
    Note:
        These match the default CTSM configuration. Different
        configurations may use different values.
    """
    nlevsoi: int = 10    # Soil layers (hydrologically active)
    nlevgrnd: int = 15   # Ground layers (soil + bedrock)
    nlevsno: int = 5     # Snow layers


# Default discretization
DEFAULT_VERTICAL_DISCRETIZATION = SoilVerticalDiscretization()


class SoilPhysicalConstants(NamedTuple):
    """Physical constants for soil calculations.
    
    Attributes:
        min_porosity: Minimum allowed porosity [-]
        max_porosity: Maximum allowed porosity [-]
        min_hksat: Minimum saturated hydraulic conductivity [mm/s]
        max_hksat: Maximum saturated hydraulic conductivity [mm/s]
        
    Note:
        These are typical bounds used for validation and
        numerical stability in soil physics calculations.
    """
    min_porosity: float = 0.1
    max_porosity: float = 0.9
    min_hksat: float = 1e-6  # mm/s
    max_hksat: float = 1e2   # mm/s


# Default physical constants
DEFAULT_SOIL_CONSTANTS = SoilPhysicalConstants()