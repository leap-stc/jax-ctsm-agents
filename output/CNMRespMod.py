"""
Maintenance Respiration Parameters.

Translated from CTSM's CNMRespMod.F90

Parameters for calculating maintenance respiration of plant tissues based on
nitrogen content and temperature.
"""

from typing import NamedTuple
import jax.numpy as jnp


class MaintenanceRespirationParams(NamedTuple):
    """Parameters for maintenance respiration calculations.
    
    Attributes:
        br: Base rate for maintenance respiration [gC/gN/s]
            Default: 2.525e-6 from Ryan (1991)
            Original: 0.0106 molC/(molN h), converted by molecular weights
        br_root: Base rate for root maintenance respiration [gC/gN/s]
            Can differ from br if acclimation is enabled
            Default: same as br
        q10: Temperature sensitivity parameter [dimensionless]
            Default: 1.5 (tuned from original 2.0)
            Controls exponential temperature response
        t_ref: Reference temperature for Q10 calculation [°C]
            Default: 20.0
        t_ref_acclim: Reference temperature for acclimation [°C]
            Default: 25.0
        acclim_coef: Acclimation coefficient [1/°C]
            Default: -0.00794
            Used in root/stem respiration acclimation
        umol_to_gc: Conversion factor from umol CO2 to gC
            Default: 12.011e-6 [gC/umol]
        t_freeze: Freezing point of water [K]
            Default: 273.15
            
    Reference:
        Ryan, M. (1991). Effects of climate change on plant respiration.
        Ecological Applications, 1(2), 157-167.
        
        Thornton, P. (2009). Q10 reduced from 2.0 to 1.5 for tuning
        seasonal cycle of atmospheric CO2.
    """
    br: float = 2.525e-6
    br_root: float = 2.525e-6
    q10: float = 1.5
    t_ref: float = 20.0
    t_ref_acclim: float = 25.0
    acclim_coef: float = -0.00794
    umol_to_gc: float = 12.011e-6
    t_freeze: float = 273.15
    
    def with_br_root(self, br_root: float) -> 'MaintenanceRespirationParams':
        """Create new params with custom br_root value.
        
        Args:
            br_root: Custom root base rate [gC/gN/s]
            
        Returns:
            New params instance with updated br_root
        """
        return self._replace(br_root=br_root)
    
    def get_temp_correction(
        self,
        temperature: jnp.ndarray,
    ) -> jnp.ndarray:
        """Calculate Q10 temperature correction factor.
        
        Implements: Q10^((T - T_ref) / 10)
        
        Args:
            temperature: Temperature [K] [...]
            
        Returns:
            Temperature correction factor [dimensionless] [...]
            
        Reference:
            CNMRespMod.F90, line ~200:
            tc = Q10**((t_ref2m(p)-SHR_CONST_TKFRZ - 20.0_r8)/10.0_r8)
        """
        temp_c = temperature - self.t_freeze
        return self.q10 ** ((temp_c - self.t_ref) / 10.0)
    
    def get_acclimation_factor(
        self,
        t_10day: jnp.ndarray,
        enable_acclimation: bool = False,
    ) -> jnp.ndarray:
        """Calculate acclimation adjustment factor for root/stem respiration.
        
        Implements: 10^(acclim_coef * (T_10day - T_ref_acclim))
        
        This is an experimental feature that adjusts base respiration rates
        based on 10-day running mean temperature.
        
        Args:
            t_10day: 10-day running mean temperature [K] [...]
            enable_acclimation: Whether to apply acclimation
            
        Returns:
            Acclimation factor [dimensionless] [...]
            Returns 1.0 if acclimation disabled
            
        Reference:
            CNMRespMod.F90, line ~210:
            br = br * 10._r8**(-0.00794_r8*((t10(p)-tfrz)-25._r8))
            
        Note:
            This feature is experimental and may increase respiration
            in boreal forests significantly.
        """
        if not enable_acclimation:
            return jnp.ones_like(t_10day)
        
        temp_c = t_10day - self.t_freeze
        return 10.0 ** (self.acclim_coef * (temp_c - self.t_ref_acclim))


def create_default_params(
    br_root: float | None = None,
) -> MaintenanceRespirationParams:
    """Create default maintenance respiration parameters.
    
    Args:
        br_root: Optional custom root base rate [gC/gN/s]
                If None, uses same value as br
                
    Returns:
        Default parameter set
        
    Example:
        >>> params = create_default_params()
        >>> params.br
        2.525e-06
        >>> params_custom = create_default_params(br_root=3.0e-6)
        >>> params_custom.br_root
        3e-06
    """
    params = MaintenanceRespirationParams()
    if br_root is not None:
        params = params.with_br_root(br_root)
    return params