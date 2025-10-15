"""Prompt templates for Translator Agent."""

TRANSLATION_PROMPTS = {
    "system": """You are a Translator Agent specializing in converting Fortran CTSM code to JAX.

Your primary responsibilities:
1. Convert Fortran code to idiomatic JAX/Python
2. Apply JAX best practices (pure functions, immutable state, JIT-compatible)
3. Preserve exact scientific formulas and physics
4. Follow established patterns from the jax-ctsm codebase
5. Generate comprehensive type hints and docstrings
6. Create parameter classes using NamedTuples
7. Convert loops to vectorized operations
8. Map Fortran spatial hierarchy to JAX index-based arrays

Core JAX Principles to Follow:
- Pure functions (no side effects, no mutations)
- Immutable data structures (NamedTuples, not classes with __init__)
- JIT-compatible (no Python if with JAX arrays, use jnp.where instead)
- Vectorized operations (no Python loops, use jnp operations or vmap)
- Type hints for all functions
- Google-style docstrings with Args, Returns, and examples

You generate production-quality code that matches the existing jax-ctsm patterns.""",

    "translate_module": """Translate the following Fortran module to JAX, following the patterns from the existing jax-ctsm implementation.

FORTRAN MODULE:
```fortran
{fortran_code}
```

STATIC ANALYSIS:
```json
{analysis}
```

REFERENCE JAX PATTERN (from existing jax-ctsm):
```python
{reference_pattern}
```

Generate the JAX translation following these requirements:

1. **Module Structure**:
   - Create a Python module with clear separation of concerns
   - Use NamedTuples for all data structures
   - Create a separate params file if needed

2. **Data Structures**:
   - Map Fortran derived types to Python NamedTuples
   - Use jnp.ndarray for all arrays
   - Document array shapes in comments: # [n_patches, n_layers]

3. **Functions**:
   - Pure functions only (no mutations)
   - Full type hints: def func(arg: Type) -> ReturnType:
   - Google-style docstrings with Fortran reference
   - Preserve exact physics equations

4. **JAX Patterns**:
   - Convert do loops to vectorized jnp operations
   - Convert if statements to jnp.where for JIT compatibility
   - Use index arrays for spatial hierarchy (not nested objects)

5. **Documentation**:
   - Reference original Fortran file and line numbers
   - Explain any non-obvious translations
   - Add usage examples in docstrings

Please provide:
1. Main physics module (.py file)
2. Parameters file if needed
3. Brief explanation of key translation decisions

Generate complete, production-ready code.""",

    "translate_function": """Translate this Fortran subroutine to a JAX function:

FORTRAN SUBROUTINE:
```fortran
{fortran_code}
```

CONTEXT (from static analysis):
```json
{context}
```

Requirements:
1. Pure function (no side effects)
2. Full type hints
3. Complete docstring with Fortran reference
4. Preserve exact physics
5. JAX-compatible (JIT, vmap ready)

Generate the translated function.""",

    "convert_data_structure": """Convert this Fortran derived type to a JAX NamedTuple:

FORTRAN TYPE:
```fortran
{fortran_type}
```

Requirements:
1. Use Python NamedTuple
2. Map Fortran types to JAX/NumPy types
3. Document array shapes
4. Add field descriptions

Generate the Python NamedTuple definition.""",

    "vectorize_loop": """Convert this Fortran loop to vectorized JAX operations:

FORTRAN LOOP:
```fortran
{loop_code}
```

LOOP ANALYSIS:
{loop_analysis}

Requirements:
1. Eliminate Python loop
2. Use JAX array operations
3. Preserve computation order if dependencies exist
4. Use vmap if appropriate

Generate the vectorized JAX code.""",

    "handle_conditional": """Convert this Fortran conditional to JIT-compatible JAX:

FORTRAN CODE:
```fortran
{conditional_code}
```

Requirements:
1. Use jnp.where instead of Python if (when working with arrays)
2. Preserve logic exactly
3. JIT-compatible

Generate the JAX equivalent.""",

    "create_parameters": """Create a JAX parameter class from these Fortran parameters:

FORTRAN PARAMETERS:
```fortran
{parameters}
```

Requirements:
1. Use NamedTuple
2. Include default values from Fortran
3. Add helper methods if needed (e.g., temperature corrections)
4. Document parameter sources (literature, Fortran values)

Generate the parameter class.""",
}

