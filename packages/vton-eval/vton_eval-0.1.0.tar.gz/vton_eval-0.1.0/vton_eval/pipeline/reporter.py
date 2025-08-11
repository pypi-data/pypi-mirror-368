from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationResult
from typing import List, Dict, Any, Optional
import json
import csv
import logging
from datetime import datetime
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


class VTONReporter:
    """
    Report generator for VTON evaluation results.
    Handles report generation, data export, and visualization.
    """
    
    def __init__(self, config: VTONConfig):
        self.config = config
        self.report_config = config.config.get('reporting', {})
        self.include_visualizations = self.report_config.get('include_visualizations', True)
        
        # Set up visualization style
        if self.include_visualizations:
            try:
                plt.style.use('seaborn-v0_8-darkgrid')
                sns.set_palette("husl")
            except:
                # Fallback if style not available
                plt.style.use('default')

    def generate_detailed_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate a comprehensive detailed report from evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with detailed report data
        """
        if not results:
            return {
                'status': 'error',
                'message': 'No results to generate report from'
            }
        
        # Group results by score ranges
        score_ranges = {
            'excellent': [],  # 0.9-1.0
            'good': [],      # 0.8-0.9
            'fair': [],      # 0.7-0.8
            'poor': []       # 0.0-0.7
        }
        
        for result in results:
            if result.overall_score >= 0.9:
                score_ranges['excellent'].append(result)
            elif result.overall_score >= 0.8:
                score_ranges['good'].append(result)
            elif result.overall_score >= 0.7:
                score_ranges['fair'].append(result)
            else:
                score_ranges['poor'].append(result)
        
        # Component-wise analysis
        component_analysis = self._analyze_components(results)
        
        # Identify best and worst performing samples
        sorted_results = sorted(results, key=lambda r: r.overall_score, reverse=True)
        top_samples = sorted_results[:10]
        bottom_samples = sorted_results[-10:]
        
        # Generate insights
        insights = self._generate_insights(results, component_analysis)
        
        # Create detailed report
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'num_samples': len(results),
                'evaluation_version': '1.0.0',
                'config_used': self.config.config
            },
            'summary_statistics': {
                'overall_mean': float(np.mean([r.overall_score for r in results])),
                'overall_std': float(np.std([r.overall_score for r in results])),
                'overall_min': float(np.min([r.overall_score for r in results])),
                'overall_max': float(np.max([r.overall_score for r in results]))
            },
            'score_distribution': {
                'excellent': len(score_ranges['excellent']),
                'good': len(score_ranges['good']),
                'fair': len(score_ranges['fair']),
                'poor': len(score_ranges['poor'])
            },
            'component_analysis': component_analysis,
            'top_performing_samples': [{
                'id': r.task_id,
                'overall_score': r.overall_score,
                'scores': {
                    'garment': r.garment_score,
                    'identity': r.identity_score,
                    'body': r.body_score,
                    'fit': r.fit_score
                }
            } for r in top_samples],
            'bottom_performing_samples': [{
                'id': r.task_id,
                'overall_score': r.overall_score,
                'scores': {
                    'garment': r.garment_score,
                    'identity': r.identity_score,
                    'body': r.body_score,
                    'fit': r.fit_score
                }
            } for r in bottom_samples],
            'insights': insights,
            'recommendations': self._generate_recommendations(results, component_analysis)
        }
        
        return report

    def generate_leaderboard_entry(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate a leaderboard entry from evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with leaderboard entry data
        """
        if not results:
            return {}
        
        # Calculate key metrics
        overall_scores = [r.overall_score for r in results]
        garment_scores = [r.garment_score for r in results]
        identity_scores = [r.identity_score for r in results]
        body_scores = [r.body_score for r in results]
        fit_scores = [r.fit_score for r in results]
        
        # Production ready count
        threshold = self.config.get_production_thresholds()
        production_ready = sum(1 for r in results if r.overall_score >= threshold)
        
        leaderboard_entry = {
            'submission_id': self.config.config.get('submission', {}).get('id', 'unknown'),
            'team_name': self.config.config.get('submission', {}).get('team_name', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'num_samples': len(results),
            'metrics': {
                'overall_score': float(np.mean(overall_scores)),
                'garment_preservation': float(np.mean(garment_scores)),
                'identity_preservation': float(np.mean(identity_scores)),
                'body_shape_consistency': float(np.mean(body_scores)),
                'fit_quality': float(np.mean(fit_scores)),
                'production_ready_percentage': (production_ready / len(results)) * 100
            },
            'percentiles': {
                'p50_overall': float(np.percentile(overall_scores, 50)),
                'p90_overall': float(np.percentile(overall_scores, 90)),
                'p95_overall': float(np.percentile(overall_scores, 95))
            }
        }
        
        return leaderboard_entry

    def export_to_csv(self, results: List[EvaluationResult], output_path: str) -> None:
        """
        Export evaluation results to CSV format.
        
        Args:
            results: List of evaluation results
            output_path: Path to save CSV file
        """
        if not results:
            logger.warning("No results to export to CSV")
            return
        
        fieldnames = [
            'task_id', 'overall_score', 'garment_score', 'identity_score',
            'body_score', 'fit_score', 'timestamp'
        ]
        
        # Add detailed score fields if available
        sample_metadata = results[0].metadata.get('detailed_scores', {})
        if sample_metadata:
            for evaluator, scores in sample_metadata.items():
                if isinstance(scores, dict):
                    for score_name in scores.keys():
                        fieldnames.append(f"{evaluator}_{score_name}")
        
        try:
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {
                        'task_id': result.task_id,
                        'overall_score': result.overall_score,
                        'garment_score': result.garment_score,
                        'identity_score': result.identity_score,
                        'body_score': result.body_score,
                        'fit_score': result.fit_score,
                        'timestamp': result.metadata.get('timestamp', '')
                    }
                    
                    # Add detailed scores
                    detailed_scores = result.metadata.get('detailed_scores', {})
                    for evaluator, scores in detailed_scores.items():
                        if isinstance(scores, dict):
                            for score_name, score_value in scores.items():
                                row[f"{evaluator}_{score_name}"] = score_value
                    
                    writer.writerow(row)
            
            logger.info(f"Exported {len(results)} results to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")

    def export_to_json(self, results: List[EvaluationResult], output_path: str) -> None:
        """
        Export evaluation results to JSON format.
        
        Args:
            results: List of evaluation results
            output_path: Path to save JSON file
        """
        try:
            # Convert results to serializable format
            serializable_results = []
            for result in results:
                result_dict = {
                    'task_id': result.task_id,
                    'scores': {
                        'overall': result.overall_score,
                        'garment': result.garment_score,
                        'identity': result.identity_score,
                        'body': result.body_score,
                        'fit': result.fit_score
                    },
                    'metadata': result.metadata
                }
                serializable_results.append(result_dict)
            
            with open(output_path, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            
            logger.info(f"Exported {len(results)} results to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")

    def generate_visualizations(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Generate visualizations from evaluation results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with visualization data (base64 encoded images)
        """
        if not self.include_visualizations or not results:
            return {}
        
        visualizations = {}
        
        try:
            # 1. Overall score distribution
            fig, ax = plt.subplots(figsize=(10, 6))
            overall_scores = [r.overall_score for r in results]
            ax.hist(overall_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_xlabel('Overall Score')
            ax.set_ylabel('Count')
            ax.set_title('Distribution of Overall Scores')
            ax.axvline(np.mean(overall_scores), color='red', linestyle='--', label=f'Mean: {np.mean(overall_scores):.3f}')
            ax.legend()
            visualizations['overall_distribution'] = self._fig_to_base64(fig)
            plt.close(fig)
            
            # 2. Component scores comparison
            fig, ax = plt.subplots(figsize=(10, 6))
            components = ['Garment', 'Identity', 'Body', 'Fit']
            means = [
                np.mean([r.garment_score for r in results]),
                np.mean([r.identity_score for r in results]),
                np.mean([r.body_score for r in results]),
                np.mean([r.fit_score for r in results])
            ]
            stds = [
                np.std([r.garment_score for r in results]),
                np.std([r.identity_score for r in results]),
                np.std([r.body_score for r in results]),
                np.std([r.fit_score for r in results])
            ]
            
            x = np.arange(len(components))
            bars = ax.bar(x, means, yerr=stds, capsize=5, alpha=0.7, 
                          color=['coral', 'lightgreen', 'gold', 'lightblue'])
            ax.set_xlabel('Component')
            ax.set_ylabel('Score')
            ax.set_title('Mean Scores by Component (with std dev)')
            ax.set_xticks(x)
            ax.set_xticklabels(components)
            ax.set_ylim(0, 1.1)
            
            # Add value labels on bars
            for bar, mean in zip(bars, means):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{mean:.3f}', ha='center', va='bottom')
            
            visualizations['component_comparison'] = self._fig_to_base64(fig)
            plt.close(fig)
            
            # 3. Score correlation heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            score_data = np.array([
                [r.garment_score, r.identity_score, r.body_score, r.fit_score]
                for r in results
            ])
            corr_matrix = np.corrcoef(score_data.T)
            
            sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                       xticklabels=components, yticklabels=components,
                       center=0, vmin=-1, vmax=1, ax=ax)
            ax.set_title('Component Score Correlations')
            visualizations['correlation_heatmap'] = self._fig_to_base64(fig)
            plt.close(fig)
            
            # 4. Quality tier pie chart
            fig, ax = plt.subplots(figsize=(8, 8))
            tiers = ['Excellent\n(≥0.9)', 'Good\n(0.8-0.9)', 'Fair\n(0.7-0.8)', 'Poor\n(<0.7)']
            counts = [
                sum(1 for r in results if r.overall_score >= 0.9),
                sum(1 for r in results if 0.8 <= r.overall_score < 0.9),
                sum(1 for r in results if 0.7 <= r.overall_score < 0.8),
                sum(1 for r in results if r.overall_score < 0.7)
            ]
            
            colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
            explode = (0.05, 0.05, 0.05, 0.05)
            
            wedges, texts, autotexts = ax.pie(counts, labels=tiers, colors=colors,
                                              autopct='%1.1f%%', startangle=90,
                                              explode=explode, shadow=True)
            
            # Make percentage text bold
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(12)
                autotext.set_weight('bold')
            
            ax.set_title('Quality Tier Distribution', fontsize=16, pad=20)
            visualizations['quality_tiers'] = self._fig_to_base64(fig)
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Failed to generate visualizations: {e}")
        
        return visualizations
    
    def _fig_to_base64(self, fig) -> str:
        """
        Convert matplotlib figure to base64 encoded string.
        
        Args:
            fig: Matplotlib figure
            
        Returns:
            Base64 encoded image string
        """
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        return f"data:image/png;base64,{image_base64}"
    
    def _analyze_components(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """
        Analyze component-wise performance.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with component analysis
        """
        components = ['garment', 'identity', 'body', 'fit']
        analysis = {}
        
        for component in components:
            scores = [getattr(r, f"{component}_score") for r in results]
            
            analysis[component] = {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'min': float(np.min(scores)),
                'max': float(np.max(scores)),
                'median': float(np.median(scores)),
                'failures': sum(1 for s in scores if s < 0.7),
                'excellent': sum(1 for s in scores if s >= 0.9)
            }
        
        return analysis
    
    def _generate_insights(self, results: List[EvaluationResult], 
                          component_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate insights from evaluation results.
        
        Args:
            results: List of evaluation results
            component_analysis: Component-wise analysis
            
        Returns:
            List of insight strings
        """
        insights = []
        
        # Overall performance insight
        overall_mean = np.mean([r.overall_score for r in results])
        if overall_mean >= 0.85:
            insights.append(f"Excellent overall performance with mean score of {overall_mean:.3f}")
        elif overall_mean >= 0.75:
            insights.append(f"Good overall performance with mean score of {overall_mean:.3f}")
        else:
            insights.append(f"Performance needs improvement with mean score of {overall_mean:.3f}")
        
        # Component-specific insights
        weakest_component = min(component_analysis.items(), key=lambda x: x[1]['mean'])
        strongest_component = max(component_analysis.items(), key=lambda x: x[1]['mean'])
        
        insights.append(f"Strongest component: {strongest_component[0]} (mean: {strongest_component[1]['mean']:.3f})")
        insights.append(f"Weakest component: {weakest_component[0]} (mean: {weakest_component[1]['mean']:.3f})")
        
        # Consistency insight
        std_scores = [component_analysis[c]['std'] for c in ['garment', 'identity', 'body', 'fit']]
        avg_std = np.mean(std_scores)
        if avg_std < 0.1:
            insights.append("Very consistent performance across samples")
        elif avg_std < 0.2:
            insights.append("Moderately consistent performance across samples")
        else:
            insights.append("High variability in performance across samples")
        
        # Failure pattern insights
        for component, data in component_analysis.items():
            if data['failures'] > len(results) * 0.2:
                insights.append(f"High failure rate in {component} preservation ({data['failures']} samples < 0.7)")
        
        return insights
    
    def _generate_recommendations(self, results: List[EvaluationResult],
                                 component_analysis: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on evaluation results.
        
        Args:
            results: List of evaluation results
            component_analysis: Component-wise analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Component-specific recommendations
        for component, data in component_analysis.items():
            if data['mean'] < 0.7:
                if component == 'garment':
                    recommendations.append("Focus on improving garment texture and pattern preservation")
                elif component == 'identity':
                    recommendations.append("Enhance face and body characteristic preservation")
                elif component == 'body':
                    recommendations.append("Improve body shape and proportion consistency")
                elif component == 'fit':
                    recommendations.append("Work on realistic garment draping and fit")
        
        # Consistency recommendations
        if any(data['std'] > 0.2 for data in component_analysis.values()):
            recommendations.append("Reduce performance variability across different input types")
        
        # Overall recommendations
        overall_mean = np.mean([r.overall_score for r in results])
        if overall_mean < 0.8:
            recommendations.append("Consider architectural improvements or training enhancements")
        
        if not recommendations:
            recommendations.append("Maintain current performance and focus on edge cases")
        
        return recommendations
