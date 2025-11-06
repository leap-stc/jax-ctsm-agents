"""
Run Control Variables and Configuration.

Translated from CTSM's clm_varctl.F90 (lines 1-15)

This module contains run-time control variables and configuration settings
for the CLM model. In the original Fortran, this was a simple module with
module-level variables. In JAX, we use immutable configuration objects and
constants.

The original Fortran module used module-level mutable state for configuration.
In JAX, we follow functional programming principles and pass configuration
explicitly through function calls.
"""

from typing import NamedTuple, Optional
import sys
from pathlib import Path


# Constants
DEFAULT_LOG_UNIT = 6  # Fortran "stdout" equivalent


class RunControlConfig(NamedTuple):
    """Run control configuration for CLM.
    
    This replaces the module-level variables from clm_varctl.F90.
    All configuration is immutable and passed explicitly.
    
    Attributes:
        log_file: Path to log file, or None for stdout
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        verbose: Whether to enable verbose output
        
    Example:
        >>> config = RunControlConfig()
        >>> config = config._replace(log_level="DEBUG")
    """
    log_file: Optional[Path] = None
    log_level: str = "INFO"
    verbose: bool = False
    
    def get_log_handle(self):
        """Get file handle for logging.
        
        Returns:
            File handle for logging output. Returns sys.stdout if no
            log file is specified (equivalent to Fortran unit 6).
            
        Note:
            In Fortran, iulog=6 corresponds to stdout. We maintain this
            behavior by defaulting to sys.stdout.
        """
        if self.log_file is None:
            return sys.stdout
        return open(self.log_file, 'a')


# Default configuration instance
DEFAULT_CONFIG = RunControlConfig()


def create_run_config(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    verbose: bool = False,
) -> RunControlConfig:
    """Create a run control configuration.
    
    This is a convenience factory function for creating RunControlConfig
    instances with validation.
    
    Args:
        log_file: Path to log file, or None for stdout
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        verbose: Whether to enable verbose output
        
    Returns:
        Immutable RunControlConfig instance
        
    Raises:
        ValueError: If log_level is not valid
        
    Example:
        >>> config = create_run_config(log_level="DEBUG", verbose=True)
        >>> print(config.log_level)
        DEBUG
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
    if log_level not in valid_levels:
        raise ValueError(
            f"Invalid log_level '{log_level}'. Must be one of {valid_levels}"
        )
    
    log_path = Path(log_file) if log_file is not None else None
    
    return RunControlConfig(
        log_file=log_path,
        log_level=log_level,
        verbose=verbose,
    )


def log_message(
    message: str,
    config: RunControlConfig = DEFAULT_CONFIG,
    level: str = "INFO",
) -> None:
    """Log a message using the run control configuration.
    
    This provides a simple logging interface that respects the configuration.
    For production use, consider integrating with Python's logging module.
    
    Args:
        message: Message to log
        config: Run control configuration
        level: Message level (DEBUG, INFO, WARNING, ERROR)
        
    Example:
        >>> config = create_run_config(verbose=True)
        >>> log_message("Starting simulation", config, "INFO")
        [INFO] Starting simulation
    """
    level_priority = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
    config_priority = level_priority.get(config.log_level, 1)
    message_priority = level_priority.get(level, 1)
    
    if message_priority >= config_priority:
        handle = config.get_log_handle()
        print(f"[{level}] {message}", file=handle)
        if config.log_file is not None:
            handle.close()


# Compatibility layer for modules expecting module-level variables
class _RunControlState:
    """Internal state holder for backward compatibility.
    
    This class provides a compatibility layer for code that expects
    module-level mutable state (like the original Fortran). However,
    new code should use RunControlConfig directly.
    
    Note:
        This is not thread-safe and should only be used during the
        transition period. Prefer passing RunControlConfig explicitly.
    """
    def __init__(self):
        self._config = DEFAULT_CONFIG
    
    @property
    def config(self) -> RunControlConfig:
        """Get current configuration."""
        return self._config
    
    @config.setter
    def config(self, value: RunControlConfig) -> None:
        """Set current configuration."""
        if not isinstance(value, RunControlConfig):
            raise TypeError("config must be a RunControlConfig instance")
        self._config = value
    
    @property
    def iulog(self) -> int:
        """Get log unit number (for Fortran compatibility).
        
        Returns:
            Always returns 6 (stdout equivalent) for compatibility.
            Actual logging should use the config object.
        """
        return DEFAULT_LOG_UNIT


# Global state instance (for backward compatibility only)
_state = _RunControlState()


def get_config() -> RunControlConfig:
    """Get the current global configuration.
    
    Returns:
        Current RunControlConfig instance
        
    Note:
        This is provided for backward compatibility. New code should
        pass configuration explicitly rather than using global state.
    """
    return _state.config


def set_config(config: RunControlConfig) -> None:
    """Set the global configuration.
    
    Args:
        config: New configuration to use
        
    Note:
        This is provided for backward compatibility. New code should
        pass configuration explicitly rather than using global state.
    """
    _state.config = config


# For modules that import iulog directly
iulog = DEFAULT_LOG_UNIT