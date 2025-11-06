"""
Soil State Variables.

Translated from CTSM's SoilStateType.F90 (lines 1-106)

This module defines the soil state data structure containing:
- Soil composition (sand, clay, organic matter)
- Hydraulic properties (conductivity, matric potential, porosity)
- Thermal properties (conductivity, heat capacity)
- Root distribution

The Fortran module uses a derived type with pointer arrays allocated based on
spatial bounds. In JAX, we use a NamedTuple with fixed-size arrays indexed by
column/patch and layer indices.

Spatial Hierarchy:
    - Columns (n_columns): Fundamental spatial unit for soil
    - Patches (n_patches): Vegetation units, multiple per column
    - Layers: Vertical discretization
        - nlevsoi: Soil layers (typically 10)
        - nlevgrnd: Ground layers including bedrock (typically 15)
        - nlevsno: Snow layers (typically 5, indexed -4 to 0)

Array Indexing Convention:
    - Column arrays: [n_columns] or [n_columns, n_layers]
    - Patch arrays: [n_patches, n_layers]
    - Layer dimension varies by variable (see individual field docs)
"""

from typing import NamedTuple
import jax.numpy as jnp


class SoilState(NamedTuple):
    """Soil state variables.
    
    This immutable structure holds all soil state information including
    composition, hydraulic properties, thermal properties, and root distribution.
    
    All arrays use 0-based indexing. Layer indices:
        - Soil layers: 0 to nlevsoi-1
        - Ground layers: 0 to nlevgrnd-1
        - Snow+ground layers: -nlevsno to nlevgrnd-1 (for thk_col only)
    
    Attributes:
        Soil Composition:
            cellorg_col: Organic matter content [kg/m³] [n_columns, nlevsoi]
            cellsand_col: Sand percentage [%] [n_columns, nlevsoi]
            cellclay_col: Clay percentage [%] [n_columns, nlevsoi]
            
        Hydraulic Properties:
            hksat_col: Saturated hydraulic conductivity [mm H2O/s] [n_columns, nlevgrnd]
            hk_l_col: Layer hydraulic conductivity [mm H2O/s] [n_columns, nlevgrnd]
            smp_l_col: Soil matric potential [mm] [n_columns, nlevgrnd]
            bsw_col: Clapp-Hornberger 'b' parameter [-] [n_columns, nlevgrnd]
            watsat_col: Volumetric water at saturation (porosity) [-] [n_columns, nlevgrnd]
            sucsat_col: Minimum soil suction [mm] [n_columns, nlevgrnd]
            dsl_col: Dry surface layer thickness [mm] [n_columns]
            soilresis_col: Soil evaporative resistance (Swenson & Lawrence 2014) [s/m] [n_columns]
            
        Thermal Properties:
            thk_col: Thermal conductivity [W/m/K] [n_columns, nlevsno+nlevgrnd]
                Note: Includes snow layers, indexed from -nlevsno+1 to nlevgrnd
                In JAX: Use 0-based indexing, snow layers at indices 0:nlevsno
            tkmg_col: Thermal conductivity of soil minerals [W/m/K] [n_columns, nlevgrnd]
            tkdry_col: Thermal conductivity of dry soil [W/m/K] [n_columns, nlevgrnd]
            csol_col: Heat capacity of soil solids [J/m³/K] [n_columns, nlevgrnd]
            
        Root Distribution:
            rootfr_patch: Effective fraction of roots in each layer [-] [n_patches, nlevgrnd]
    
    Reference:
        SoilStateType.F90, lines 20-50
    """
    
    # Soil composition (nlevsoi layers)
    cellorg_col: jnp.ndarray    # [n_columns, nlevsoi]
    cellsand_col: jnp.ndarray   # [n_columns, nlevsoi]
    cellclay_col: jnp.ndarray   # [n_columns, nlevsoi]
    
    # Hydraulic properties (nlevgrnd layers)
    hksat_col: jnp.ndarray      # [n_columns, nlevgrnd]
    hk_l_col: jnp.ndarray       # [n_columns, nlevgrnd]
    smp_l_col: jnp.ndarray      # [n_columns, nlevgrnd]
    bsw_col: jnp.ndarray        # [n_columns, nlevgrnd]
    watsat_col: jnp.ndarray     # [n_columns, nlevgrnd]
    sucsat_col: jnp.ndarray     # [n_columns, nlevgrnd]
    dsl_col: jnp.ndarray        # [n_columns]
    soilresis_col: jnp.ndarray  # [n_columns]
    
    # Thermal properties
    thk_col: jnp.ndarray        # [n_columns, nlevsno+nlevgrnd]
    tkmg_col: jnp.ndarray       # [n_columns, nlevgrnd]
    tkdry_col: jnp.ndarray      # [n_columns, nlevgrnd]
    csol_col: jnp.ndarray       # [n_columns, nlevgrnd]
    
    # Root distribution
    rootfr_patch: jnp.ndarray   # [n_patches, nlevgrnd]


def initialize_soil_state(
    n_columns: int,
    n_patches: int,
    nlevsoi: int = 10,
    nlevgrnd: int = 15,
    nlevsno: int = 5,
    fill_value: float = jnp.nan,
) -> SoilState:
    """Initialize soil state with default values.
    
    Creates a SoilState structure with all arrays initialized to fill_value
    (typically NaN to match Fortran initialization). Arrays are allocated with
    appropriate shapes based on spatial dimensions and vertical levels.
    
    Args:
        n_columns: Number of columns in the domain
        n_patches: Number of patches in the domain
        nlevsoi: Number of soil layers (default: 10)
        nlevgrnd: Number of ground layers including bedrock (default: 15)
        nlevsno: Number of snow layers (default: 5)
        fill_value: Initial value for all arrays (default: NaN)
        
    Returns:
        Initialized SoilState with all arrays filled with fill_value
        
    Example:
        >>> soil_state = initialize_soil_state(
        ...     n_columns=100,
        ...     n_patches=500,
        ...     nlevsoi=10,
        ...     nlevgrnd=15
        ... )
        >>> soil_state.cellsand_col.shape
        (100, 10)
        >>> soil_state.rootfr_patch.shape
        (500, 15)
        
    Reference:
        SoilStateType.F90, InitAllocate subroutine, lines 67-104
        
    Note:
        The thk_col array includes snow layers, so its shape is
        [n_columns, nlevsno + nlevgrnd]. In Fortran, this is indexed
        from -nlevsno+1:nlevgrnd. In JAX, we use 0-based indexing where
        indices 0:nlevsno correspond to snow layers and nlevsno: correspond
        to ground layers.
    """
    # Soil composition arrays (nlevsoi layers)
    cellorg_col = jnp.full((n_columns, nlevsoi), fill_value)
    cellsand_col = jnp.full((n_columns, nlevsoi), fill_value)
    cellclay_col = jnp.full((n_columns, nlevsoi), fill_value)
    
    # Hydraulic property arrays (nlevgrnd layers)
    hksat_col = jnp.full((n_columns, nlevgrnd), fill_value)
    hk_l_col = jnp.full((n_columns, nlevgrnd), fill_value)
    smp_l_col = jnp.full((n_columns, nlevgrnd), fill_value)
    bsw_col = jnp.full((n_columns, nlevgrnd), fill_value)
    watsat_col = jnp.full((n_columns, nlevgrnd), fill_value)
    sucsat_col = jnp.full((n_columns, nlevgrnd), fill_value)
    
    # Scalar column arrays
    dsl_col = jnp.full(n_columns, fill_value)
    soilresis_col = jnp.full(n_columns, fill_value)
    
    # Thermal property arrays
    # thk_col includes snow layers: -nlevsno+1:nlevgrnd in Fortran
    # In JAX: 0-based indexing, total size is nlevsno + nlevgrnd
    thk_col = jnp.full((n_columns, nlevsno + nlevgrnd), fill_value)
    tkmg_col = jnp.full((n_columns, nlevgrnd), fill_value)
    tkdry_col = jnp.full((n_columns, nlevgrnd), fill_value)
    csol_col = jnp.full((n_columns, nlevgrnd), fill_value)
    
    # Root distribution (patch-level)
    rootfr_patch = jnp.full((n_patches, nlevgrnd), fill_value)
    
    return SoilState(
        cellorg_col=cellorg_col,
        cellsand_col=cellsand_col,
        cellclay_col=cellclay_col,
        hksat_col=hksat_col,
        hk_l_col=hk_l_col,
        smp_l_col=smp_l_col,
        bsw_col=bsw_col,
        watsat_col=watsat_col,
        sucsat_col=sucsat_col,
        dsl_col=dsl_col,
        soilresis_col=soilresis_col,
        thk_col=thk_col,
        tkmg_col=tkmg_col,
        tkdry_col=tkdry_col,
        csol_col=csol_col,
        rootfr_patch=rootfr_patch,
    )


def update_soil_state(
    state: SoilState,
    **updates,
) -> SoilState:
    """Update soil state with new values.
    
    Creates a new SoilState with specified fields updated. This is the
    idiomatic way to "modify" the immutable SoilState structure.
    
    Args:
        state: Current soil state
        **updates: Keyword arguments specifying fields to update
        
    Returns:
        New SoilState with updated fields
        
    Example:
        >>> new_state = update_soil_state(
        ...     state,
        ...     hk_l_col=new_hydraulic_conductivity,
        ...     smp_l_col=new_matric_potential
        ... )
        
    Note:
        This uses NamedTuple._replace() which creates a shallow copy
        with specified fields replaced. Arrays are not copied unless
        explicitly provided as new arrays.
    """
    return state._replace(**updates)


def get_snow_layer_index(layer_idx: int, nlevsno: int = 5) -> int:
    """Convert Fortran snow layer index to JAX array index.
    
    In Fortran, snow layers are indexed from -nlevsno+1 to 0.
    In JAX, we use 0-based indexing where snow layers occupy
    indices 0 to nlevsno-1 in the thk_col array.
    
    Args:
        layer_idx: Fortran layer index (-nlevsno+1 to nlevgrnd)
        nlevsno: Number of snow layers (default: 5)
        
    Returns:
        JAX array index (0 to nlevsno+nlevgrnd-1)
        
    Example:
        >>> # Fortran index -4 (first snow layer with nlevsno=5)
        >>> get_snow_layer_index(-4, nlevsno=5)
        0
        >>> # Fortran index 0 (last snow layer)
        >>> get_snow_layer_index(0, nlevsno=5)
        4
        >>> # Fortran index 1 (first ground layer)
        >>> get_snow_layer_index(1, nlevsno=5)
        5
        
    Note:
        Only relevant for thk_col which includes snow layers.
        Other arrays use standard 0-based indexing for ground layers only.
    """
    return layer_idx + nlevsno - 1


def get_ground_layer_slice(nlevsno: int = 5) -> slice:
    """Get slice for ground layers in thk_col array.
    
    Args:
        nlevsno: Number of snow layers (default: 5)
        
    Returns:
        Slice object for ground layers (excludes snow layers)
        
    Example:
        >>> thk_ground = state.thk_col[:, get_ground_layer_slice()]
        >>> # Equivalent to state.thk_col[:, 5:] with nlevsno=5
    """
    return slice(nlevsno, None)


def get_snow_layer_slice(nlevsno: int = 5) -> slice:
    """Get slice for snow layers in thk_col array.
    
    Args:
        nlevsno: Number of snow layers (default: 5)
        
    Returns:
        Slice object for snow layers
        
    Example:
        >>> thk_snow = state.thk_col[:, get_snow_layer_slice()]
        >>> # Equivalent to state.thk_col[:, :5] with nlevsno=5
    """
    return slice(0, nlevsno)