"""
CLM Run Control Variables Module.

Translated from CTSM's clm_varctl.F90

This module contains run control variables used throughout CLM.
In the original Fortran, these are module-level variables that maintain
state across the simulation.

In JAX, we represent these as immutable configuration parameters stored
in a NamedTuple to maintain functional purity. This allows the configuration
to be passed explicitly through the computation graph while maintaining
JIT compatibility.

Key differences from Fortran:
    - Module variables → NamedTuple fields
    - Mutable state → Immutable configuration
    - Implicit global access → Explicit parameter passing

Usage: