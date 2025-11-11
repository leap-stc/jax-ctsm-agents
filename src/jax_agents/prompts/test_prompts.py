"""
Prompts for the Test Agent.

These prompts guide Claude in:
- Analyzing function signatures
- Generating synthetic test data
- Creating Fortran test harnesses
- Generating pytest files
- Creating test reports
"""

TEST_PROMPTS = {
    "system": """You are an expert Testing Agent specializing in validating Fortran-to-JAX translations.

Your expertise includes:
- Fortran 90/95 and modern Fortran syntax and semantics
- Python, JAX, and NumPy
- Scientific computing and numerical methods
- Test-driven development and validation strategies
- Fortran-Python interoperability

Your responsibilities:
1. Analyze Fortran and Python function signatures to understand inputs/outputs
2. Generate realistic synthetic test data covering edge cases
3. Create Fortran test harnesses that can read inputs and write outputs
4. Generate comprehensive pytest files for continuous testing
5. Produce detailed test reports comparing implementations

You follow these principles:
- Generate physically realistic test data
- Cover edge cases (zeros, negatives, boundaries, NaN/Inf)
- Use appropriate tolerances for floating-point comparison
- Provide clear, actionable test reports
- Ensure test harnesses are robust and compilable

You communicate clearly and provide complete, working code.""",

    "analyze_fortran_signature": """Analyze the following Fortran subroutine and extract its signature.

Module: {module_name}

Fortran Code:
```fortran
{fortran_code}
```

Please extract:
1. Subroutine/function name
2. All parameters with:
   - Name
   - Type (real, integer, logical, etc.)
   - Dimension/shape (scalar, 1D, 2D, etc.)
   - Intent (in, out, inout)
   - Default values or ranges (if any comments indicate)
3. Any module-level parameters or constants used
4. Dependencies on other modules

Return the analysis as a JSON object with the following structure:
```json
{{
  "name": "subroutine_name",
  "type": "subroutine" or "function",
  "parameters": [
    {{
      "name": "param_name",
      "fortran_type": "real(r8)",
      "dimension": "(:)" or "(:,:)" or "",
      "intent": "in" or "out" or "inout",
      "description": "brief description",
      "physical_range": {{"min": 0, "max": 1}} or null
    }}
  ],
  "constants": [
    {{
      "name": "constant_name",
      "value": 1.23,
      "description": "brief description"
    }}
  ],
  "dependencies": ["module1", "module2"]
}}
```

Be thorough and precise. This information will be used to generate test data.""",

    "analyze_python_signature": """Analyze the following Python/JAX function and extract its signature.

Module: {module_name}

Python Code:
```python
{python_code}
```

Please extract:
1. Function name
2. All parameters with:
   - Name
   - Python type hint
   - JAX array shape (if applicable)
   - Default values
   - Description from docstring
3. Return type and structure
4. Any NamedTuple or dataclass definitions used

Return the analysis as a JSON object with the following structure:
```json
{{
  "name": "function_name",
  "parameters": [
    {{
      "name": "param_name",
      "python_type": "jnp.ndarray" or "float" etc.,
      "shape": "(n, m)" or null,
      "default": null or value,
      "description": "brief description",
      "physical_range": {{"min": 0, "max": 1}} or null
    }}
  ],
  "returns": {{
    "type": "jnp.ndarray" or "tuple" or "NamedTuple",
    "structure": "description of return structure",
    "components": ["component1", "component2"]
  }},
  "namedtuples": [
    {{
      "name": "TupleName",
      "fields": ["field1", "field2"]
    }}
  ]
}}
```

Be thorough and precise. This information will be used to generate test data and compare outputs.""",

    "generate_test_data": """Generate synthetic test data for validating a Fortran-to-Python translation.

Fortran Signature:
```json
{fortran_signature}
```

Python Signature:
```json
{python_signature}
```

Number of test cases: {num_cases}

Existing CLM tests (if any): {clm_tests}

Please generate {num_cases} test cases that:
1. Cover typical/nominal cases
2. Include edge cases:
   - Zero values
   - Negative values (where appropriate)
   - Boundary values
   - Very small/large values
3. Are physically realistic (e.g., temperatures in Kelvin > 0)
4. Test different array sizes (if parameters have variable dimensions)
5. If CLM tests are provided, incorporate their test patterns

Return as JSON:
```json
{{
  "function_name": "function_name_from_python",
  "test_cases": [
    {{
      "name": "test_case_1_description",
      "inputs": {{
        "param1": value_or_array,
        "param2": value_or_array
      }},
      "metadata": {{
        "description": "what this test case covers",
        "edge_cases": ["zero_values", "negative_temps"]
      }}
    }}
  ],
  "data_generation_notes": "Notes about how data was generated and what assumptions were made"
}}
```

For arrays, use nested lists (e.g., [[1,2],[3,4]] for 2D array).
For scalars, use numeric values.
Ensure all input dimensions are consistent within each test case.""",

    "create_fortran_harness": """Create a STANDALONE Fortran test harness that can read test data and execute the original subroutine.

Original Fortran Code:
```fortran
{fortran_code}
```

Fortran Signature:
```json
{fortran_signature}
```

Test Data Structure:
```json
{test_data_structure}
```

Module: {module_name}

IMPORTANT: Create a STANDALONE program that does NOT depend on external modules.

Requirements:
1. Define `r8` precision directly: `integer, parameter :: r8 = selected_real_kind(15, 307)`
2. Replace any `use` statements with direct type definitions
3. Include simplified versions of any required constants (e.g., denh2o=1000.0_r8, tfrz=273.15_r8)
4. Copy the ENTIRE subroutine body inline (don't reference external modules)
5. Declare all necessary variables matching the subroutine signature
6. Read input data from stdin in JSON format
7. Write output data to stdout in simple format: variable_name=value
8. Handle arrays properly (Fortran array order)

The harness should be:
- Compilable with ONLY gfortran (no external dependencies)
- Self-contained (all code inline)
- Able to read JSON-like input from stdin
- Able to write simple key=value output to stdout

Structure:
```fortran
program test_{module_name}
  implicit none
  
  ! Define precision
  integer, parameter :: r8 = selected_real_kind(15, 307)
  
  ! Define necessary constants
  real(r8), parameter :: denh2o = 1000.0_r8
  real(r8), parameter :: tfrz = 273.15_r8
  ! ... other constants ...
  
  ! Declare variables
  real(r8) :: var1, var2
  real(r8), dimension(10) :: array1
  ! ... other variables ...
  
  ! Read inputs from stdin
  read(*,*) var1
  read(*,*) var2
  ! ... read other inputs ...
  
  ! Call subroutine (inline below)
  call subroutine_name(var1, var2, array1, ...)
  
  ! Write outputs to stdout
  write(*,'(A,E20.12)') 'var1=', var1
  write(*,'(A,E20.12)') 'var2=', var2
  ! ... write other outputs ...
  
contains

  subroutine subroutine_name(var1, var2, array1, ...)
    ! Copy the ENTIRE subroutine body here
    ! Replace module dependencies with local definitions
  end subroutine

end program
```

Return only the complete, standalone Fortran code that can be compiled without any external dependencies.""",

    "generate_pytest": """Generate a pytest file for the translated Python function.

Module: {module_name}

Python Signature:
```json
{python_signature}
```

Test Data:
```json
{test_data}
```

Test Results Summary:
```json
{test_results_summary}
```

Create a comprehensive pytest file that:
1. Imports the translated module
2. Defines test fixtures for test data
3. Creates individual test functions for each test case
4. Tests:
   - Basic functionality
   - Edge cases
   - Array shapes
   - Output types
   - Numerical accuracy (with appropriate tolerances)
5. Uses pytest.mark.parametrize for test cases
6. Includes docstrings explaining what each test does
7. Uses appropriate assertions (np.allclose for arrays, == for scalars)

Follow pytest best practices:
- Clear test names (test_<what>_<condition>_<expected>)
- Use fixtures for common setup
- Good error messages in assertions
- Proper tolerance for floating-point comparisons

Return only the Python pytest code.""",

    "generate_report": """Generate a comprehensive test report comparing Fortran and Python implementations.

Module: {module_name}

Fortran Signature:
```json
{fortran_signature}
```

Python Signature:
```json
{python_signature}
```

Test Results:
```json
{test_results}
```

Create a detailed markdown report that includes:

## Executive Summary
- Overall test status (pass/fail)
- Number of tests passed/failed
- Key findings

## Test Configuration
- Number of test cases
- Tolerance settings
- Compilation flags

## Detailed Results
For each test case:
- Test name and description
- Input summary
- Pass/fail status
- Error metrics (max absolute error, max relative error, RMS error)
- Output comparison

## Error Analysis
- Maximum errors observed
- Variables with largest discrepancies
- Potential causes of differences

## Performance Comparison
- Execution time comparison
- Speedup or slowdown

## Recommendations
- Is the translation validated?
- Any concerns or issues?
- Suggestions for improvement

Use tables for numerical data.
Use clear formatting with markdown.
Be specific about any failures or concerns.

Return the complete markdown report.""",
}

