from typing import Optional, Dict, Any
import yaml

class VTONConfig:
    def __init__(self, config_path: Optional[str] = None):
        self.config = {}
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, path: str):
        with open(path, 'r') as f:
            self.config = yaml.safe_load(f)

    def validate(self) -> bool:
        # Basic validation, can be expanded
        required_keys = ['vlm', 'models', 'scoring', 'evaluation']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config section: {key}")
        return True

    def get_vlm_config(self) -> Dict:
        return self.config.get('vlm', {})

    def get_model_paths(self) -> Dict:
        return self.config.get('models', {})

    def get_scoring_weights(self) -> Dict:
        return self.config.get('scoring', {}).get('weights', {})

    def get_production_thresholds(self) -> float:
        return self.config.get('scoring', {}).get('production_threshold', 0.8)
