"""Prompt templates for Orchestrator Agent."""

ORCHESTRATOR_PROMPTS = {
    "system": """You are an Orchestrator Agent coordinating the conversion of Fortran CTSM modules to JAX.

Your primary responsibilities:
1. Plan conversion strategies for Fortran modules
2. Coordinate between Static Analysis and Translator agents
3. Manage dependencies between modules
4. Track conversion progress
5. Ensure consistency across converted modules
6. Generate comprehensive reports
7. Make high-level architectural decisions

You take a systematic, strategic approach to module conversion, ensuring each module is properly analyzed before translation and that the resulting JAX code follows established patterns.""",

    "plan_conversion": """Plan the conversion strategy for the following Fortran module:

MODULE TO CONVERT: {module_name}
MODULE PATH: {module_path}

EXISTING JAX-CTSM MODULES:
{existing_modules}

Please provide a conversion plan with:

1. **Conversion Strategy**:
   - Estimated complexity (simple/medium/complex)
   - Key challenges
   - Suggested approach
   - Dependencies to handle first

2. **Analysis Requirements**:
   - What the Static Analysis agent should focus on
   - Specific patterns to look for
   - Known CTSM patterns in this module type

3. **Translation Requirements**:
   - Target JAX structure
   - Required data structures
   - Parameter handling approach
   - Testing strategy

4. **Integration Plan**:
   - How this fits with existing jax-ctsm modules
   - Required updates to existing code
   - New dependencies to add

Provide as structured JSON.""",

    "synthesize_results": """Synthesize the results from analysis and translation:

STATIC ANALYSIS RESULTS:
```json
{analysis_results}
```

TRANSLATOR OUTPUT:
```python
{translation_output}
```

Please provide:

1. **Quality Assessment**:
   - Does translation match analysis?
   - Are all Fortran features translated?
   - Any missing pieces?

2. **Consistency Check**:
   - Follows jax-ctsm patterns?
   - Proper type hints and docstrings?
   - JIT-compatible code?

3. **Recommendations**:
   - Suggested improvements
   - Validation tests needed
   - Integration considerations

4. **Next Steps**:
   - What to do next
   - Dependencies to handle
   - Testing priorities

Provide as structured report.""",

    "manage_dependencies": """Analyze module dependencies for conversion planning:

TARGET MODULE: {target_module}

MODULE DEPENDENCIES (from static analysis):
{dependencies}

ALREADY CONVERTED MODULES:
{converted_modules}

Provide a dependency resolution plan:

1. **Conversion Order**:
   - Which modules to convert first
   - Why this order is optimal

2. **Missing Dependencies**:
   - What's not yet converted
   - Impact on current conversion

3. **Workarounds**:
   - How to handle unconverted dependencies
   - Stub implementations if needed

4. **Timeline Estimate**:
   - Time to convert dependencies
   - Time to convert target module

Provide as structured JSON.""",

    "generate_report": """Generate a comprehensive conversion report:

MODULE: {module_name}
STATUS: {status}

ANALYSIS SUMMARY:
{analysis_summary}

TRANSLATION SUMMARY:
{translation_summary}

COSTS:
{cost_summary}

Generate a detailed markdown report including:

1. **Executive Summary**
   - What was converted
   - Success/challenges
   - Key metrics

2. **Technical Details**
   - Analysis findings
   - Translation approach
   - JAX patterns used

3. **Code Quality**
   - Type coverage
   - Documentation completeness
   - JIT/vmap compatibility

4. **Testing Recommendations**
   - Unit tests needed
   - Validation tests needed
   - Integration tests needed

5. **Next Steps**
   - Follow-up work
   - Dependencies to handle
   - Optimization opportunities

6. **Costs**
   - Token usage
   - API costs
   - Time spent

Provide as formatted markdown.""",
}

