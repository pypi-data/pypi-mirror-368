from typing import Dict, Any

class BaseModelWrapper:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None

    def load_model(self) -> None:
        raise NotImplementedError

    def unload_model(self) -> None:
        self.model = None

    def is_loaded(self) -> bool:
        return self.model is not None
