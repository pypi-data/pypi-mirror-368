from typing import List, Dict, Any
import numpy as np

class VLMBackend:
    def __init__(self, backend_type: str, config: Dict[str, Any]):
        self.backend_type = backend_type
        self.config = config

    def query(self, prompt: str, images: List[np.ndarray], **kwargs) -> str:
        raise NotImplementedError

    def batch_query(self, queries: List[Dict[str, Any]]) -> List[str]:
        raise NotImplementedError

    def get_confidence_score(self, response: str) -> float:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError
