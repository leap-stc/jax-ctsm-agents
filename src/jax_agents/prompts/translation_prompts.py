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

MODULE: {module_name}

FORTRAN SOURCE CODE:
```fortran
{fortran_code}
```

MODULE ANALYSIS (from analysis_results.json):
```json
{module_info}
```

ENHANCED CONTEXT (dependencies, translation units, complexity):
```json
{enhanced_context}
```

REFERENCE JAX PATTERN (from existing jax-ctsm):
```python
{reference_pattern}
```

IMPORTANT TRANSLATION CONTEXT:
The enhanced context above includes:
- **Dependencies**: What modules this module uses and what modules use it
- **Translation Units**: Breakdown of this module into translatable units with complexity scores
- **Complexity Info**: Effort estimates and whether large functions have been split
- **Translation Units Guide**: Each unit has:
  - unit_type: "module" (module header), "root" (complete function), "inner" (part of split function)
  - line_start/line_end: Exact location in source file
  - complexity_score: Relative difficulty (higher = more complex)
  - estimated_effort: "low", "medium", or "high"
  - parent_id/child_ids: For functions split into multiple units

Pay special attention to:
1. Functions marked as "inner" units - these are parts of larger functions that were split for easier translation
2. High complexity scores - may need extra care with loop vectorization or conditional handling
3. Dependencies - ensure you understand what external modules/types are being used

Generate the JAX translation following these requirements:

1. **Module Structure**:
   - Create a Python module with clear separation of concerns
   - Use NamedTuples for all data structures
   - Create a separate params file if needed
   - Follow the translation unit breakdown for organization

2. **Data Structures**:
   - Map Fortran derived types to Python NamedTuples
   - Use jnp.ndarray for all arrays
   - Document array shapes in comments: # [n_patches, n_layers]
   - Pay attention to types defined in dependencies

3. **Functions**:
   - Pure functions only (no mutations)
   - Full type hints: def func(arg: Type) -> ReturnType:
   - Google-style docstrings with Fortran reference (file + line numbers from translation units)
   - Preserve exact physics equations
   - For "inner" units, note the parent function in docstring

4. **JAX Patterns**:
   - Convert do loops to vectorized jnp operations
   - Convert if statements to jnp.where for JIT compatibility
   - Use index arrays for spatial hierarchy (not nested objects)
   - Apply vmap for vectorization where appropriate

5. **Documentation**:
   - Reference original Fortran file and exact line numbers from translation units
   - Explain any non-obvious translations
   - Add usage examples in docstrings
   - Note complexity considerations for high-complexity units

6. **Translation Unit Handling**:
   - If the module has split functions (has_split_functions=true), handle inner units carefully
   - Maintain logical flow even when functions are split
   - Consider refactoring split functions into helper functions

Please provide:
1. Main physics module (.py file)
2. Parameters file if needed (check module_info for parameter definitions)
3. Brief explanation of key translation decisions
4. Notes on handling any high-complexity or split units

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

