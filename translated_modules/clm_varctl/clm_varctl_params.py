"""
Configuration and run control for JAX-CTSM.

This package contains configuration management and run control utilities
translated from CTSM's Fortran modules.
"""

from jax_ctsm.config.run_control import (
    RunControlConfig,
    DEFAULT_CONFIG,
    create_run_config,
    log_message,
    get_config,
    set_config,
    iulog,
)

__all__ = [
    "RunControlConfig",
    "DEFAULT_CONFIG",
    "create_run_config",
    "log_message",
    "get_config",
    "set_config",
    "iulog",
]