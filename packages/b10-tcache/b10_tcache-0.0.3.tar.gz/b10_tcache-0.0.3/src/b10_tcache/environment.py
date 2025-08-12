# Not sure if these libraries should be nestled inside the code.

import hashlib
import logging
import os
import platform

logger = logging.getLogger(__name__)


# FIXME(SR): I wonder if there's a race here if the environment info is trying to be extracted while we're importing torch/triton.


def get_environment_key() -> str:
    """Generate unique key based on torch/triton/gpu configuration."""
    try:
        import torch

        components = []

        # PyTorch version
        torch_version = torch.__version__.split("+")[0]
        components.append(f"torch-{torch_version}")

        # CUDA/GPU info
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda or "unknown"
            components.append(f"cuda-{cuda_version}")

            try:
                gpu_capability = torch.cuda.get_device_capability(0)
                components.append(f"cc-{gpu_capability[0]}.{gpu_capability[1]}")
            except Exception:
                components.append("gpu-unknown")
        else:
            components.append("cpu")

        # Triton version
        try:
            import triton

            triton_version = triton.__version__.split("+")[0]
            components.append(f"triton-{triton_version}")
        except ImportError:
            components.append("triton-none")

        # Create hash
        env_string = "_".join(components)
        env_hash = hashlib.sha256(env_string.encode()).hexdigest()[:12]

        return env_hash

    except Exception as e:
        logger.debug(f"Environment key generation failed: {e}")
        # Use deterministic fallback based on stable system properties
        fallback = f"fallback-{platform.machine()}-{platform.python_version()}-{platform.system()}"
        return hashlib.sha256(fallback.encode()).hexdigest()[:12]


def get_cache_filename() -> str:
    """Get cache filename for current environment."""
    env_key = get_environment_key()
    return f"cache_{env_key}"


def get_hostname() -> str:
    """Get hostname for current machine."""
    hostname = os.uname().nodename or os.getenv("HOSTNAME", "unknown-host")
    return hostname
