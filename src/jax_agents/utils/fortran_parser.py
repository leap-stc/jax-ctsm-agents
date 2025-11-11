"""
Simple utilities for parsing Fortran code.

Note: These are basic helpers. The main analysis is done by the LLM agents.
"""

import re
from typing import List, Dict, Any


class FortranParser:
    """Basic Fortran parser for extracting structure."""
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def extract_subroutines(self, fortran_code: str) -> List[Dict[str, Any]]:
        """Extract subroutines from code."""
        return extract_subroutines(fortran_code)
    
    def extract_types(self, fortran_code: str) -> List[Dict[str, Any]]:
        """Extract type definitions from code."""
        return extract_types(fortran_code)


def extract_subroutines(fortran_code: str) -> List[Dict[str, Any]]:
    """
    Extract subroutine names and signatures from Fortran code.
    
    This is a simple regex-based extractor. The LLM does deeper analysis.
    
    Args:
        fortran_code: Fortran source code
        
    Returns:
        List of dictionaries with subroutine info
    """
    subroutines = []
    
    # Match subroutine declarations
    pattern = r'subroutine\s+(\w+)\s*\((.*?)\)'
    matches = re.finditer(pattern, fortran_code, re.IGNORECASE | re.MULTILINE)
    
    for match in matches:
        name = match.group(1)
        args = match.group(2)
        
        subroutines.append({
            "name": name,
            "arguments": [arg.strip() for arg in args.split(',') if arg.strip()],
        })
    
    return subroutines


def extract_types(fortran_code: str) -> List[Dict[str, Any]]:
    """
    Extract derived type definitions from Fortran code.
    
    Args:
        fortran_code: Fortran source code
        
    Returns:
        List of dictionaries with type info
    """
    types = []
    
    # Match type declarations
    pattern = r'type\s*::\s*(\w+)'
    matches = re.finditer(pattern, fortran_code, re.IGNORECASE)
    
    for match in matches:
        name = match.group(1)
        types.append({
            "name": name,
        })
    
    return types


def extract_use_statements(fortran_code: str) -> List[str]:
    """
    Extract module dependencies from 'use' statements.
    
    Args:
        fortran_code: Fortran source code
        
    Returns:
        List of module names
    """
    modules = []
    
    pattern = r'use\s+(\w+)'
    matches = re.finditer(pattern, fortran_code, re.IGNORECASE)
    
    for match in matches:
        module_name = match.group(1)
        if module_name not in modules:
            modules.append(module_name)
    
    return modules


def extract_parameters(fortran_code: str) -> List[Dict[str, Any]]:
    """
    Extract parameter definitions from Fortran code.
    
    Args:
        fortran_code: Fortran source code
        
    Returns:
        List of dictionaries with parameter info
    """
    parameters = []
    
    # Match parameter declarations
    # Example: real(r8), parameter :: br = 2.525e-6_r8
    pattern = r'parameter\s*::\s*(\w+)\s*=\s*([^\n!]+)'
    matches = re.finditer(pattern, fortran_code, re.IGNORECASE)
    
    for match in matches:
        name = match.group(1)
        value = match.group(2).strip()
        
        parameters.append({
            "name": name,
            "value": value,
        })
    
    return parameters

