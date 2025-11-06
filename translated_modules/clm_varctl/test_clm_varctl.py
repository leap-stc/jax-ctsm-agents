from jax_ctsm.config import create_run_config, log_message

# Create configuration
config = create_run_config(log_level="DEBUG", verbose=True)

# Use in functions
def my_function(config: RunControlConfig):
    log_message("Processing data", config, "INFO")
    # ... do work ...