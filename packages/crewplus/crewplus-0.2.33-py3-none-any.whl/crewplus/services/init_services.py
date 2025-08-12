import os
from .model_load_balancer import ModelLoadBalancer

model_balancer = None

def init_load_balancer(config_path: str = None):
    """
    Initializes the global ModelLoadBalancer instance.

    This function is idempotent. If the balancer is already initialized,
    it does nothing. It follows a safe initialization pattern where the
    global instance is only assigned after successful configuration loading.
    """
    global model_balancer
    if model_balancer is None:
        # Use parameter if provided, otherwise check env var, then default
        final_config_path = config_path or os.getenv(
            "MODEL_CONFIG_PATH", 
            "config/models_config.json"
        )
        try:
            # 1. Create a local instance first.
            balancer = ModelLoadBalancer(final_config_path)
            # 2. Attempt to load its configuration.
            balancer.load_config()
            # 3. Only assign to the global variable on full success.
            model_balancer = balancer
        except Exception as e:
            # If any step fails, the global model_balancer remains None,
            # allowing for another initialization attempt later.
            # Re-raise the exception to notify the caller of the failure.
            raise RuntimeError(f"Failed to initialize and configure ModelLoadBalancer from {final_config_path}: {e}") from e

def get_model_balancer() -> ModelLoadBalancer:
    if model_balancer is None:
        raise RuntimeError("ModelLoadBalancer not initialized. Please call init_load_balancer() first.")
    return model_balancer
