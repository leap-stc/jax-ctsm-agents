# Initialize parameters
params = SoilTemperatureParams()

# Set up geometry, water, and soil states
geom = ColumnGeometry(dz=..., z=..., zi=..., snl=..., nbedrock=...)
water = WaterState(h2osoi_liq=..., h2osoi_ice=..., ...)
soil = SoilState(tkmg=..., tkdry=..., csol=..., watsat=...)

# Compute soil temperature
result, thermal_props = compute_soil_temperature(
    geom=geom,
    t_soisno=initial_temperature,
    gsoi=ground_heat_flux,
    water=water,
    soil=soil,
    params=params,
    dtime=1800.0,  # 30-minute timestep
    nlevsno=5,
    nlevgrnd=15,
)

# Access results
new_temperature = result.t_soisno
energy_error = result.energy_error
thermal_conductivity = thermal_props.tk
heat_capacity = thermal_props.cv