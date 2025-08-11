from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationTask, EvaluationResult
from vton_eval.pipeline.scorer import VTONScorer
from vton_eval.pipeline.reporter import VTONReporter
from vton_eval.vlm import create_vlm_backend
from vton_eval.evaluators.garment_preservation import GarmentPreservationEvaluator
from vton_eval.evaluators.identity_preservation import IdentityPreservationEvaluator
from vton_eval.evaluators.body_shape import BodyShapeEvaluator
from vton_eval.evaluators.fit_measurement import FitMeasurementEvaluator
from typing import List, Dict, Any, Optional
import numpy as np
import logging
import cv2
import os
import json
from pathlib import Path
from tqdm import tqdm
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)


class VTONEvaluationPipeline:
    """
    Main orchestrator for VTON evaluation pipeline.
    Coordinates all evaluators and manages the evaluation flow.
    """
    
    def __init__(self, config: VTONConfig):
        self.config = config
        self.vlm_backend = self._initialize_vlm_backend()
        self.evaluators = self._initialize_evaluators()
        self.scorer = VTONScorer(config)
        self.reporter = VTONReporter(config)
        self.batch_size = config.config.get('evaluation', {}).get('batch_size', 32)
        self.checkpoint_interval = config.config.get('evaluation', {}).get('checkpoint_interval', 100)
        self.current_checkpoint = None
        
        logger.info("Initialized VTON Evaluation Pipeline")
    
    def _initialize_evaluators(self) -> Dict[str, Any]:
        """Initialize all evaluators with config and VLM backend."""
        evaluators = {}
        
        try:
            # Initialize each evaluator if enabled in config
            evaluator_config = self.config.config.get('evaluation', {}).get('evaluators', {})
            
            if evaluator_config.get('garment_preservation', {}).get('enabled', True):
                evaluators['garment'] = GarmentPreservationEvaluator(self.config, self.vlm_backend)
                logger.info("Initialized Garment Preservation Evaluator")
            
            if evaluator_config.get('identity_preservation', {}).get('enabled', True):
                evaluators['identity'] = IdentityPreservationEvaluator(self.config, self.vlm_backend)
                logger.info("Initialized Identity Preservation Evaluator")
            
            if evaluator_config.get('body_shape', {}).get('enabled', True):
                evaluators['body'] = BodyShapeEvaluator(self.config, self.vlm_backend)
                logger.info("Initialized Body Shape Evaluator")
            
            if evaluator_config.get('fit_measurement', {}).get('enabled', True):
                evaluators['fit'] = FitMeasurementEvaluator(self.config, self.vlm_backend)
                logger.info("Initialized Fit Measurement Evaluator")
            
        except Exception as e:
            logger.error(f"Failed to initialize evaluators: {e}")
            raise
        
        return evaluators

    def _initialize_vlm_backend(self):
        """Initialize VLM backend from config."""
        vlm_config = self.config.get_vlm_config()
        backend_type = vlm_config.get('backend', 'gemini')
        
        vlm = create_vlm_backend(backend_type, vlm_config)
        if not vlm:
            logger.warning("Failed to initialize VLM backend, evaluators will run without VLM")
        else:
            logger.info(f"Initialized {backend_type} VLM backend")
        
        return vlm

    def evaluate_submission(self, submission_dir: str, output_path: str) -> Dict[str, Any]:
        """
        Evaluate a complete submission directory.
        
        Args:
            submission_dir: Directory containing generated images
            output_path: Path to save evaluation results
            
        Returns:
            Dictionary with evaluation results and statistics
        """
        logger.info(f"Starting evaluation of submission: {submission_dir}")
        
        # Load evaluation tasks
        tasks = self._load_evaluation_tasks(submission_dir)
        if not tasks:
            logger.error("No evaluation tasks found")
            return {"error": "No evaluation tasks found"}
        
        logger.info(f"Loaded {len(tasks)} evaluation tasks")
        
        # Process in batches
        all_results = []
        for i in range(0, len(tasks), self.batch_size):
            batch_tasks = tasks[i:i + self.batch_size]
            batch_images = self._load_generated_images(batch_tasks, submission_dir)
            
            # Evaluate batch
            batch_results = self.batch_evaluate(batch_tasks, batch_images)
            all_results.extend(batch_results)
            
            # Save checkpoint
            if (i + self.batch_size) % self.checkpoint_interval == 0:
                self._save_checkpoint(all_results, i + self.batch_size, output_path)
            
            logger.info(f"Processed {min(i + self.batch_size, len(tasks))}/{len(tasks)} samples")
        
        # Generate final report
        report = self._generate_final_report(all_results)
        
        # Save results
        self._save_results(all_results, report, output_path)
        
        logger.info(f"Evaluation completed. Results saved to {output_path}")
        
        return report

    def evaluate_single_sample(self, task: EvaluationTask, generated_image: np.ndarray) -> EvaluationResult:
        """
        Evaluate a single VTON sample.
        
        Args:
            task: Evaluation task with paths and metadata
            generated_image: Generated try-on image
            
        Returns:
            EvaluationResult with all scores
        """
        results = {}
        detailed_scores = {}
        
        # Run each evaluator
        for name, evaluator in self.evaluators.items():
            try:
                scores = evaluator.evaluate(task, generated_image)
                
                # Extract main score
                if name == 'garment':
                    results['garment_score'] = scores.get('garment_preservation_score', 0.0)
                elif name == 'identity':
                    results['identity_score'] = scores.get('identity_preservation_score', 0.0)
                elif name == 'body':
                    results['body_score'] = scores.get('body_shape_score', 0.0)
                elif name == 'fit':
                    results['fit_score'] = scores.get('fit_quality_score', 0.0)
                
                # Store all detailed scores
                detailed_scores[name] = scores
                
            except Exception as e:
                logger.error(f"Error in {name} evaluator: {e}")
                results[f'{name}_score'] = 0.0
                detailed_scores[name] = {"error": str(e)}
        
        # Calculate overall score
        overall_score = self.scorer.calculate_overall_score(results)
        
        # Create result object
        result = EvaluationResult(
            task_id=task.metadata.get('id', 'unknown'),
            garment_score=results.get('garment_score', 0.0),
            identity_score=results.get('identity_score', 0.0),
            body_score=results.get('body_score', 0.0),
            fit_score=results.get('fit_score', 0.0),
            overall_score=overall_score,
            metadata={
                'detailed_scores': detailed_scores,
                'task_metadata': task.metadata,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return result

    def batch_evaluate(self, tasks: List[EvaluationTask], images: List[np.ndarray]) -> List[EvaluationResult]:
        """
        Evaluate a batch of samples.
        
        Args:
            tasks: List of evaluation tasks
            images: List of generated images
            
        Returns:
            List of evaluation results
        """
        if len(tasks) != len(images):
            raise ValueError(f"Number of tasks ({len(tasks)}) doesn't match number of images ({len(images)})")
        
        results = []
        
        # Process each sample
        for task, image in tqdm(zip(tasks, images), total=len(tasks), desc="Evaluating samples"):
            result = self.evaluate_single_sample(task, image)
            results.append(result)
        
        return results

    def resume_evaluation(self, checkpoint_path: str) -> Dict[str, Any]:
        """
        Resume evaluation from a checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint file
            
        Returns:
            Dictionary with resume status and results
        """
        try:
            with open(checkpoint_path, 'rb') as f:
                checkpoint = pickle.load(f)
            
            self.current_checkpoint = checkpoint
            logger.info(f"Resumed from checkpoint: {checkpoint['processed_samples']} samples processed")
            
            return {
                'status': 'resumed',
                'processed_samples': checkpoint['processed_samples'],
                'partial_results': checkpoint['results']
            }
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _load_evaluation_tasks(self, submission_dir: str) -> List[EvaluationTask]:
        """Load evaluation tasks from submission directory."""
        tasks = []
        
        # Look for metadata file
        metadata_path = Path(submission_dir) / 'metadata.json'
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            for item in metadata:
                task = EvaluationTask(
                    human_image=item['human_image'],
                    garment_image=item['garment_image'],
                    measurements=item.get('measurements', {}),
                    metadata=item
                )
                tasks.append(task)
        else:
            # Fallback: scan directory for images
            logger.warning("No metadata.json found, scanning directory for images")
            # Implementation would depend on naming convention
        
        return tasks
    
    def _load_generated_images(self, tasks: List[EvaluationTask], submission_dir: str) -> List[np.ndarray]:
        """Load generated images for the given tasks."""
        images = []
        
        for task in tasks:
            # Construct generated image path based on task ID
            task_id = task.metadata.get('id', 'unknown')
            image_path = Path(submission_dir) / f"{task_id}_generated.jpg"
            
            if not image_path.exists():
                # Try alternative naming schemes
                image_path = Path(submission_dir) / f"{task_id}.jpg"
            
            if image_path.exists():
                image = cv2.imread(str(image_path))
                if image is not None:
                    images.append(image)
                else:
                    logger.error(f"Failed to load image: {image_path}")
                    images.append(np.zeros((512, 384, 3), dtype=np.uint8))
            else:
                logger.error(f"Generated image not found: {image_path}")
                images.append(np.zeros((512, 384, 3), dtype=np.uint8))
        
        return images
    
    def _save_checkpoint(self, results: List[EvaluationResult], processed_samples: int, output_path: str):
        """Save evaluation checkpoint."""
        checkpoint = {
            'results': results,
            'processed_samples': processed_samples,
            'timestamp': datetime.now().isoformat(),
            'config': self.config.config
        }
        
        checkpoint_path = Path(output_path).parent / f"checkpoint_{processed_samples}.pkl"
        with open(checkpoint_path, 'wb') as f:
            pickle.dump(checkpoint, f)
        
        logger.info(f"Saved checkpoint: {checkpoint_path}")
    
    def _generate_final_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Generate final evaluation report."""
        # Use scorer to aggregate results
        statistics = self.scorer.generate_statistics(results)
        
        # Generate detailed report
        detailed_report = self.reporter.generate_detailed_report(results)
        
        # Generate leaderboard entry
        leaderboard_entry = self.reporter.generate_leaderboard_entry(results)
        
        report = {
            'summary': statistics,
            'detailed_report': detailed_report,
            'leaderboard_entry': leaderboard_entry,
            'num_samples': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
        return report
    
    def _save_results(self, results: List[EvaluationResult], report: Dict[str, Any], output_path: str):
        """Save evaluation results and report."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results as JSON
        self.reporter.export_to_json(results, str(output_dir / 'detailed_results.json'))
        
        # Save results as CSV
        self.reporter.export_to_csv(results, str(output_dir / 'results.csv'))
        
        # Save report
        with open(output_dir / 'evaluation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate visualizations if enabled
        if self.config.config.get('evaluation', {}).get('generate_visualizations', True):
            visualizations = self.reporter.generate_visualizations(results)
            # Save visualization data
            with open(output_dir / 'visualizations.json', 'w') as f:
                json.dump(visualizations, f, indent=2)
