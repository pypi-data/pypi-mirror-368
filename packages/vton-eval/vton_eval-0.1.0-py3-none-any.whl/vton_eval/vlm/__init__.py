"""Vision-Language Model backends for VTON evaluation."""

from typing import Dict, Any, Optional
import logging
import os

from vton_eval.vlm.base import VLMBackend
from vton_eval.vlm.gemini import GeminiBackend

logger = logging.getLogger(__name__)

# Registry of available VLM backends
VLM_BACKENDS = {
    'gemini': GeminiBackend,
}


def create_vlm_backend(backend_type: str, config: Dict[str, Any]) -> Optional[VLMBackend]:
    """Factory function to create VLM backend instances.
    
    Args:
        backend_type: Type of backend ('gemini', 'gpt4o', 'llava')
        config: Configuration dictionary with backend-specific settings
        
    Returns:
        VLMBackend instance or None if creation fails
    """
    if backend_type not in VLM_BACKENDS:
        logger.error(f"Unknown VLM backend type: {backend_type}")
        return None
    
    try:
        # Get API key from config or environment
        api_key = config.get('api_key')
        if not api_key:
            # Try environment variables
            env_vars = {
                'gemini': 'GEMINI_API_KEY',
            }
            if backend_type in env_vars:
                api_key = os.getenv(env_vars[backend_type])
        
        if not api_key:
            logger.error(f"No API key provided for {backend_type} backend")
            return None
        
        # Create backend instance
        backend_class = VLM_BACKENDS[backend_type]
        backend = backend_class(api_key, config)
        
        logger.info(f"Created {backend_type} VLM backend")
        return backend
        
    except Exception as e:
        logger.error(f"Failed to create {backend_type} backend: {e}")
        return None


def get_available_backends() -> list:
    """Get list of available VLM backend types."""
    return list(VLM_BACKENDS.keys())


__all__ = [
    'VLMBackend',
    'GeminiBackend',
    'create_vlm_backend',
    'get_available_backends',
]