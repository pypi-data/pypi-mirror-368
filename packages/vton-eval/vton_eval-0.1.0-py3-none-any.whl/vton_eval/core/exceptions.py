class VTONException(Exception):
    """Base exception for the VTON evaluation suite."""
    pass

class ConfigError(VTONException):
    """Exception for configuration errors."""
    pass

class ModelError(VTONException):
    """Exception for model loading or inference errors."""
    pass

class EvaluationError(VTONException):
    """Exception for errors during the evaluation process."""
    pass

class VLMError(VTONException):
    """Exception for errors related to Vision-Language Models."""
    pass
