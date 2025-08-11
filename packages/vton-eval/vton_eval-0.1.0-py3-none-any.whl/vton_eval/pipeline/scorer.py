from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationResult
from typing import List, Dict, Any, Union
import numpy as np
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class VTONScorer:
    """
    Score aggregator for VTON evaluation results.
    Handles score calculation, aggregation, and statistical analysis.
    """
    
    def __init__(self, config: VTONConfig):
        self.weights = config.get_scoring_weights()
        self.threshold = config.get_production_thresholds()
        
        # Default weights if not specified in config
        if not self.weights:
            self.weights = {
                'garment': 0.35,
                'identity': 0.25,
                'body': 0.20,
                'fit': 0.20
            }
        
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v/total_weight for k, v in self.weights.items()}
        
        logger.info(f"Initialized VTONScorer with weights: {self.weights}")
    
    def calculate_overall_score(self, scores: Union[Dict[str, float], EvaluationResult]) -> float:
        """
        Calculate weighted overall score from individual component scores.
        
        Args:
            scores: Either a dictionary of scores or an EvaluationResult object
            
        Returns:
            Weighted overall score between 0.0 and 1.0
        """
        if isinstance(scores, EvaluationResult):
            # Convert EvaluationResult to dict
            scores = {
                'garment': scores.garment_score,
                'identity': scores.identity_score,
                'body': scores.body_score,
                'fit': scores.fit_score
            }
        
        overall_score = 0.0
        
        for component, weight in self.weights.items():
            if component in scores:
                score = scores[component]
                # Ensure score is in valid range
                score = max(0.0, min(1.0, score))
                overall_score += score * weight
            else:
                logger.warning(f"Missing score for component: {component}")
        
        return float(overall_score)

    def is_production_ready(self, result: EvaluationResult) -> bool:
        """
        Check if the evaluation result meets production quality threshold.
        
        Args:
            result: Evaluation result to check
            
        Returns:
            True if meets production threshold
        """
        overall_score = result.overall_score
        
        # Check overall threshold
        if overall_score < self.threshold:
            return False
        
        # Check individual component thresholds if specified
        component_thresholds = self.threshold if isinstance(self.threshold, dict) else {}
        
        if 'garment' in component_thresholds and result.garment_score < component_thresholds['garment']:
            return False
        if 'identity' in component_thresholds and result.identity_score < component_thresholds['identity']:
            return False
        if 'body' in component_thresholds and result.body_score < component_thresholds['body']:
            return False
        if 'fit' in component_thresholds and result.fit_score < component_thresholds['fit']:
            return False
        
        return True

    def aggregate_batch_results(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Aggregate results from a batch of evaluations.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not results:
            return {
                'num_samples': 0,
                'mean_scores': {},
                'std_scores': {},
                'production_ready_count': 0,
                'production_ready_percentage': 0.0
            }
        
        # Collect scores by component
        scores_by_component = defaultdict(list)
        overall_scores = []
        production_ready_count = 0
        
        for result in results:
            scores_by_component['garment'].append(result.garment_score)
            scores_by_component['identity'].append(result.identity_score)
            scores_by_component['body'].append(result.body_score)
            scores_by_component['fit'].append(result.fit_score)
            overall_scores.append(result.overall_score)
            
            if self.is_production_ready(result):
                production_ready_count += 1
        
        # Calculate statistics
        mean_scores = {}
        std_scores = {}
        min_scores = {}
        max_scores = {}
        
        for component, scores in scores_by_component.items():
            mean_scores[component] = float(np.mean(scores))
            std_scores[component] = float(np.std(scores))
            min_scores[component] = float(np.min(scores))
            max_scores[component] = float(np.max(scores))
        
        # Overall statistics
        mean_scores['overall'] = float(np.mean(overall_scores))
        std_scores['overall'] = float(np.std(overall_scores))
        min_scores['overall'] = float(np.min(overall_scores))
        max_scores['overall'] = float(np.max(overall_scores))
        
        return {
            'num_samples': len(results),
            'mean_scores': mean_scores,
            'std_scores': std_scores,
            'min_scores': min_scores,
            'max_scores': max_scores,
            'production_ready_count': production_ready_count,
            'production_ready_percentage': (production_ready_count / len(results)) * 100
        }

    def generate_statistics(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate comprehensive statistics from evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with detailed statistics
        """
        # Basic aggregation
        basic_stats = self.aggregate_batch_results(results)
        
        if not results:
            return basic_stats
        
        # Score distribution analysis
        score_distributions = {}
        percentiles = [10, 25, 50, 75, 90]
        
        for component in ['garment', 'identity', 'body', 'fit', 'overall']:
            if component == 'overall':
                scores = [r.overall_score for r in results]
            else:
                scores = [getattr(r, f"{component}_score") for r in results]
            
            score_distributions[component] = {
                'percentiles': {}
            }
            
            for p in percentiles:
                score_distributions[component]['percentiles'][f'p{p}'] = float(np.percentile(scores, p))
            
            # Score bins for histogram
            bins = np.linspace(0, 1, 11)
            hist, _ = np.histogram(scores, bins=bins)
            score_distributions[component]['histogram'] = {
                'bins': bins.tolist(),
                'counts': hist.tolist()
            }
        
        # Quality tier distribution
        quality_tiers = {
            'excellent': 0,  # >= 0.9
            'good': 0,       # >= 0.8
            'fair': 0,       # >= 0.7
            'poor': 0        # < 0.7
        }
        
        for result in results:
            if result.overall_score >= 0.9:
                quality_tiers['excellent'] += 1
            elif result.overall_score >= 0.8:
                quality_tiers['good'] += 1
            elif result.overall_score >= 0.7:
                quality_tiers['fair'] += 1
            else:
                quality_tiers['poor'] += 1
        
        # Component correlation analysis
        correlations = self._calculate_correlations(results)
        
        # Failure analysis
        failure_analysis = self._analyze_failures(results)
        
        return {
            **basic_stats,
            'score_distributions': score_distributions,
            'quality_tiers': quality_tiers,
            'correlations': correlations,
            'failure_analysis': failure_analysis,
            'weights_used': self.weights
        }
    
    def _calculate_correlations(self, results: List[EvaluationResult]) -> Dict[str, float]:
        """
        Calculate correlations between different score components.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with correlation coefficients
        """
        if len(results) < 2:
            return {}
        
        # Extract score arrays
        garment_scores = np.array([r.garment_score for r in results])
        identity_scores = np.array([r.identity_score for r in results])
        body_scores = np.array([r.body_score for r in results])
        fit_scores = np.array([r.fit_score for r in results])
        
        correlations = {}
        
        # Calculate pairwise correlations
        try:
            correlations['garment_identity'] = float(np.corrcoef(garment_scores, identity_scores)[0, 1])
            correlations['garment_body'] = float(np.corrcoef(garment_scores, body_scores)[0, 1])
            correlations['garment_fit'] = float(np.corrcoef(garment_scores, fit_scores)[0, 1])
            correlations['identity_body'] = float(np.corrcoef(identity_scores, body_scores)[0, 1])
            correlations['identity_fit'] = float(np.corrcoef(identity_scores, fit_scores)[0, 1])
            correlations['body_fit'] = float(np.corrcoef(body_scores, fit_scores)[0, 1])
        except Exception as e:
            logger.warning(f"Failed to calculate correlations: {e}")
        
        return correlations
    
    def _analyze_failures(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Analyze failure patterns in evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with failure analysis
        """
        failures = [r for r in results if not self.is_production_ready(r)]
        
        if not failures:
            return {
                'num_failures': 0,
                'failure_rate': 0.0,
                'primary_failure_reasons': {}
            }
        
        # Identify primary failure reason for each failed sample
        failure_reasons = defaultdict(int)
        
        for result in failures:
            min_component = None
            min_score = 1.0
            
            # Find the lowest scoring component
            for component, score in [
                ('garment', result.garment_score),
                ('identity', result.identity_score),
                ('body', result.body_score),
                ('fit', result.fit_score)
            ]:
                if score < min_score:
                    min_score = score
                    min_component = component
            
            if min_component:
                failure_reasons[min_component] += 1
        
        # Calculate average scores for failed samples
        failed_avg_scores = {}
        if failures:
            failed_avg_scores = {
                'garment': np.mean([r.garment_score for r in failures]),
                'identity': np.mean([r.identity_score for r in failures]),
                'body': np.mean([r.body_score for r in failures]),
                'fit': np.mean([r.fit_score for r in failures]),
                'overall': np.mean([r.overall_score for r in failures])
            }
        
        return {
            'num_failures': len(failures),
            'failure_rate': (len(failures) / len(results)) * 100,
            'primary_failure_reasons': dict(failure_reasons),
            'failed_samples_avg_scores': failed_avg_scores
        }
