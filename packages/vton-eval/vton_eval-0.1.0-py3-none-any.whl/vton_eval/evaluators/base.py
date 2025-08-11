from typing import List, Dict
from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationTask
from vton_eval.vlm.base import VLMBackend
import numpy as np

class BaseEvaluator:
    def __init__(self, config: VTONConfig, vlm_backend: VLMBackend):
        self.config = config
        self.vlm_backend = vlm_backend

    def evaluate(self, task: EvaluationTask, generated_image: np.ndarray) -> Dict[str, float]:
        raise NotImplementedError

    def batch_evaluate(self, tasks: List[EvaluationTask], images: List[np.ndarray]) -> List[Dict]:
        return [self.evaluate(task, image) for task, image in zip(tasks, images)]

    def get_score_components(self) -> Dict[str, float]:
        raise NotImplementedError
