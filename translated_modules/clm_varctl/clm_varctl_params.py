from jax_ctsm.control.clm_varctl import ClmVarCtl, create_default_clm_varctl
    
    # Create configuration
    config = create_default_clm_varctl()
    
    # Or customize
    config = ClmVarCtl(iulog=7)
    
    # Pass to functions that need it
    result = some_clm_function(state, config)