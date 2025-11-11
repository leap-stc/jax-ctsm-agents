"""
Output comparison utilities for validating translations.

Provides functions to compare Fortran and Python outputs with:
- Tolerance-based comparison
- Multiple error metrics (absolute, relative, max, RMS)
- Detailed difference reporting
- Array shape validation
"""

import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


def compare_outputs(
    fortran_outputs: Dict[str, Any],
    python_outputs: Dict[str, Any],
    tolerance: float = 1e-6,
    relative_tolerance: float = 1e-6,
) -> Dict[str, Any]:
    """
    Compare Fortran and Python outputs.
    
    Performs comprehensive comparison including:
    - Value comparison with absolute and relative tolerances
    - Shape validation for arrays
    - Multiple error metrics
    - Detailed reporting of differences
    
    Args:
        fortran_outputs: Dictionary of Fortran output variables
        python_outputs: Dictionary of Python output variables
        tolerance: Absolute tolerance for comparison
        relative_tolerance: Relative tolerance for comparison
        
    Returns:
        Dictionary containing:
        - all_close: bool - Whether all outputs match within tolerance
        - differences: Dict of per-variable differences
        - error_metrics: Dict of error metrics
        - mismatched_keys: List of variables that don't match
    """
    result = {
        "all_close": True,
        "differences": {},
        "error_metrics": {},
        "mismatched_keys": [],
        "shape_mismatches": [],
        "missing_in_fortran": [],
        "missing_in_python": [],
    }
    
    # Check for missing variables
    fortran_keys = set(fortran_outputs.keys())
    python_keys = set(python_outputs.keys())
    
    result["missing_in_fortran"] = list(python_keys - fortran_keys)
    result["missing_in_python"] = list(fortran_keys - python_keys)
    
    if result["missing_in_fortran"] or result["missing_in_python"]:
        result["all_close"] = False
        logger.warning(
            f"Key mismatch - Missing in Fortran: {result['missing_in_fortran']}, "
            f"Missing in Python: {result['missing_in_python']}"
        )
    
    # Compare common variables
    common_keys = fortran_keys & python_keys
    
    for key in common_keys:
        fortran_val = fortran_outputs[key]
        python_val = python_outputs[key]
        
        # Convert to numpy arrays
        try:
            f_array = np.asarray(fortran_val)
            p_array = np.asarray(python_val)
        except Exception as e:
            logger.error(f"Failed to convert {key} to array: {e}")
            result["all_close"] = False
            result["mismatched_keys"].append(key)
            continue
        
        # Check shapes
        if f_array.shape != p_array.shape:
            result["all_close"] = False
            result["shape_mismatches"].append({
                "variable": key,
                "fortran_shape": f_array.shape,
                "python_shape": p_array.shape,
            })
            logger.warning(
                f"Shape mismatch for {key}: "
                f"Fortran {f_array.shape} vs Python {p_array.shape}"
            )
            continue
        
        # Compare values
        comparison = compare_arrays(
            f_array, p_array, tolerance, relative_tolerance
        )
        
        result["differences"][key] = comparison
        result["error_metrics"][key] = comparison["metrics"]
        
        if not comparison["all_close"]:
            result["all_close"] = False
            result["mismatched_keys"].append(key)
            logger.info(
                f"Mismatch in {key}: max_abs_error={comparison['metrics']['max_abs_error']:.2e}, "
                f"max_rel_error={comparison['metrics']['max_rel_error']:.2e}"
            )
    
    return result


def compare_arrays(
    fortran_array: np.ndarray,
    python_array: np.ndarray,
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
) -> Dict[str, Any]:
    """
    Compare two arrays with comprehensive error metrics.
    
    Args:
        fortran_array: Fortran output array
        python_array: Python output array
        abs_tol: Absolute tolerance
        rel_tol: Relative tolerance
        
    Returns:
        Dictionary with comparison results and metrics
    """
    # Handle NaN and Inf
    fortran_finite = np.isfinite(fortran_array)
    python_finite = np.isfinite(python_array)
    
    if not np.array_equal(fortran_finite, python_finite):
        return {
            "all_close": False,
            "nan_inf_mismatch": True,
            "metrics": {
                "fortran_nans": np.sum(~fortran_finite),
                "python_nans": np.sum(~python_finite),
            }
        }
    
    # Compare only finite values
    finite_mask = fortran_finite & python_finite
    
    if not np.any(finite_mask):
        # Both arrays are all NaN/Inf
        return {
            "all_close": True,
            "metrics": {
                "all_nan_inf": True,
            }
        }
    
    f_finite = fortran_array[finite_mask]
    p_finite = python_array[finite_mask]
    
    # Calculate error metrics
    abs_error = np.abs(f_finite - p_finite)
    max_abs_error = np.max(abs_error)
    mean_abs_error = np.mean(abs_error)
    rms_error = np.sqrt(np.mean(abs_error ** 2))
    
    # Relative error (avoid division by zero)
    denominator = np.maximum(np.abs(f_finite), np.abs(p_finite))
    rel_error = np.where(
        denominator > 0,
        abs_error / denominator,
        0.0
    )
    max_rel_error = np.max(rel_error)
    mean_rel_error = np.mean(rel_error)
    
    # Check if all close
    all_close = np.allclose(
        fortran_array, python_array,
        atol=abs_tol, rtol=rel_tol
    )
    
    metrics = {
        "max_abs_error": float(max_abs_error),
        "mean_abs_error": float(mean_abs_error),
        "rms_error": float(rms_error),
        "max_rel_error": float(max_rel_error),
        "mean_rel_error": float(mean_rel_error),
        "num_elements": int(np.prod(fortran_array.shape)),
        "num_mismatched": int(np.sum(abs_error > abs_tol)),
        "fortran_min": float(np.min(f_finite)),
        "fortran_max": float(np.max(f_finite)),
        "python_min": float(np.min(p_finite)),
        "python_max": float(np.max(p_finite)),
    }
    
    result = {
        "all_close": all_close,
        "metrics": metrics,
        "nan_inf_mismatch": False,
    }
    
    # Add location of maximum error for debugging
    if max_abs_error > abs_tol:
        max_error_idx = np.unravel_index(
            np.argmax(abs_error.ravel()),
            fortran_array[finite_mask].shape
        )
        result["max_error_location"] = {
            "index": max_error_idx,
            "fortran_value": float(f_finite[max_error_idx]),
            "python_value": float(p_finite[max_error_idx]),
        }
    
    return result


def generate_comparison_summary(
    comparison: Dict[str, Any],
    verbose: bool = False,
) -> str:
    """
    Generate human-readable summary of comparison results.
    
    Args:
        comparison: Comparison result from compare_outputs
        verbose: Include detailed metrics
        
    Returns:
        Formatted summary string
    """
    lines = []
    
    if comparison["all_close"]:
        lines.append("✓ All outputs match within tolerance")
    else:
        lines.append("✗ Outputs do not match")
    
    lines.append("")
    
    # Summary statistics
    if comparison["mismatched_keys"]:
        lines.append(f"Mismatched variables ({len(comparison['mismatched_keys'])}):")
        for key in comparison["mismatched_keys"]:
            if key in comparison["error_metrics"]:
                metrics = comparison["error_metrics"][key]
                lines.append(
                    f"  - {key}: "
                    f"max_abs={metrics['max_abs_error']:.2e}, "
                    f"max_rel={metrics['max_rel_error']:.2e}"
                )
    
    if comparison["shape_mismatches"]:
        lines.append("")
        lines.append(f"Shape mismatches ({len(comparison['shape_mismatches'])}):")
        for mismatch in comparison["shape_mismatches"]:
            lines.append(
                f"  - {mismatch['variable']}: "
                f"Fortran {mismatch['fortran_shape']} vs "
                f"Python {mismatch['python_shape']}"
            )
    
    if comparison["missing_in_fortran"]:
        lines.append("")
        lines.append("Missing in Fortran:")
        for key in comparison["missing_in_fortran"]:
            lines.append(f"  - {key}")
    
    if comparison["missing_in_python"]:
        lines.append("")
        lines.append("Missing in Python:")
        for key in comparison["missing_in_python"]:
            lines.append(f"  - {key}")
    
    # Verbose metrics
    if verbose and comparison["error_metrics"]:
        lines.append("")
        lines.append("Detailed Metrics:")
        for key, metrics in comparison["error_metrics"].items():
            lines.append(f"\n  {key}:")
            for metric_name, value in metrics.items():
                if isinstance(value, float):
                    lines.append(f"    {metric_name}: {value:.6e}")
                else:
                    lines.append(f"    {metric_name}: {value}")
    
    return "\n".join(lines)


def compare_scalar(
    fortran_val: float,
    python_val: float,
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
) -> Tuple[bool, float, float]:
    """
    Compare two scalar values.
    
    Args:
        fortran_val: Fortran scalar value
        python_val: Python scalar value
        abs_tol: Absolute tolerance
        rel_tol: Relative tolerance
        
    Returns:
        Tuple of (matches, abs_error, rel_error)
    """
    abs_error = abs(fortran_val - python_val)
    
    # Relative error
    denominator = max(abs(fortran_val), abs(python_val))
    if denominator > 0:
        rel_error = abs_error / denominator
    else:
        rel_error = 0.0
    
    # Check tolerance
    matches = (abs_error <= abs_tol) or (rel_error <= rel_tol)
    
    return matches, abs_error, rel_error


def compare_execution_times(
    fortran_times: List[float],
    python_times: List[float],
) -> Dict[str, Any]:
    """
    Compare execution times between implementations.
    
    Args:
        fortran_times: List of Fortran execution times
        python_times: List of Python execution times
        
    Returns:
        Dictionary with timing comparison statistics
    """
    fortran_array = np.array(fortran_times)
    python_array = np.array(python_times)
    
    speedup = fortran_array / python_array
    
    return {
        "fortran_mean": float(np.mean(fortran_array)),
        "fortran_std": float(np.std(fortran_array)),
        "python_mean": float(np.mean(python_array)),
        "python_std": float(np.std(python_array)),
        "speedup_mean": float(np.mean(speedup)),
        "speedup_std": float(np.std(speedup)),
        "speedup_min": float(np.min(speedup)),
        "speedup_max": float(np.max(speedup)),
        "python_faster": python_array < fortran_array,
    }

