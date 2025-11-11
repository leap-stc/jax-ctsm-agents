"""
Maintenance Respiration Calculations for CN Vegetation.

Translated from CTSM's CNMRespMod.F90

This module calculates maintenance respiration (MR) for all live plant tissues:
- Leaves (from photosynthesis model)
- Fine roots (integrated over soil layers)
- Live stems (woody PFTs only)
- Live coarse roots (woody PFTs only)
- Reproductive tissues (crops only)

Maintenance respiration represents the carbon cost of maintaining existing
plant biomass and scales with tissue nitrogen content and temperature via
Q10 relationships.

Key Physics:
    MR = N_tissue * base_rate * Q10^((T - T_ref) / 10)
    
    With optional acclimation:
    base_rate_adj = base_rate * 10^(coef * (T_10day - T_ref_acclim))

Reference:
    CTSM source: src/biogeochem/CNMRespMod.F90
    
    Ryan, M. (1991). Effects of climate change on plant respiration.
    Ecological Applications, 1(2), 157-167.
"""

from typing import NamedTuple
import jax
import jax.numpy as jnp

from jax_ctsm.params.maintenance_respiration import MaintenanceRespirationParams


class CanopyState(NamedTuple):
    """Canopy state variables for maintenance respiration.
    
    Attributes:
        frac_veg_nosno: Fraction of vegetation not covered by snow [0 or 1]
                       [n_patches]
        lai_sun: Sunlit leaf area index [m2/m2] [n_patches]
        lai_shade: Shaded leaf area index [m2/m2] [n_patches]
    """
    frac_veg_nosno: jnp.ndarray  # [n_patches]
    lai_sun: jnp.ndarray  # [n_patches]
    lai_shade: jnp.ndarray  # [n_patches]


class SoilState(NamedTuple):
    """Soil state variables for maintenance respiration.
    
    Attributes:
        crootfr: Fraction of fine roots in each soil layer [0-1]
                Sums to 1.0 over all layers
                [n_patches, n_levgrnd]
    """
    crootfr: jnp.ndarray  # [n_patches, n_levgrnd]


class TemperatureState(NamedTuple):
    """Temperature state variables for maintenance respiration.
    
    Attributes:
        t_soisno: Soil temperature by layer [K] [n_cols, n_levgrnd]
        t_ref2m: 2m reference air temperature [K] [n_patches]
        t_10day: 10-day running mean temperature [K] [n_patches]
    """
    t_soisno: jnp.ndarray  # [n_cols, n_levgrnd]
    t_ref2m: jnp.ndarray  # [n_patches]
    t_10day: jnp.ndarray  # [n_patches]


class PhotosynthesisState(NamedTuple):
    """Photosynthesis state variables for maintenance respiration.
    
    Attributes:
        lmr_sun: Sunlit leaf maintenance respiration rate
                [umol CO2/m2 leaf/s] [n_patches]
        lmr_shade: Shaded leaf maintenance respiration rate
                  [umol CO2/m2 leaf/s] [n_patches]
    """
    lmr_sun: jnp.ndarray  # [n_patches]
    lmr_shade: jnp.ndarray  # [n_patches]


class NitrogenState(NamedTuple):
    """Vegetation nitrogen state for maintenance respiration.
    
    Attributes:
        frootn: Fine root nitrogen [gN/m2] [n_patches]
        livestemn: Live stem nitrogen [gN/m2] [n_patches]
        livecrootn: Live coarse root nitrogen [gN/m2] [n_patches]
        reproductiven: Reproductive tissue nitrogen [gN/m2]
                      [n_patches, n_repr]
    """
    frootn: jnp.ndarray  # [n_patches]
    livestemn: jnp.ndarray  # [n_patches]
    livecrootn: jnp.ndarray  # [n_patches]
    reproductiven: jnp.ndarray  # [n_patches, n_repr]


class PFTConstants(NamedTuple):
    """PFT-specific constants for maintenance respiration.
    
    Attributes:
        is_woody: Whether PFT is woody [boolean] [n_patches]
        is_crop: Whether PFT is prognostic crop [boolean] [n_patches]
    """
    is_woody: jnp.ndarray  # [n_patches]
    is_crop: jnp.ndarray  # [n_patches]


class MaintenanceRespirationFluxes(NamedTuple):
    """Maintenance respiration carbon fluxes.
    
    All fluxes in [gC/m2/s]
    
    Attributes:
        leaf_mr: Leaf maintenance respiration [n_patches]
        froot_mr: Fine root maintenance respiration [n_patches]
        livestem_mr: Live stem maintenance respiration [n_patches]
        livecroot_mr: Live coarse root maintenance respiration [n_patches]
        reproductive_mr: Reproductive tissue maintenance respiration
                        [n_patches, n_repr]
    """
    leaf_mr: jnp.ndarray  # [n_patches]
    froot_mr: jnp.ndarray  # [n_patches]
    livestem_mr: jnp.ndarray  # [n_patches]
    livecroot_mr: jnp.ndarray  # [n_patches]
    reproductive_mr: jnp.ndarray  # [n_patches, n_repr]


def calculate_soil_temperature_corrections(
    t_soisno: jnp.ndarray,
    params: MaintenanceRespirationParams,
) -> jnp.ndarray:
    """Calculate Q10 temperature correction for each soil layer.
    
    Used for fine root maintenance respiration, which varies with depth
    due to soil temperature gradients.
    
    Args:
        t_soisno: Soil temperature by layer [K] [n_cols, n_levgrnd]
        params: Respiration parameters
        
    Returns:
        Temperature correction factors [dimensionless] [n_cols, n_levgrnd]
        
    Reference:
        CNMRespMod.F90, lines ~185-195:
        do j=1,nlevgrnd
            tcsoi(c,j) = Q10**((t_soisno(c,j)-SHR_CONST_TKFRZ - 20.0_r8)/10.0_r8)
        end do
    """
    return params.get_temp_correction(t_soisno)


def calculate_leaf_maintenance_respiration(
    canopy: CanopyState,
    photosyns: PhotosynthesisState,
    params: MaintenanceRespirationParams,
) -> jnp.ndarray:
    """Calculate leaf maintenance respiration.
    
    Leaf MR is calculated by the photosynthesis model as a function of
    leaf nitrogen and temperature. Here we just convert units and account
    for snow cover.
    
    Args:
        canopy: Canopy state (LAI, snow cover)
        photosyns: Photosynthesis state (leaf MR rates)
        params: Respiration parameters
        
    Returns:
        Leaf MR flux [gC/m2 ground/s] [n_patches]
        
    Reference:
        CNMRespMod.F90, lines ~215-225:
        if (frac_veg_nosno(p) == 1) then
            leaf_mr(p) = lmrsun(p) * laisun(p) * 12.011e-6_r8 + 
                         lmrsha(p) * laisha(p) * 12.011e-6_r8
        else
            leaf_mr(p) = 0._r8
        end if
        
    Note:
        When snow covered (frac_veg_nosno=0), leaf MR is set to zero.
        The conversion factor 12.011e-6 converts umol CO2/m2 leaf/s to
        gC/m2 ground/s when multiplied by LAI.
    """
    # Convert from umol CO2/m2 leaf/s to gC/m2 ground/s
    # Multiply by LAI to convert from leaf area to ground area basis
    leaf_mr_sun = photosyns.lmr_sun * canopy.lai_sun * params.umol_to_gc
    leaf_mr_shade = photosyns.lmr_shade * canopy.lai_shade * params.umol_to_gc
    
    # Total leaf MR
    leaf_mr = leaf_mr_sun + leaf_mr_shade
    
    # Zero out if snow covered
    # Use > 0 instead of == 1 for numerical robustness
    leaf_mr = jnp.where(canopy.frac_veg_nosno > 0, leaf_mr, 0.0)
    
    return leaf_mr


def calculate_stem_maintenance_respiration(
    livestemn: jnp.ndarray,
    t_ref2m: jnp.ndarray,
    t_10day: jnp.ndarray,
    is_woody: jnp.ndarray,
    params: MaintenanceRespirationParams,
    enable_acclimation: bool = False,
) -> jnp.ndarray:
    """Calculate live stem maintenance respiration.
    
    Only applies to woody PFTs and prognostic crops.
    
    Args:
        livestemn: Live stem nitrogen [gN/m2] [n_patches]
        t_ref2m: 2m air temperature [K] [n_patches]
        t_10day: 10-day running mean temperature [K] [n_patches]
        is_woody: Whether PFT is woody [boolean] [n_patches]
        params: Respiration parameters
        enable_acclimation: Whether to apply acclimation adjustment
        
    Returns:
        Stem MR flux [gC/m2/s] [n_patches]
        
    Reference:
        CNMRespMod.F90, lines ~227-235:
        if (woody(ivt(p)) == 1) then
            livestem_mr(p) = livestemn(p)*br*tc
        else if (is_prognostic_crop(ivt(p))) then
            livestem_mr(p) = livestemn(p)*br*tc
        end if
        
    Note:
        Acclimation adjustment (if enabled) modifies base rate based on
        10-day running mean temperature. This is experimental.
    """
    # Get temperature correction from 2m air temperature
    temp_corr = params.get_temp_correction(t_ref2m)
    
    # Get acclimation factor if enabled
    acclim_factor = params.get_acclimation_factor(t_10day, enable_acclimation)
    
    # Base rate with acclimation
    br_adjusted = params.br * acclim_factor
    
    # Calculate stem MR: N * base_rate * temp_correction
    stem_mr = livestemn * br_adjusted * temp_corr
    
    # Only apply to woody PFTs (crops handled separately but use same formula)
    stem_mr = jnp.where(is_woody, stem_mr, 0.0)
    
    return stem_mr


def calculate_coarse_root_maintenance_respiration(
    livecrootn: jnp.ndarray,
    t_ref2m: jnp.ndarray,
    t_10day: jnp.ndarray,
    is_woody: jnp.ndarray,
    params: MaintenanceRespirationParams,
    enable_acclimation: bool = False,
) -> jnp.ndarray:
    """Calculate live coarse root maintenance respiration.
    
    Only applies to woody PFTs.
    
    Args:
        livecrootn: Live coarse root nitrogen [gN/m2] [n_patches]
        t_ref2m: 2m air temperature [K] [n_patches]
        t_10day: 10-day running mean temperature [K] [n_patches]
        is_woody: Whether PFT is woody [boolean] [n_patches]
        params: Respiration parameters
        enable_acclimation: Whether to apply acclimation adjustment
        
    Returns:
        Coarse root MR flux [gC/m2/s] [n_patches]
        
    Reference:
        CNMRespMod.F90, lines ~227-235:
        if (woody(ivt(p)) == 1) then
            livecroot_mr(p) = livecrootn(p)*br_root*tc
        end if
    """
    # Get temperature correction from 2m air temperature
    temp_corr = params.get_temp_correction(t_ref2m)
    
    # Get acclimation factor if enabled
    acclim_factor = params.get_acclimation_factor(t_10day, enable_acclimation)
    
    # Base rate with acclimation (use br_root)
    br_root_adjusted = params.br_root * acclim_factor
    
    # Calculate coarse root MR: N * base_rate * temp_correction
    croot_mr = livecrootn * br_root_adjusted * temp_corr
    
    # Only apply to woody PFTs
    croot_mr = jnp.where(is_woody, croot_mr, 0.0)
    
    return croot_mr


def calculate_reproductive_maintenance_respiration(
    reproductiven: jnp.ndarray,
    t_ref2m: jnp.ndarray,
    t_10day: jnp.ndarray,
    is_crop: jnp.ndarray,
    params: MaintenanceRespirationParams,
    enable_acclimation: bool = False,
) -> jnp.ndarray:
    """Calculate reproductive tissue maintenance respiration.
    
    Only applies to prognostic crops.
    
    Args:
        reproductiven: Reproductive tissue nitrogen [gN/m2]
                      [n_patches, n_repr]
        t_ref2m: 2m air temperature [K] [n_patches]
        t_10day: 10-day running mean temperature [K] [n_patches]
        is_crop: Whether PFT is prognostic crop [boolean] [n_patches]
        params: Respiration parameters
        enable_acclimation: Whether to apply acclimation adjustment
        
    Returns:
        Reproductive MR flux [gC/m2/s] [n_patches, n_repr]
        
    Reference:
        CNMRespMod.F90, lines ~227-235:
        else if (is_prognostic_crop(ivt(p))) then
            do k = 1, nrepr
                reproductive_mr(p,k) = reproductiven(p,k)*br*tc
            end do
        end if
    """
    # Get temperature correction from 2m air temperature
    # Broadcast to match reproductive array shape
    temp_corr = params.get_temp_correction(t_ref2m)[:, None]  # [n_patches, 1]
    
    # Get acclimation factor if enabled
    acclim_factor = params.get_acclimation_factor(t_10day, enable_acclimation)[:, None]
    
    # Base rate with acclimation
    br_adjusted = params.br * acclim_factor
    
    # Calculate reproductive MR: N * base_rate * temp_correction
    repr_mr = reproductiven * br_adjusted * temp_corr
    
    # Only apply to crops
    # Broadcast is_crop to match reproductive array shape
    repr_mr = jnp.where(is_crop[:, None], repr_mr, 0.0)
    
    return repr_mr


def calculate_fine_root_maintenance_respiration(
    frootn: jnp.ndarray,
    crootfr: jnp.ndarray,
    tcsoi: jnp.ndarray,
    patch_to_col: jnp.ndarray,
    t_10day: jnp.ndarray,
    params: MaintenanceRespirationParams,
    enable_acclimation: bool = False,
) -> jnp.ndarray:
    """Calculate fine root maintenance respiration.
    
    Fine root MR is integrated over soil layers, with each layer weighted
    by the fraction of roots in that layer and the layer-specific temperature
    correction.
    
    Args:
        frootn: Fine root nitrogen [gN/m2] [n_patches]
        crootfr: Fraction of roots in each layer [0-1] [n_patches, n_levgrnd]
                Sums to 1.0 over all layers
        tcsoi: Soil temperature correction by layer [dimensionless]
              [n_cols, n_levgrnd]
        patch_to_col: Mapping from patch to column index [n_patches]
        t_10day: 10-day running mean temperature [K] [n_patches]
        params: Respiration parameters
        enable_acclimation: Whether to apply acclimation adjustment
        
    Returns:
        Fine root MR flux [gC/m2/s] [n_patches]
        
    Reference:
        CNMRespMod.F90, lines ~240-255:
        do j = 1,nlevgrnd
            do fp = 1,num_soilp
                p = filter_soilp(fp)
                c = patch%column(p)
                froot_mr(p) = froot_mr(p) + 
                    frootn(p)*br_root*tcsoi(c,j)*crootfr(p,j)
            end do
        end do
        
    Note:
        The accumulation over layers is vectorized using jnp.sum.
        Temperature corrections are at column level, so we index into
        tcsoi using patch_to_col mapping.
    """
    # Get acclimation factor if enabled
    acclim_factor = params.get_acclimation_factor(t_10day, enable_acclimation)
    
    # Base rate with acclimation (use br_root)
    br_root_adjusted = params.br_root * acclim_factor
    
    # Get column-level temperature corrections for each patch
    # tcsoi[patch_to_col] gives [n_patches, n_levgrnd]
    tcsoi_patch = tcsoi[patch_to_col]
    
    # Calculate contribution from each layer
    # frootn[:, None] broadcasts to [n_patches, 1]
    # Result is [n_patches, n_levgrnd]
    froot_mr_by_layer = (
        frootn[:, None] * 
        br_root_adjusted[:, None] * 
        tcsoi_patch * 
        crootfr
    )
    
    # Sum over all layers to get total fine root MR
    froot_mr = jnp.sum(froot_mr_by_layer, axis=1)  # [n_patches]
    
    return froot_mr


def calculate_maintenance_respiration(
    canopy: CanopyState,
    soil: SoilState,
    temperature: TemperatureState,
    photosyns: PhotosynthesisState,
    nitrogen: NitrogenState,
    pft_constants: PFTConstants,
    patch_to_col: jnp.ndarray,
    params: MaintenanceRespirationParams,
    enable_acclimation: bool = False,
) -> MaintenanceRespirationFluxes:
    """Calculate maintenance respiration for all plant tissues.
    
    This is the main entry point for maintenance respiration calculations.
    It computes MR for leaves, fine roots, live stems, live coarse roots,
    and reproductive tissues based on tissue nitrogen content and temperature.
    
    Args:
        canopy: Canopy state (LAI, snow cover)
        soil: Soil state (root fractions)
        temperature: Temperature state (soil, air, 10-day mean)
        photosyns: Photosynthesis state (leaf MR rates)
        nitrogen: Vegetation nitrogen state (tissue N content)
        pft_constants: PFT-specific constants (woody, crop flags)
        patch_to_col: Mapping from patch to column index [n_patches]
        params: Respiration parameters
        enable_acclimation: Whether to apply acclimation adjustment
        
    Returns:
        Maintenance respiration fluxes for all tissues
        
    Reference:
        CNMRespMod.F90, subroutine CNMResp (lines ~140-260)
        
    Example:
        >>> params = create_default_params()
        >>> fluxes = calculate_maintenance_respiration(
        ...     canopy, soil, temperature, photosyns, nitrogen,
        ...     pft_constants, patch_to_col, params
        ... )
        >>> total_mr = (fluxes.leaf_mr + fluxes.froot_mr + 
        ...             fluxes.livestem_mr + fluxes.livecroot_mr)
        
    Note:
        - Leaf MR comes from photosynthesis model (already calculated)
        - Fine root MR integrates over soil layers with depth-dependent T
        - Woody tissue MR only for woody PFTs
        - Reproductive MR only for prognostic crops
        - Acclimation is experimental and may significantly affect results
    """
    # Calculate soil temperature corrections for fine root MR
    tcsoi = calculate_soil_temperature_corrections(
        temperature.t_soisno,
        params,
    )
    
    # Leaf maintenance respiration
    leaf_mr = calculate_leaf_maintenance_respiration(
        canopy,
        photosyns,
        params,
    )
    
    # Fine root maintenance respiration (integrated over soil layers)
    froot_mr = calculate_fine_root_maintenance_respiration(
        nitrogen.frootn,
        soil.crootfr,
        tcsoi,
        patch_to_col,
        temperature.t_10day,
        params,
        enable_acclimation,
    )
    
    # Live stem maintenance respiration (woody PFTs and crops)
    livestem_mr = calculate_stem_maintenance_respiration(
        nitrogen.livestemn,
        temperature.t_ref2m,
        temperature.t_10day,
        pft_constants.is_woody | pft_constants.is_crop,  # Both woody and crops
        params,
        enable_acclimation,
    )
    
    # Live coarse root maintenance respiration (woody PFTs only)
    livecroot_mr = calculate_coarse_root_maintenance_respiration(
        nitrogen.livecrootn,
        temperature.t_ref2m,
        temperature.t_10day,
        pft_constants.is_woody,
        params,
        enable_acclimation,
    )
    
    # Reproductive tissue maintenance respiration (crops only)
    reproductive_mr = calculate_reproductive_maintenance_respiration(
        nitrogen.reproductiven,
        temperature.t_ref2m,
        temperature.t_10day,
        pft_constants.is_crop,
        params,
        enable_acclimation,
    )
    
    return MaintenanceRespirationFluxes(
        leaf_mr=leaf_mr,
        froot_mr=froot_mr,
        livestem_mr=livestem_mr,
        livecroot_mr=livecroot_mr,
        reproductive_mr=reproductive_mr,
    )


def calculate_total_maintenance_respiration(
    fluxes: MaintenanceRespirationFluxes,
) -> jnp.ndarray:
    """Calculate total maintenance respiration across all tissues.
    
    Args:
        fluxes: Maintenance respiration fluxes for all tissues
        
    Returns:
        Total MR flux [gC/m2/s] [n_patches]
        
    Note:
        Reproductive MR is summed over all reproductive pools.
    """
    total_mr = (
        fluxes.leaf_mr +
        fluxes.froot_mr +
        fluxes.livestem_mr +
        fluxes.livecroot_mr +
        jnp.sum(fluxes.reproductive_mr, axis=1)
    )
    return total_mr