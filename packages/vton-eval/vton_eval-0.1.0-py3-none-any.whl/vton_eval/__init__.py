"""VTON Evaluation Suite - A comprehensive framework for evaluating Virtual Try-On models."""

from vton_eval.__version__ import __version__
from vton_eval.core.config import (
    EvaluatorConfig,
    GarmentPreservationConfig,
    IdentityPreservationConfig,
    BodyShapeConfig,
    FitMeasurementConfig,
    PipelineConfig,
)
from vton_eval.core.data_models import (
    VTONSample,
    EvaluationResult,
    GarmentPreservationResult,
    IdentityPreservationResult,
    BodyShapeResult,
    FitMeasurementResult,
)
from vton_eval.evaluators import (
    GarmentPreservationEvaluator,
    IdentityPreservationEvaluator,
    BodyShapeEvaluator,
    FitMeasurementEvaluator,
)
from vton_eval.pipeline import VTONEvaluationPipeline

__all__ = [
    "__version__",
    # Config classes
    "EvaluatorConfig",
    "GarmentPreservationConfig",
    "IdentityPreservationConfig",
    "BodyShapeConfig",
    "FitMeasurementConfig",
    "PipelineConfig",
    # Data models
    "VTONSample",
    "EvaluationResult",
    "GarmentPreservationResult",
    "IdentityPreservationResult",
    "BodyShapeResult",
    "FitMeasurementResult",
    # Evaluators
    "GarmentPreservationEvaluator",
    "IdentityPreservationEvaluator",
    "BodyShapeEvaluator",
    "FitMeasurementEvaluator",
    # Pipeline
    "VTONEvaluationPipeline",
]