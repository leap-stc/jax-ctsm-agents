# SoilTemperatureMod Test Suite Documentation

## Test Suite Overview

This test suite provides comprehensive validation for the `SoilTemperatureMod` module, which implements soil and snow temperature calculations using implicit finite difference methods for land surface modeling.

### Functions Tested

1. **`soil_temperature`** (Main function)
   - Solves heat diffusion equation for soil/snow layers
   - Computes thermal properties (conductivity, heat capacity)
   - Updates temperatures using implicit time-stepping
   - Returns updated temperatures and thermal properties

2. **Helper Functions**
   - `soil_thermal_properties` - Computes thermal conductivity and heat capacity
   - `calculate_soil_thermal_conductivity` - Farouki (1981) method
   - `calculate_snow_thermal_conductivity` - Jordan (1991) method
   - `calculate_interface_thermal_conductivity` - Harmonic mean method
   - `calculate_heat_capacity` - de Vries (1963) method
   - `setup_tridiagonal_system` - Builds implicit finite difference system
   - `solve_tridiagonal` - Thomas algorithm solver
   - `check_energy_conservation` - Energy balance verification

### Test Statistics

- **Total Test Cases**: 10 parametrized cases
- **Test Types**: 
  - Nominal cases: 4 (typical operational conditions)
  - Edge cases: 4 (boundary conditions, extreme values)
  - Special cases: 2 (physical edge cases, numerical stability)
- **Array Dimensions Tested**: Multiple column and level configurations
- **Physical Scenarios**: Frozen soil, thawed soil, snow-covered, bare ground

### Coverage Areas

#### Physical Processes
- Heat conduction in soil layers
- Snow layer thermal dynamics
- Phase change effects (ice/water)
- Surface water thermal effects
- Bedrock boundary conditions

#### Numerical Methods
- Implicit finite difference scheme
- Tridiagonal matrix solver (Thomas algorithm)
- Interface thermal conductivity (harmonic mean)
- Energy conservation checks

#### Edge Cases
- Zero snow cover
- Maximum snow layers
- Frozen vs. thawed conditions
- Extreme temperatures (-100°C to 100°C)
- Minimal layer thickness
- Zero water content
- Saturated conditions

#### Input Validation
- Array shape consistency
- Physical constraint satisfaction
- Numerical stability (NaN/Inf handling)
- Boundary condition enforcement

---

## Running the Tests

### Basic Execution

```bash
# Run all tests
pytest test_SoilTemperatureMod.py

# Run with verbose output
pytest test_SoilTemperatureMod.py -v

# Run specific test
pytest test_SoilTemperatureMod.py::test_soil_temperature -v
```

### Coverage Analysis

```bash
# Generate coverage report
pytest test_SoilTemperatureMod.py --cov=SoilTemperatureMod --cov-report=html

# View coverage in terminal
pytest test_SoilTemperatureMod.py --cov=SoilTemperatureMod --cov-report=term-missing

# Generate XML report for CI/CD
pytest test_SoilTemperatureMod.py --cov=SoilTemperatureMod --cov-report=xml
```

### Filtering Tests

```bash
# Run only nominal cases
pytest test_SoilTemperatureMod.py -k "nominal"

# Run only edge cases
pytest test_SoilTemperatureMod.py -k "edge"

# Run only special cases
pytest test_SoilTemperatureMod.py -k "special"

# Skip slow tests (if marked)
pytest test_SoilTemperatureMod.py -m "not slow"
```

### Debugging

```bash
# Stop on first failure
pytest test_SoilTemperatureMod.py -x

# Show local variables on failure
pytest test_SoilTemperatureMod.py -l

# Enter debugger on failure
pytest test_SoilTemperatureMod.py --pdb

# Show print statements
pytest test_SoilTemperatureMod.py -s
```

---

## Test Cases

### Nominal Cases (Typical Operations)

#### 1. **Standard Summer Conditions**
- **Description**: Warm soil, no snow, moderate moisture
- **Key Parameters**:
  - Temperature: 288K (15°C)
  - No snow layers (snl=0)
  - Moderate soil moisture (50% saturation)
  - Standard time step (1800s)
- **Expected**: Stable temperature evolution, positive heat capacity

#### 2. **Winter Frozen Soil**
- **Description**: Cold temperatures, frozen soil, snow cover
- **Key Parameters**:
  - Temperature: 263K (-10°C)
  - 3 snow layers (snl=-3)
  - High ice content
  - Snow fraction: 0.8
- **Expected**: Lower thermal conductivity in snow, phase change effects

#### 3. **Spring Thaw Transition**
- **Description**: Temperatures near freezing, mixed phase
- **Key Parameters**:
  - Temperature: 273K (0°C)
  - Both liquid water and ice present
  - Partial snow cover (frac_sno=0.3)
- **Expected**: Latent heat effects, gradual temperature change

#### 4. **Multi-Column Simulation**
- **Description**: Multiple spatial locations with varying conditions
- **Key Parameters**:
  - 5 columns with different properties
  - Varying snow cover, moisture, temperature
- **Expected**: Independent column evolution, vectorized computation

### Edge Cases (Boundary Conditions)

#### 5. **Extreme Cold**
- **Description**: Very low temperatures near physical minimum
- **Key Parameters**:
  - Temperature: 173K (-100°C)
  - Minimal moisture
  - High thermal conductivity contrast
- **Expected**: Numerical stability, no NaN/Inf values
- **Physical Relevance**: Polar regions, high-altitude sites

#### 6. **Extreme Heat**
- **Description**: High temperatures near boiling point
- **Key Parameters**:
  - Temperature: 323K (50°C)
  - Dry soil conditions
  - High surface heat flux (150 W/m²)
- **Expected**: Stable solution, realistic heat diffusion
- **Physical Relevance**: Desert environments, summer conditions

#### 7. **Zero Water Content**
- **Description**: Completely dry soil
- **Key Parameters**:
  - h2osoi_liq = 0
  - h2osoi_ice = 0
  - h2osno = 0
  - h2osfc = 0
- **Expected**: Dry soil thermal properties, no phase change
- **Physical Relevance**: Arid regions, drought conditions

#### 8. **Saturated Soil**
- **Description**: Maximum water content at porosity limit
- **Key Parameters**:
  - Water content = watsat (porosity)
  - High thermal conductivity
  - Large heat capacity
- **Expected**: Maximum thermal inertia, slow temperature change
- **Physical Relevance**: Wetlands, post-precipitation

### Special Cases (Numerical Stability)

#### 9. **Minimal Layer Thickness**
- **Description**: Very thin layers testing numerical stability
- **Key Parameters**:
  - dz = 1e-10 m (minimum allowed)
  - Small time step (60s)
  - Standard conditions otherwise
- **Expected**: Stable solution, no division by zero
- **Purpose**: Tests numerical robustness

#### 10. **Maximum Snow Layers**
- **Description**: Deep snowpack with maximum layer count
- **Key Parameters**:
  - snl = -5 (5 snow layers)
  - High snow water equivalent (500 mm)
  - Full snow cover (frac_sno=1.0)
- **Expected**: Correct snow thermal properties, stable solution
- **Physical Relevance**: Deep snowpack regions, avalanche zones

---

## Test Data

### Generation Strategy

Test data is generated using pytest fixtures with the following approach:

#### 1. **Fixture-Based Data Generation**
```python
@pytest.fixture
def soil_temp_params():
    """Physical constants for soil temperature calculations"""
    return SoilTemperatureParams(
        denh2o=1000.0,      # Water density [kg/m³]
        denice=917.0,       # Ice density [kg/m³]
        tfrz=273.15,        # Freezing point [K]
        tkwat=0.57,         # Water thermal conductivity [W/m/K]
        tkice=2.29,         # Ice thermal conductivity [W/m/K]
        tkair=0.023,        # Air thermal conductivity [W/m/K]
        cpice=2117.27,      # Ice heat capacity [J/kg/K]
        cpliq=4188.0,       # Water heat capacity [J/kg/K]
        thk_bedrock=3.0,    # Bedrock thermal conductivity [W/m/K]
        csol_bedrock=2.0e6, # Bedrock heat capacity [J/m³/K]
        thin_sfclayer=0.007 # Thin surface layer threshold [m]
    )
```

#### 2. **Parametrized Test Data**
Each test case is defined with:
- **Case ID**: Descriptive name (e.g., "nominal_summer", "edge_extreme_cold")
- **Array Dimensions**: (n_columns, n_levels) tuples
- **Physical Parameters**: Temperature, moisture, snow properties
- **Expected Behavior**: Pass/fail criteria, tolerance levels

#### 3. **Physical Realism Constraints**
All generated data satisfies:
- **Temperature**: T > 0K, typically 173K < T < 373K
- **Fractions**: 0 ≤ f ≤ 1 (watsat, frac_sno)
- **Non-negative**: All mass/energy quantities ≥ 0
- **Geometric**: z, zi increasing with depth; dz > 0
- **Thermal Properties**: Realistic ranges for soil/snow

#### 4. **Coverage Matrix**

| Dimension | Values Tested | Purpose |
|-----------|---------------|---------|
| n_columns | 1, 3, 5 | Single/multi-column |
| n_levels | 10, 15, 20 | Shallow/deep profiles |
| snl | 0, -3, -5 | No snow to deep snow |
| Temperature | 173K, 263K, 273K, 288K, 323K | Cold to hot |
| Moisture | 0%, 50%, 100% saturation | Dry to saturated |
| Time step | 60s, 1800s, 3600s | Fine to coarse |

### Data Validation

Each test case includes validation for:
1. **Input Constraints**: All parameters within physical bounds
2. **Array Shapes**: Consistent dimensions across all inputs
3. **Geometric Consistency**: z[i] < z[i+1], zi defines layer boundaries
4. **Mass Balance**: Total water = liquid + ice
5. **Energy Balance**: Heat flux consistency

---

## Expected Behavior

### Passing Tests Should Demonstrate

#### 1. **Physical Correctness**
- ✅ Temperatures remain above absolute zero
- ✅ Heat flows from hot to cold (second law of thermodynamics)
- ✅ Energy is conserved (within numerical tolerance)
- ✅ Phase change occurs near freezing point
- ✅ Thermal properties in realistic ranges

#### 2. **Numerical Stability**
- ✅ No NaN or Inf values in outputs
- ✅ Solution converges for all time steps
- ✅ Tridiagonal solver produces valid results
- ✅ Implicit scheme is unconditionally stable
- ✅ Handles extreme parameter values gracefully

#### 3. **Computational Efficiency**
- ✅ Vectorized operations over columns
- ✅ O(n) complexity for tridiagonal solve
- ✅ JAX JIT compilation successful
- ✅ Reasonable execution time (<1s for typical cases)

#### 4. **Output Validity**
- ✅ Temperature array shape matches input
- ✅ Thermal properties have correct dimensions
- ✅ All NamedTuple fields populated
- ✅ Values within expected physical ranges

### Failure Modes and Diagnostics

#### Common Failure Scenarios

1. **Shape Mismatch**
   ```
   AssertionError: Temperature array shape mismatch
   Expected: (5, 15), Got: (5, 14)
   ```
   - **Cause**: Incorrect handling of snow layers or bedrock
   - **Fix**: Check snl indexing and level counting

2. **Physical Constraint Violation**
   ```
   AssertionError: Negative temperature detected
   Min temperature: -5.2K
   ```
   - **Cause**: Numerical instability or incorrect boundary conditions
   - **Fix**: Reduce time step, check heat flux inputs

3. **Energy Conservation Error**
   ```
   AssertionError: Energy not conserved
   Relative error: 0.15 (tolerance: 0.01)
   ```
   - **Cause**: Accumulation of numerical errors
   - **Fix**: Verify tridiagonal solver, check interface conductivity

4. **NaN/Inf Propagation**
   ```
   AssertionError: NaN values in output
   Location: column 2, level 8
   ```
   - **Cause**: Division by zero, invalid thermal properties
   - **Fix**: Check for zero layer thickness, validate input data

### Tolerance Levels

| Quantity | Absolute Tolerance | Relative Tolerance | Justification |
|----------|-------------------|-------------------|---------------|
| Temperature | 1e-6 K | 1e-8 | High precision needed |
| Thermal Conductivity | 1e-8 W/m/K | 1e-6 | Moderate precision |
| Heat Capacity | 1e-3 J/m³/K | 1e-6 | Large values, relative matters |
| Energy Balance | - | 1e-2 (1%) | Accumulated numerical error |

---

## Extending Tests

### Adding New Test Cases

#### 1. **Add to Parametrize Decorator**

```python
@pytest.mark.parametrize("case_id, n_columns, n_levels, ...", [
    # Existing cases...
    
    # New case: Your scenario
    pytest.param(
        "custom_scenario_name",
        3,  # n_columns
        12,  # n_levels
        280.0,  # temperature
        # ... other parameters
        id="custom_scenario_name"
    ),
])
def test_soil_temperature(case_id, n_columns, n_levels, ...):
    # Test implementation
```

#### 2. **Create Specialized Fixture**

```python
@pytest.fixture
def permafrost_conditions():
    """Test data for permafrost scenarios"""
    return {
        'temperature': 263.0,  # -10°C
        'ice_fraction': 0.9,   # Mostly frozen
        'active_layer_depth': 0.5,  # 50cm thaw depth
        # ... additional parameters
    }

def test_permafrost_dynamics(permafrost_conditions, soil_temp_params):
    """Test permafrost-specific behavior"""
    # Use fixture data
    # Run simulation
    # Assert permafrost-specific conditions
```

#### 3. **Add Property-Based Tests**

```python
from hypothesis import given, strategies as st

@given(
    temperature=st.floats(min_value=173.15, max_value=373.15),
    moisture=st.floats(min_value=0.0, max_value=1.0),
)
def test_temperature_monotonicity(temperature, moisture):
    """Property: Temperature should evolve smoothly"""
    # Generate inputs with random but valid parameters
    # Run simulation
    # Assert monotonicity or other properties
```

### Adding New Assertions

#### Energy Balance Check
```python
def test_energy_conservation_detailed(test_data):
    """Verify energy balance at each time step"""
    t_new, props = soil_temperature(**test_data)
    
    # Calculate energy change
    delta_E = calculate_energy_change(test_data['t_soisno'], t_new, props.cv)
    
    # Calculate heat flux integral
    Q_net = integrate_heat_flux(test_data['gsoi'], test_data['dtime'])
    
    # Assert balance
    assert jnp.abs(delta_E - Q_net) / Q_net < 0.01, \
        f"Energy not conserved: ΔE={delta_E}, Q_net={Q_net}"
```

#### Phase Change Verification
```python
def test_phase_change_latent_heat(test_data):
    """Verify latent heat effects during freezing/thawing"""
    # Set temperature near freezing
    test_data['t_soisno'] = jnp.full_like(test_data['t_soisno'], 273.15)
    
    t_new, props = soil_temperature(**test_data)
    
    # Check for temperature plateau at freezing point
    near_freezing = jnp.abs(t_new - 273.15) < 0.1
    assert jnp.any(near_freezing), "No phase change plateau detected"
```

### Performance Benchmarking

```python
import time

@pytest.mark.benchmark
def test_performance_scaling(benchmark):
    """Benchmark performance vs. problem size"""
    sizes = [(1, 10), (10, 10), (100, 10), (1000, 10)]
    times = []
    
    for n_cols, n_levs in sizes:
        test_data = generate_test_data(n_cols, n_levs)
        
        start = time.time()
        soil_temperature(**test_data)
        elapsed = time.time() - start
        
        times.append(elapsed)
    
    # Assert linear scaling
    assert times[-1] / times[0] < len(sizes) * 2, \
        "Performance scaling worse than linear"
```

---

## Common Issues

### Issue 1: JAX Array Mutability

**Problem**: Attempting to modify JAX arrays in-place
```python
# ❌ Wrong
t_soisno[0, 0] = 273.15

# ✅ Correct
t_soisno = t_soisno.at[0, 0].set(273.15)
```

**Solution**: Use JAX's `.at[]` indexing for updates

### Issue 2: Shape Broadcasting Errors

**Problem**: Incompatible array shapes in operations
```
ValueError: operands could not be broadcast together with shapes (5,15) (5,)
```

**Solution**: 
- Check array dimensions carefully
- Use `jnp.expand_dims()` or reshape to match dimensions
- Verify fixture data generation

### Issue 3: Numerical Precision

**Problem**: Tests fail due to floating-point precision
```python
# ❌ Too strict
assert result == expected

# ✅ Use tolerance
assert jnp.allclose(result, expected, rtol=1e-6, atol=1e-8)
```

**Solution**: Always use `jnp.allclose()` or `jnp.isclose()` with appropriate tolerances

### Issue 4: Random Seed for Reproducibility

**Problem**: Tests pass/fail randomly due to stochastic data generation

**Solution**:
```python
@pytest.fixture(autouse=True)
def set_random_seed():
    """Ensure reproducible random data"""
    jax.random.PRNGKey(42)
    np.random.seed(42)
```

### Issue 5: Memory Issues with Large Arrays

**Problem**: Out-of-memory errors with large test cases

**Solution**:
```python
# Use smaller test cases
@pytest.mark.parametrize("n_columns", [1, 10])  # Not 1000
def test_large_scale(n_columns):
    # Or use pytest-xdist for parallel execution
    # pytest -n auto test_SoilTemperatureMod.py
```

### Issue 6: Slow Test Execution

**Problem**: Tests take too long to run

**Solutions**:
1. **Mark slow tests**:
   ```python
   @pytest.mark.slow
   def test_long_simulation():
       # Skip with: pytest -m "not slow"
   ```

2. **Use JAX JIT compilation**:
   ```python
   @jax.jit
   def soil_temperature_jitted(*args):
       return soil_temperature(*args)
   ```

3. **Reduce test case complexity**:
   - Fewer columns/levels for unit tests
   - Save integration tests for CI/CD

### Issue 7: Fixture Scope Issues

**Problem**: Expensive fixtures recreated for each test

**Solution**:
```python
@pytest.fixture(scope="module")  # Create once per module
def expensive_params():
    # Expensive computation
    return params
```

### Issue 8: Debugging Failed Tests

**Strategy**:
```bash
# 1. Run with verbose output
pytest test_SoilTemperatureMod.py::test_soil_temperature -v

# 2. Show local variables
pytest test_SoilTemperatureMod.py::test_soil_temperature -l

# 3. Enter debugger
pytest test_SoilTemperatureMod.py::test_soil_temperature --pdb

# 4. Print intermediate values
pytest test_SoilTemperatureMod.py::test_soil_temperature -s
```

**Add diagnostic output**:
```python
def test_soil_temperature(test_data):
    print(f"\nInput shapes: {test_data['t_soisno'].shape}")
    
    t_new, props = soil_temperature(**test_data)
    
    print(f"Output shapes: {t_new.shape}")
    print(f"Temperature range: [{t_new.min()}, {t_new.max()}]")
    
    assert t_new.shape == test_data['t_soisno'].shape
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test SoilTemperatureMod

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install jax jaxlib pytest pytest-cov
      - name: Run tests
        run: |
          pytest test_SoilTemperatureMod.py --cov=SoilTemperatureMod --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

---

## References

### Scientific Methods Implemented
1. **Farouki (1981)**: Soil thermal conductivity parameterization
2. **Jordan (1991)**: Snow thermal conductivity
3. **de Vries (1963)**: Soil heat capacity
4. **Crank-Nicolson**: Implicit finite difference scheme

### Testing Resources
- [pytest documentation](https://docs.pytest.org/)
- [JAX testing guide](https://jax.readthedocs.io/en/latest/notebooks/testing.html)
- [NumPy testing utilities](https://numpy.org/doc/stable/reference/routines.testing.html)

---

## Contact and Support

For questions or issues with the test suite:
1. Check this documentation first
2. Review test output carefully
3. Examine fixture definitions
4. Consult module documentation
5. Open an issue with minimal reproducible example

**Last Updated**: 2024
**Test Suite Version**: 1.0
**Module Version**: Compatible with SoilTemperatureMod v1.x