# Unit test example
def test_temperature_correction():
    params = create_default_params()
    t_kelvin = jnp.array([293.15, 303.15])  # 20°C, 30°C
    tc = params.get_temp_correction(t_kelvin)
    # At 20°C (reference): tc = 1.5^0 = 1.0
    # At 30°C: tc = 1.5^1 = 1.5
    assert jnp.allclose(tc[0], 1.0)
    assert jnp.allclose(tc[1], 1.5)