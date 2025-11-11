from jax_ctsm.soil.soil_state_type import (
    init_soil_state,
    create_simple_bounds,
)

# Create bounds for a small domain
bounds = create_simple_bounds(
    n_patches=100,
    n_columns=50,
    n_gridcells=25,
)

# Initialize soil state
soil_state = init_soil_state(bounds)

# Access soil properties
sand_content = soil_state.cellsand_col  # [50, 10]
hydraulic_conductivity = soil_state.hksat_col  # [50, 15]