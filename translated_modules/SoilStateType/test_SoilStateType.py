"""
Tests for soil state module.

Verifies initialization, updates, and indexing utilities.
"""

import jax.numpy as jnp
import pytest
from jax_ctsm.soil.soil_state import (
    SoilState,
    initialize_soil_state,
    update_soil_state,
    get_snow_layer_index,
    get_ground_layer_slice,
    get_snow_layer_slice,
)
from jax_ctsm.soil.soil_constants import DEFAULT_VERTICAL_DISCRETIZATION


def test_initialize_soil_state_shapes():
    """Test that initialization creates correct array shapes."""
    n_columns = 100
    n_patches = 500
    nlevsoi = 10
    nlevgrnd = 15
    nlevsno = 5
    
    state = initialize_soil_state(
        n_columns=n_columns,
        n_patches=n_patches,
        nlevsoi=nlevsoi,
        nlevgrnd=nlevgrnd,
        nlevsno=nlevsno,
    )
    
    # Check soil composition arrays
    assert state.cellorg_col.shape == (n_columns, nlevsoi)
    assert state.cellsand_col.shape == (n_columns, nlevsoi)
    assert state.cellclay_col.shape == (n_columns, nlevsoi)
    
    # Check hydraulic property arrays
    assert state.hksat_col.shape == (n_columns, nlevgrnd)
    assert state.hk_l_col.shape == (n_columns, nlevgrnd)
    assert state.smp_l_col.shape == (n_columns, nlevgrnd)
    assert state.bsw_col.shape == (n_columns, nlevgrnd)
    assert state.watsat_col.shape == (n_columns, nlevgrnd)
    assert state.sucsat_col.shape == (n_columns, nlevgrnd)
    
    # Check scalar column arrays
    assert state.dsl_col.shape == (n_columns,)
    assert state.soilresis_col.shape == (n_columns,)
    
    # Check thermal property arrays
    assert state.thk_col.shape == (n_columns, nlevsno + nlevgrnd)
    assert state.tkmg_col.shape == (n_columns, nlevgrnd)
    assert state.tkdry_col.shape == (n_columns, nlevgrnd)
    assert state.csol_col.shape == (n_columns, nlevgrnd)
    
    # Check root distribution
    assert state.rootfr_patch.shape == (n_patches, nlevgrnd)


def test_initialize_soil_state_values():
    """Test that initialization fills arrays with correct values."""
    state = initialize_soil_state(
        n_columns=10,
        n_patches=20,
        fill_value=jnp.nan,
    )
    
    # All values should be NaN
    assert jnp.all(jnp.isnan(state.cellsand_col))
    assert jnp.all(jnp.isnan(state.hksat_col))
    assert jnp.all(jnp.isnan(state.dsl_col))
    
    # Test with different fill value
    state_zeros = initialize_soil_state(
        n_columns=10,
        n_patches=20,
        fill_value=0.0,
    )
    
    assert jnp.all(state_zeros.cellsand_col == 0.0)
    assert jnp.all(state_zeros.hksat_col == 0.0)


def test_update_soil_state():
    """Test updating soil state fields."""
    state = initialize_soil_state(
        n_columns=10,
        n_patches=20,
        fill_value=0.0,
    )
    
    # Update a single field
    new_hksat = jnp.ones((10, 15))
    updated_state = update_soil_state(state, hksat_col=new_hksat)
    
    assert jnp.all(updated_state.hksat_col == 1.0)
    assert jnp.all(updated_state.cellsand_col == 0.0)  # Other fields unchanged
    
    # Update multiple fields
    new_watsat = jnp.full((10, 15), 0.5)
    new_dsl = jnp.full(10, 10.0)
    
    updated_state = update_soil_state(
        state,
        hksat_col=new_hksat,
        watsat_col=new_watsat,
        dsl_col=new_dsl,
    )
    
    assert jnp.all(updated_state.hksat_col == 1.0)
    assert jnp.all(updated_state.watsat_col == 0.5)
    assert jnp.all(updated_state.dsl_col == 10.0)


def test_snow_layer_indexing():
    """Test snow layer index conversion."""
    nlevsno = 5
    
    # First snow layer: Fortran -4 -> JAX 0
    assert get_snow_layer_index(-4, nlevsno) == 0
    
    # Last snow layer: Fortran 0 -> JAX 4
    assert get_snow_layer_index(0, nlevsno) == 4
    
    # First ground layer: Fortran 1 -> JAX 5
    assert get_snow_layer_index(1, nlevsno) == 5
    
    # Arbitrary ground layer: Fortran 10 -> JAX 14
    assert get_snow_layer_index(10, nlevsno) == 14


def test_layer_slicing():
    """Test layer slice utilities."""
    nlevsno = 5
    nlevgrnd = 15
    
    state = initialize_soil_state(
        n_columns=10,
        n_patches=20,
        nlevsno=nlevsno,
        nlevgrnd=nlevgrnd,
        fill_value=0.0,
    )
    
    # Set different values for snow and ground layers
    thk_modified = state.thk_col.at[:, :nlevsno].set(1.0)  # Snow layers
    thk_modified = thk_modified.at[:, nlevsno:].set(2.0)   # Ground layers
    
    state = update_soil_state(state, thk_col=thk_modified)
    
    # Test slicing
    snow_slice = get_snow_layer_slice(nlevsno)
    ground_slice = get_ground_layer_slice(nlevsno)
    
    assert jnp.all(state.thk_col[:, snow_slice] == 1.0)
    assert jnp.all(state.thk_col[:, ground_slice] == 2.0)
    
    # Check shapes
    assert state.thk_col[:, snow_slice].shape == (10, nlevsno)
    assert state.thk_col[:, ground_slice].shape == (10, nlevgrnd)


def test_immutability():
    """Test that SoilState is immutable."""
    state = initialize_soil_state(n_columns=10, n_patches=20)
    
    # Attempting to modify should raise an error
    with pytest.raises(AttributeError):
        state.hksat_col = jnp.ones((10, 15))
    
    # Update creates a new instance
    new_state = update_soil_state(state, hksat_col=jnp.ones((10, 15)))
    assert new_state is not state
    assert not jnp.array_equal(new_state.hksat_col, state.hksat_col)


def test_default_discretization():
    """Test using default vertical discretization."""
    disc = DEFAULT_VERTICAL_DISCRETIZATION
    
    state = initialize_soil_state(
        n_columns=10,
        n_patches=20,
        nlevsoi=disc.nlevsoi,
        nlevgrnd=disc.nlevgrnd,
        nlevsno=disc.nlevsno,
    )
    
    assert state.cellsand_col.shape == (10, disc.nlevsoi)
    assert state.hksat_col.shape == (10, disc.nlevgrnd)
    assert state.thk_col.shape == (10, disc.nlevsno + disc.nlevgrnd)