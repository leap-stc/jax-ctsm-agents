# In other modules
from jax_ctsm.control.clm_varctl import ClmVarCtl, create_default_clm_varctl

def some_clm_function(
    state: SomeState,
    config: ClmVarCtl,
) -> SomeOutput:
    """Function that needs access to control variables."""
    if config.iulog >= 0:
        # Logging logic
        pass
    # ... rest of function