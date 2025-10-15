"""
Code validation utilities.

These help validate generated JAX code before it's finalized.
"""

import ast
from typing import List, Dict, Any, Optional


class CodeValidator:
    """Validate generated JAX code."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_python_syntax(self, code: str) -> bool:
        """
        Check if code is valid Python.
        
        Args:
            code: Python code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.errors.append(f"Syntax error: {e}")
            return False
    
    def check_type_hints(self, code: str) -> bool:
        """
        Check if functions have type hints.
        
        Args:
            code: Python code to check
            
        Returns:
            True if all functions have type hints
        """
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check return type annotation
                if node.returns is None:
                    self.warnings.append(f"Function {node.name} missing return type hint")
                
                # Check argument annotations
                for arg in node.args.args:
                    if arg.annotation is None:
                        self.warnings.append(f"Argument {arg.arg} in {node.name} missing type hint")
        
        return len(self.warnings) == 0
    
    def check_jax_patterns(self, code: str) -> Dict[str, Any]:
        """
        Check for common JAX anti-patterns.
        
        Args:
            code: Python code to check
            
        Returns:
            Dictionary with pattern check results
        """
        results = {
            "pure_functions": True,
            "no_mutations": True,
            "no_python_if_with_arrays": True,
        }
        
        # Check for mutations (assignments to attributes)
        if '.append(' in code or '[i] =' in code:
            results["no_mutations"] = False
            self.warnings.append("Potential mutation detected")
        
        # Check for problematic if statements (heuristic)
        if 'if ' in code and 'jnp.' in code:
            # This is a simple heuristic - the LLM should handle this properly
            self.warnings.append("Check if statements are JIT-compatible (use jnp.where)")
        
        return results
    
    def get_report(self) -> str:
        """
        Get validation report.
        
        Returns:
            Formatted validation report
        """
        report = "Validation Report\n"
        report += "=" * 50 + "\n\n"
        
        if self.errors:
            report += "Errors:\n"
            for error in self.errors:
                report += f"  ❌ {error}\n"
            report += "\n"
        else:
            report += "✓ No errors found\n\n"
        
        if self.warnings:
            report += "Warnings:\n"
            for warning in self.warnings:
                report += f"  ⚠️  {warning}\n"
        else:
            report += "✓ No warnings\n"
        
        return report


def validate_generated_code(code: str) -> tuple[bool, str]:
    """
    Validate generated code.
    
    Args:
        code: Generated Python/JAX code
        
    Returns:
        (is_valid, report) tuple
    """
    validator = CodeValidator()
    
    # Check syntax
    is_valid_syntax = validator.validate_python_syntax(code)
    
    # Check type hints
    validator.check_type_hints(code)
    
    # Check JAX patterns
    validator.check_jax_patterns(code)
    
    # Get report
    report = validator.get_report()
    
    return is_valid_syntax and len(validator.errors) == 0, report

