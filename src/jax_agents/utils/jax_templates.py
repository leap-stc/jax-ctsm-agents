"""
JAX code templates for common patterns.

These templates help maintain consistency across translated modules.
"""


def get_namedtuple_template(
    name: str,
    fields: list,
    docstring: str = "",
) -> str:
    """
    Generate NamedTuple template.
    
    Args:
        name: Class name
        fields: List of (field_name, field_type, description) tuples
        docstring: Class docstring
        
    Returns:
        Python code for NamedTuple
    """
    code = f'''from typing import NamedTuple
import jax.numpy as jnp


class {name}(NamedTuple):
    """{docstring}"""
'''
    
    for field_name, field_type, description in fields:
        code += f'    {field_name}: {field_type}  # {description}\n'
    
    return code


def get_function_template(
    name: str,
    args: list,
    return_type: str,
    docstring: str,
    body: str = "    pass",
) -> str:
    """
    Generate function template with full type hints.
    
    Args:
        name: Function name
        args: List of (arg_name, arg_type, description) tuples
        return_type: Return type annotation
        docstring: Function docstring
        body: Function body
        
    Returns:
        Python function code
    """
    # Build argument list
    arg_strs = []
    for arg_name, arg_type, _ in args:
        arg_strs.append(f'{arg_name}: {arg_type}')
    
    args_joined = ',\n    '.join(arg_strs)
    
    # Build docstring Args section
    args_docs = []
    for arg_name, _, description in args:
        args_docs.append(f'        {arg_name}: {description}')
    
    args_docs_joined = '\n'.join(args_docs)
    
    code = f'''def {name}(
    {args_joined},
) -> {return_type}:
    """{docstring}
    
    Args:
{args_docs_joined}
        
    Returns:
        [Description of return value]
    """
{body}
'''
    
    return code


def get_params_class_template(
    name: str,
    parameters: list,
    docstring: str = "",
) -> str:
    """
    Generate parameter class template.
    
    Args:
        name: Parameter class name
        parameters: List of (param_name, param_type, default_value, description) tuples
        docstring: Class docstring
        
    Returns:
        Python code for parameter NamedTuple
    """
    code = f'''from typing import NamedTuple
import jax.numpy as jnp


class {name}(NamedTuple):
    """{docstring}"""
'''
    
    for param_name, param_type, default_value, description in parameters:
        code += f'    {param_name}: {param_type} = {default_value}  # {description}\n'
    
    # Add helper methods section
    code += '''
    
    # Helper methods can be added here
    # def get_temp_correction(self, temperature: jnp.ndarray) -> jnp.ndarray:
    #     """Calculate temperature correction factor."""
    #     return self.q10 ** ((temperature - 273.15 - 20.0) / 10.0)
'''
    
    return code


# Example JAX patterns
JAX_PATTERNS = {
    "pure_function": '''def physics_calculation(
    state: StateType,
    params: ParamsType,
) -> FluxType:
    """Pure function - no side effects, no mutations."""
    # Calculations here
    flux = state.nitrogen * params.rate
    return FluxType(flux=flux)
''',
    
    "vectorized_loop": '''# Instead of:
# for i in range(n):
#     result[i] = array1[i] * array2[i]

# Use:
result = array1 * array2
''',
    
    "conditional": '''# Instead of:
# if is_woody:
#     mr = calculate_stem_mr(...)

# Use:
mr = jnp.where(is_woody, calculate_stem_mr(...), 0.0)
''',
    
    "immutable_update": '''# Instead of:
# state.carbon.leafc = new_leafc  # Mutation!

# Use:
new_carbon = state.carbon._replace(leafc=new_leafc)
new_state = state._replace(carbon=new_carbon)
''',
}

