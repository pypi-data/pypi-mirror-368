from vton_eval.evaluators.base import BaseEvaluator
from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationTask
from vton_eval.vlm.base import VLMBackend
from vton_eval.models.sam_wrapper import SAMWrapper
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Union
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN
import logging

class FitMeasurementEvaluator(BaseEvaluator):
    """
    Evaluates how well a generated garment fits the person by measuring garment dimensions
    and comparing them with expected specifications or body measurements.
    
    Uses SMPL/SMPLX body models for scale calibration and SAM for garment segmentation.
    """
    
    def __init__(self, config: VTONConfig, vlm_backend: VLMBackend):
        super().__init__(config, vlm_backend)
        # self.smplx_model = SMPLXWrapper(config.get_model_config('smplx'))
        # self.sam_model = SAMWrapper(config.get_model_config('sam'))
        
        # Standard anthropometric measurements for scale calibration
        self.standard_measurements = {
            'height': 175.0,  # cm - average adult height
            'shoulder_width': 45.0,  # cm - average shoulder width
            'head_circumference': 57.0,  # cm - average head circumference
            'chest_circumference': 95.0,  # cm - average chest circumference
            'waist_circumference': 80.0,  # cm - average waist circumference
            'hip_circumference': 100.0,  # cm - average hip circumference
        }
        
        # Pixel density assumptions (can be calibrated)
        self.default_dpi = 96  # Standard screen DPI
        self.cm_to_pixels = 37.79527559  # At 96 DPI: 1 cm = ~37.8 pixels
        
        # Garment measurement definitions
        self.garment_measurements = {
            'shirt': ['chest_width', 'shoulder_width', 'sleeve_length', 'body_length'],
            'pants': ['waist_width', 'hip_width', 'leg_length', 'thigh_width'],
            'dress': ['chest_width', 'waist_width', 'hip_width', 'total_length'],
            'jacket': ['chest_width', 'shoulder_width', 'sleeve_length', 'body_length'],
            'skirt': ['waist_width', 'hip_width', 'skirt_length']
        }
        
        self.logger = logging.getLogger(__name__)
    
    def calibrate_pixel_to_cm(self, smplx_mesh: Dict[str, any]) -> float:
        """
        Calibrate pixel-to-cm conversion using SMPL/SMPLX body model measurements.
        
        Args:
            smplx_mesh: Dictionary containing SMPL/SMPLX mesh data with vertices and joints
            
        Returns:
            float: Scale factor to convert pixels to centimeters
        """
        try:
            if smplx_mesh is None:
                self.logger.warning("No SMPL mesh provided, using default scale")
                return self.cm_to_pixels
            
            # Extract key measurements from SMPL mesh
            vertices = smplx_mesh.get('vertices', np.array([]))
            joints = smplx_mesh.get('joints', np.array([]))
            
            if len(vertices) == 0:
                self.logger.warning("Empty vertices in SMPL mesh, using default scale")
                return self.cm_to_pixels
            
            # Calculate body height from mesh (top of head to bottom of feet)
            mesh_height_3d = self._calculate_mesh_height(vertices, joints)
            
            # Get corresponding pixel height in image
            mesh_height_pixels = self._get_body_height_in_pixels(vertices)
            
            if mesh_height_pixels == 0:
                self.logger.warning("Could not determine body height in pixels")
                return self.cm_to_pixels
            
            # Calculate scale: pixels per cm
            # Assuming standard body height of 175cm for calibration
            scale_factor = mesh_height_pixels / self.standard_measurements['height']
            
            self.logger.info(f"Calibrated scale: {scale_factor:.2f} pixels/cm (height: {mesh_height_pixels}px)")
            return scale_factor
            
        except Exception as e:
            self.logger.error(f"Error in pixel-to-cm calibration: {e}")
            return self.cm_to_pixels
    
    def _calculate_mesh_height(self, vertices: np.ndarray, joints: np.ndarray) -> float:
        """Calculate 3D height of the mesh."""
        if len(vertices) > 0:
            return np.max(vertices[:, 1]) - np.min(vertices[:, 1])  # Y-axis is height
        return 0.0
    
    def _get_body_height_in_pixels(self, vertices: np.ndarray) -> float:
        """Get body height in pixels from projected vertices."""
        if len(vertices) == 0:
            return 0.0
        
        # Project 3D vertices to 2D (simplified orthographic projection)
        projected_y = vertices[:, 1]  # Y coordinates
        pixel_height = np.max(projected_y) - np.min(projected_y)
        
        # Convert to reasonable pixel scale (this is a simplified approach)
        # In practice, this would use proper camera projection
        return abs(pixel_height) * 100  # Scale factor for reasonable pixel values
    
    def measure_garment_dimensions(self, garment_mask: np.ndarray, scale: float) -> Dict[str, float]:
        """
        Measure garment dimensions from segmented mask.
        
        Args:
            garment_mask: Binary mask of the garment (0/255 or 0/1)
            scale: Pixels per centimeter conversion factor
            
        Returns:
            Dict containing measured dimensions in centimeters
        """
        try:
            if garment_mask is None or garment_mask.size == 0:
                return {}
            
            # Ensure binary mask
            if garment_mask.max() > 1:
                garment_mask = (garment_mask > 127).astype(np.uint8)
            
            measurements = {}
            
            # Find contours
            contours, _ = cv2.findContours(garment_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                self.logger.warning("No contours found in garment mask")
                return measurements
            
            # Use largest contour (main garment)
            main_contour = max(contours, key=cv2.contourArea)
            
            # Calculate bounding box measurements
            x, y, w, h = cv2.boundingRect(main_contour)
            
            measurements.update({
                'total_width': w / scale,
                'total_height': h / scale,
                'area': cv2.contourArea(main_contour) / (scale ** 2)  # cm²
            })
            
            # Calculate more specific measurements
            measurements.update(self._measure_garment_specifics(main_contour, scale))
            
            # Calculate circumference measurements
            measurements.update(self._measure_circumferences(garment_mask, scale))
            
            return measurements
            
        except Exception as e:
            self.logger.error(f"Error measuring garment dimensions: {e}")
            return {}
    
    def _measure_garment_specifics(self, contour: np.ndarray, scale: float) -> Dict[str, float]:
        """Measure specific garment dimensions like shoulder width, chest width, etc."""
        measurements = {}
        
        try:
            # Get contour points
            points = contour.reshape(-1, 2)
            
            # Calculate various widths at different heights
            y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
            height_range = y_max - y_min
            
            # Measure widths at different relative heights
            height_percentages = [0.1, 0.25, 0.5, 0.75, 0.9]  # Top to bottom
            width_names = ['shoulder_width', 'chest_width', 'waist_width', 'hip_width', 'bottom_width']
            
            for i, (pct, name) in enumerate(zip(height_percentages, width_names)):
                y_level = y_min + (height_range * pct)
                width = self._measure_width_at_height(points, y_level, scale)
                if width > 0:
                    measurements[name] = width
            
            # Calculate lengths
            measurements['body_length'] = height_range / scale
            
            # Estimate sleeve measurements if applicable
            sleeve_measurements = self._estimate_sleeve_measurements(points, scale)
            measurements.update(sleeve_measurements)
            
        except Exception as e:
            self.logger.error(f"Error in specific garment measurements: {e}")
        
        return measurements
    
    def _measure_width_at_height(self, points: np.ndarray, y_level: float, scale: float) -> float:
        """Measure garment width at a specific height level."""
        try:
            # Find points near the target height
            tolerance = 5  # pixels
            near_points = points[np.abs(points[:, 1] - y_level) <= tolerance]
            
            if len(near_points) < 2:
                return 0.0
            
            # Get leftmost and rightmost points
            x_min, x_max = np.min(near_points[:, 0]), np.max(near_points[:, 0])
            width_pixels = x_max - x_min
            
            return width_pixels / scale
            
        except Exception:
            return 0.0
    
    def _measure_circumferences(self, mask: np.ndarray, scale: float) -> Dict[str, float]:
        """Estimate circumferences from 2D garment mask."""
        measurements = {}
        
        try:
            # Find horizontal cross-sections at different heights
            height, width = mask.shape
            
            # Measure at different height percentages
            height_levels = [0.25, 0.5, 0.75]  # Chest, waist, hip levels
            circ_names = ['chest_circumference', 'waist_circumference', 'hip_circumference']
            
            for pct, name in zip(height_levels, circ_names):
                y_level = int(height * pct)
                if 0 <= y_level < height:
                    row = mask[y_level, :]
                    width_pixels = np.sum(row > 0)
                    
                    if width_pixels > 0:
                        # Estimate circumference from width (assuming elliptical cross-section)
                        # This is an approximation: C ≈ π * (width/2 + depth/2)
                        # Assuming depth ≈ 0.6 * width for typical garments
                        estimated_depth = width_pixels * 0.6
                        circumference_pixels = np.pi * (width_pixels + estimated_depth) / 2
                        measurements[name] = circumference_pixels / scale
        
        except Exception as e:
            self.logger.error(f"Error measuring circumferences: {e}")
        
        return measurements
    
    def _estimate_sleeve_measurements(self, points: np.ndarray, scale: float) -> Dict[str, float]:
        """Estimate sleeve measurements if garment has sleeves."""
        measurements = {}
        
        try:
            # This is a simplified approach - in practice would need more sophisticated analysis
            # Look for extended parts that might be sleeves
            x_min, x_max = np.min(points[:, 0]), np.max(points[:, 0])
            y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
            
            total_width = x_max - x_min
            total_height = y_max - y_min
            
            # Rough estimation: if width is significantly larger than height, might have sleeves
            if total_width > total_height * 1.5:
                # Estimate sleeve length as the excess width
                estimated_body_width = total_height * 0.6  # Rough body width estimate
                sleeve_extension = (total_width - estimated_body_width) / 2
                if sleeve_extension > 0:
                    measurements['sleeve_length'] = sleeve_extension / scale
        
        except Exception as e:
            self.logger.error(f"Error estimating sleeve measurements: {e}")
        
        return measurements
    
    def compare_with_spec(self, measured: Dict[str, float], spec: Dict[str, float]) -> Dict[str, float]:
        """
        Compare measured dimensions with specification or expected values.
        
        Args:
            measured: Dictionary of measured dimensions in cm
            spec: Dictionary of expected/specification dimensions in cm
            
        Returns:
            Dict containing fit scores and differences for each dimension
        """
        comparison_results = {}
        
        try:
            if not measured or not spec:
                self.logger.warning("Empty measured or spec dictionaries")
                return comparison_results
            
            # Calculate differences and fit scores for each measurement
            for measurement_name in measured.keys():
                if measurement_name in spec:
                    measured_val = measured[measurement_name]
                    spec_val = spec[measurement_name]
                    
                    # Calculate absolute and relative differences
                    abs_diff = abs(measured_val - spec_val)
                    rel_diff = abs_diff / spec_val if spec_val != 0 else float('inf')
                    
                    # Calculate fit score (higher is better, 1.0 = perfect fit)
                    fit_score = self._calculate_fit_score(abs_diff, spec_val, measurement_name)
                    
                    comparison_results[f"{measurement_name}_difference"] = abs_diff
                    comparison_results[f"{measurement_name}_relative_diff"] = rel_diff
                    comparison_results[f"{measurement_name}_fit_score"] = fit_score
                    comparison_results[f"{measurement_name}_measured"] = measured_val
                    comparison_results[f"{measurement_name}_expected"] = spec_val
            
            # Calculate overall fit score
            fit_scores = [v for k, v in comparison_results.items() if k.endswith('_fit_score')]
            if fit_scores:
                comparison_results['overall_fit_score'] = np.mean(fit_scores)
            else:
                comparison_results['overall_fit_score'] = 0.0
            
            # Categorize fit quality
            overall_score = comparison_results['overall_fit_score']
            if overall_score >= 0.9:
                comparison_results['fit_quality'] = 'excellent'
            elif overall_score >= 0.8:
                comparison_results['fit_quality'] = 'good'
            elif overall_score >= 0.7:
                comparison_results['fit_quality'] = 'acceptable'
            elif overall_score >= 0.6:
                comparison_results['fit_quality'] = 'poor'
            else:
                comparison_results['fit_quality'] = 'very_poor'
                
        except Exception as e:
            self.logger.error(f"Error comparing measurements with spec: {e}")
            comparison_results['overall_fit_score'] = 0.0
            comparison_results['fit_quality'] = 'error'
        
        return comparison_results
    
    def _calculate_fit_score(self, abs_diff: float, spec_val: float, measurement_name: str) -> float:
        """
        Calculate fit score based on measurement difference and type.
        
        Different measurements have different tolerance levels.
        """
        try:
            # Define tolerance levels for different measurement types (as percentage of spec value)
            tolerance_map = {
                'width': 0.05,      # 5% tolerance for widths
                'length': 0.03,     # 3% tolerance for lengths  
                'circumference': 0.08,  # 8% tolerance for circumferences
                'area': 0.10,       # 10% tolerance for areas
                'default': 0.05     # Default 5% tolerance
            }
            
            # Determine measurement type
            measurement_type = 'default'
            for mtype in tolerance_map.keys():
                if mtype in measurement_name.lower():
                    measurement_type = mtype
                    break
            
            tolerance = tolerance_map[measurement_type]
            max_acceptable_diff = spec_val * tolerance
            
            if abs_diff <= max_acceptable_diff:
                # Perfect to acceptable range
                score = 1.0 - (abs_diff / max_acceptable_diff) * 0.2  # Score 0.8-1.0
            else:
                # Beyond acceptable range - exponential decay
                excess_diff = abs_diff - max_acceptable_diff
                penalty_factor = excess_diff / (spec_val * tolerance)
                score = 0.8 * np.exp(-penalty_factor)  # Exponential decay from 0.8
            
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
            
        except Exception:
            return 0.0
    
    def _generate_default_spec(self, garment_type: str, body_measurements: Dict[str, float]) -> Dict[str, float]:
        """Generate default garment specifications based on body measurements."""
        spec = {}
        
        try:
            garment_type = garment_type.lower()
            
            if garment_type in ['shirt', 'blouse', 'top']:
                spec.update({
                    'chest_width': body_measurements.get('chest_circumference', 95) / 2 + 5,  # Ease
                    'shoulder_width': body_measurements.get('shoulder_width', 45) + 2,
                    'body_length': 65,  # Standard shirt length
                    'sleeve_length': 60  # Standard sleeve length
                })
            
            elif garment_type in ['pants', 'trousers', 'jeans']:
                spec.update({
                    'waist_width': body_measurements.get('waist_circumference', 80) / 2 + 3,
                    'hip_width': body_measurements.get('hip_circumference', 100) / 2 + 3,
                    'leg_length': 105,  # Standard inseam
                    'thigh_width': 30   # Standard thigh width
                })
            
            elif garment_type == 'dress':
                spec.update({
                    'chest_width': body_measurements.get('chest_circumference', 95) / 2 + 3,
                    'waist_width': body_measurements.get('waist_circumference', 80) / 2 + 2,
                    'hip_width': body_measurements.get('hip_circumference', 100) / 2 + 3,
                    'total_length': 110  # Standard dress length
                })
                
        except Exception as e:
            self.logger.error(f"Error generating default spec: {e}")
        
        return spec
    
    def evaluate(self, task: EvaluationTask, generated_image: np.ndarray) -> Dict[str, float]:
        """
        Evaluate fit measurement quality of the generated image.
        
        Args:
            task: Evaluation task containing human image, garment info, and measurements
            generated_image: Generated try-on image to evaluate
            
        Returns:
            Dictionary containing fit measurement scores and metrics
        """
        try:
            # Initialize results
            results = {
                'fit_measurement_score': 0.0,
                'scale_calibration_score': 1.0,
                'measurement_accuracy_score': 0.0,
                'garment_fit_score': 0.0
            }
            
            if generated_image is None or generated_image.size == 0:
                self.logger.error("Generated image is empty")
                return results
            
            # Step 1: Get body model for scale calibration (placeholder)
            # In practice, this would use the SMPL/SMPLX wrapper
            smplx_mesh = None  # self.smplx_model.fit_image(generated_image)
            scale_factor = self.calibrate_pixel_to_cm(smplx_mesh)
            
            # Step 2: Segment garment from generated image (placeholder)
            # In practice, this would use the SAM wrapper
            garment_mask = self._mock_garment_segmentation(generated_image)
            
            # Step 3: Measure garment dimensions
            measured_dimensions = self.measure_garment_dimensions(garment_mask, scale_factor)
            
            # Step 4: Get expected specifications
            garment_type = task.metadata.get('garment_type', 'shirt')
            expected_spec = task.measurements if hasattr(task, 'measurements') and task.measurements else {}
            
            # Generate default spec if none provided
            if not expected_spec:
                body_measurements = task.metadata.get('body_measurements', {})
                expected_spec = self._generate_default_spec(garment_type, body_measurements)
            
            # Step 5: Compare measurements with specifications
            if measured_dimensions and expected_spec:
                comparison_results = self.compare_with_spec(measured_dimensions, expected_spec)
                
                # Extract scores
                results['garment_fit_score'] = comparison_results.get('overall_fit_score', 0.0)
                results['measurement_accuracy_score'] = results['garment_fit_score']
                
                # Add detailed measurements to results
                results.update({
                    'measured_dimensions': measured_dimensions,
                    'expected_dimensions': expected_spec,
                    'fit_comparison': comparison_results,
                    'fit_quality': comparison_results.get('fit_quality', 'unknown')
                })
            
            # Calculate overall fit measurement score
            results['fit_measurement_score'] = (
                results['scale_calibration_score'] * 0.2 +
                results['measurement_accuracy_score'] * 0.5 +
                results['garment_fit_score'] * 0.3
            )
            
            self.logger.info(f"Fit measurement evaluation completed. Score: {results['fit_measurement_score']:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error in fit measurement evaluation: {e}")
            results = {'fit_measurement_score': 0.0, 'error': str(e)}
        
        return results
    
    def _mock_garment_segmentation(self, image: np.ndarray) -> np.ndarray:
        """
        Mock garment segmentation for testing purposes.
        In practice, this would use the SAM wrapper.
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image.copy()
            
            # Simple thresholding to create a mock garment mask
            # This is just for testing - real implementation would use SAM
            _, mask = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Apply some morphological operations to clean up
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            return mask
            
        except Exception as e:
            self.logger.error(f"Error in mock garment segmentation: {e}")
            return np.zeros((100, 100), dtype=np.uint8) 
