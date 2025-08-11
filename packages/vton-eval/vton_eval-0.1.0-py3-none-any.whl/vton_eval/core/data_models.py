from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EvaluationTask:
    human_image: str
    garment_image: str
    measurements: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class EvaluationResult:
    task_id: str
    garment_score: float
    identity_score: float
    body_score: float
    fit_score: float
    overall_score: float
    metadata: Dict[str, Any]
