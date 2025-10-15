"""Prompt templates for Static Analysis Agent."""

ANALYSIS_PROMPTS = {
    "system": """You are a Static Analysis Agent specializing in Fortran code analysis for CTSM.

Your primary responsibilities:
1. Analyze Fortran module structure and organization
2. Extract dependencies (use statements, includes)
3. Identify data types and derived types
4. Map subroutines and functions with their signatures
5. Detect loops, conditionals, and control flow patterns
6. Extract parameters, constants, and magic numbers
7. Identify spatial hierarchy patterns (patch, column, landunit, gridcell)
8. Map variable relationships and data flow

You provide detailed, structured analysis in JSON format that will be used by the Translator Agent.""",

    "analyze_module": """Analyze the following Fortran module from CTSM and provide a comprehensive structural analysis.

FORTRAN MODULE:
```fortran
{fortran_code}
```

Please provide a detailed JSON analysis with the following structure:

{{
  "module_name": "string",
  "description": "string - what this module does",
  "dependencies": {{
    "modules": ["list of modules used"],
    "includes": ["list of include files"],
    "external_types": ["derived types from other modules"]
  }},
  "data_types": [
    {{
      "name": "type name",
      "kind": "derived_type|parameter_type|variable",
      "fields": [
        {{
          "name": "field name",
          "type": "Fortran type",
          "description": "what this field represents"
        }}
      ]
    }}
  ],
  "parameters": [
    {{
      "name": "parameter name",
      "value": "parameter value",
      "type": "Fortran type",
      "description": "what this parameter represents"
    }}
  ],
  "subroutines": [
    {{
      "name": "subroutine name",
      "purpose": "what it does",
      "inputs": [
        {{
          "name": "argument name",
          "type": "type",
          "intent": "in|out|inout",
          "description": "description"
        }}
      ],
      "outputs": ["list of output variables"],
      "key_operations": ["list of main operations"],
      "loops": [
        {{
          "type": "spatial|vertical|temporal",
          "variable": "loop variable",
          "range": "loop range"
        }}
      ],
      "fortran_patterns": {{
        "filters": ["filter patterns used"],
        "conditionals": ["key if statements"],
        "calculations": ["main physics calculations"]
      }}
    }}
  ],
  "spatial_hierarchy": {{
    "levels_used": ["patch", "column", "landunit", "gridcell"],
    "iteration_patterns": ["how code iterates over spatial levels"],
    "aggregation_patterns": ["how data is aggregated across levels"]
  }},
  "jax_translation_notes": {{
    "challenges": ["list of translation challenges"],
    "suggested_approach": ["suggested approach for each challenge"],
    "data_structure_mapping": {{
      "fortran_type": "suggested JAX equivalent"
    }}
  }}
}}

Be thorough and precise. This analysis will guide the translation to JAX.""",

    "extract_dependencies": """Extract all dependencies from the following Fortran module:

```fortran
{fortran_code}
```

List all:
1. Module dependencies (use statements)
2. Include files
3. External type dependencies
4. Parameter dependencies

Provide the result as a structured JSON object.""",

    "identify_physics": """Analyze the physics calculations in this Fortran code:

```fortran
{fortran_code}
```

For each physics calculation:
1. Identify the scientific formula
2. Extract the equation in mathematical notation
3. List all variables and their physical meanings
4. Identify units for each variable
5. Note any temperature dependencies, Q10 responses, or other key patterns
6. Reference any comments that cite scientific papers

This analysis will ensure we preserve the exact physics in the JAX translation.""",

    "analyze_loops": """Analyze all loop structures in this Fortran code:

```fortran
{fortran_code}
```

For each loop:
1. Identify the loop type (spatial iteration, vertical levels, etc.)
2. Determine if it can be vectorized
3. Identify data dependencies between iterations
4. Suggest JAX equivalent (vmap, direct vectorization, etc.)

Provide analysis as JSON.""",
}

