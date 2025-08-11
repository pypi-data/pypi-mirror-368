from vton_eval.evaluators.base import BaseEvaluator
from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationTask
from vton_eval.vlm.base import VLMBackend
import numpy as np
import torch
import cv2
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import logging
import mediapipe as mp
import math
from scipy.spatial.distance import euclidean
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# Suppress MediaPipe warnings
warnings.filterwarnings("ignore", category=UserWarning)

logger = logging.getLogger(__name__)

class BodyShapeEvaluator(BaseEvaluator):
    """
    Evaluates how well the generated image preserves the person's body shape,
    proportions, and pose consistency from the original image.
    
    Uses multiple evaluation methods:
    1. 2D Keypoint Detection (MediaPipe)
    2. Body Proportion Analysis
    3. Pose Consistency Assessment
    4. VLM-based Body Shape Evaluation
    5. Anthropometric Measurements
    """
    
    def __init__(self, config: VTONConfig, vlm_backend: VLMBackend):
        super().__init__(config, vlm_backend)
        
        # Initialize device
        self.device = torch.device('cpu')
        
        # Initialize MediaPipe pose detection
        self._init_mediapipe_pose()
        
        # Body keypoint indices for MediaPipe Pose
        self.body_keypoints = {
            'nose': 0, 'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
            'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
            'left_ear': 7, 'right_ear': 8, 'mouth_left': 9, 'mouth_right': 10,
            'left_shoulder': 11, 'right_shoulder': 12, 'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16, 'left_pinky': 17, 'right_pinky': 18,
            'left_index': 19, 'right_index': 20, 'left_thumb': 21, 'right_thumb': 22,
            'left_hip': 23, 'right_hip': 24, 'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28, 'left_heel': 29, 'right_heel': 30,
            'left_foot_index': 31, 'right_foot_index': 32
        }
        
        # Key body ratios for anthropometric analysis
        self.body_ratio_pairs = {
            'shoulder_width_to_height': (['left_shoulder', 'right_shoulder'], ['nose', 'left_ankle']),
            'torso_to_leg_ratio': (['left_shoulder', 'left_hip'], ['left_hip', 'left_ankle']),
            'arm_to_torso_ratio': (['left_shoulder', 'left_wrist'], ['left_shoulder', 'left_hip']),
            'head_to_body_ratio': (['nose', 'left_shoulder'], ['left_shoulder', 'left_ankle']),
            'hip_width_to_height': (['left_hip', 'right_hip'], ['nose', 'left_ankle']),
            'leg_proportions': (['left_hip', 'left_knee'], ['left_knee', 'left_ankle'])
        }
        
        # VLM prompts for body shape assessment
        self.body_shape_prompts = {
            'overall_proportions': """
            Compare the overall body proportions between these two images.
            Focus on the relative sizes of head, torso, arms, and legs.
            Rate how well the body proportions are preserved from 0.0 to 1.0.
            Consider natural human proportions and consistency between images.
            """,
            'shoulder_width': """
            Compare the shoulder width relative to the overall body size in these images.
            Rate how consistent the shoulder width appears from 0.0 to 1.0.
            Focus on the shoulder-to-hip ratio and overall upper body proportions.
            """,
            'torso_length': """
            Compare the torso length (from shoulders to hips) in these two images.
            Rate how well the torso proportions are preserved from 0.0 to 1.0.
            Consider the torso-to-leg ratio and overall body balance.
            """,
            'limb_proportions': """
            Compare the arm and leg proportions between these two images.
            Rate how consistent the limb lengths and proportions are from 0.0 to 1.0.
            Focus on arm-to-torso and leg-to-torso ratios.
            """,
            'body_posture': """
            Compare the body posture and stance between these two images.
            Rate how well the overall posture is preserved from 0.0 to 1.0.
            Consider spine alignment, shoulder position, and general body positioning.
            """
        }
        
        # Pose similarity thresholds
        self.pose_thresholds = {
            'high_similarity': 0.85,
            'medium_similarity': 0.7,
            'low_similarity': 0.5
        }
        
    def _init_mediapipe_pose(self):
        """Initialize MediaPipe pose detection model."""
        try:
            self.mp_pose = mp.solutions.pose
            self.pose_detector = self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=2,  # Use highest accuracy model
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_drawing = mp.solutions.drawing_utils
            logger.info("MediaPipe pose detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MediaPipe pose detector: {e}")
            self.pose_detector = None
            self.mp_pose = None
            self.mp_drawing = None

    def extract_2d_keypoints(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract 2D keypoints using MediaPipe pose detection.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Dictionary containing keypoints, confidence scores, and metadata
        """
        results = {
            'keypoints': {},
            'keypoints_array': None,
            'confidence_scores': {},
            'pose_detected': False,
            'visibility_scores': {},
            'pose_landmarks': None
        }
        
        if self.pose_detector is None:
            logger.warning("MediaPipe pose detector not available")
            return results
        
        try:
            # Convert BGR to RGB for MediaPipe
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Process image with MediaPipe
            pose_results = self.pose_detector.process(image_rgb)
            
            if pose_results.pose_landmarks:
                results['pose_detected'] = True
                results['pose_landmarks'] = pose_results.pose_landmarks
                
                height, width = image.shape[:2]
                keypoints_array = []
                
                # Extract keypoints with confidence and visibility
                for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
                    x = landmark.x * width
                    y = landmark.y * height
                    confidence = landmark.visibility  # MediaPipe uses visibility as confidence
                    
                    keypoints_array.append([x, y, confidence])
                    
                    # Store by keypoint name if available
                    for name, kp_idx in self.body_keypoints.items():
                        if idx == kp_idx:
                            results['keypoints'][name] = (x, y)
                            results['confidence_scores'][name] = confidence
                            results['visibility_scores'][name] = landmark.visibility
                            break
                
                results['keypoints_array'] = np.array(keypoints_array)
                
                logger.debug(f"Successfully extracted {len(keypoints_array)} keypoints")
            else:
                logger.warning("No pose detected in image")
                
        except Exception as e:
            logger.error(f"2D keypoint extraction failed: {e}")
            
        return results

    def compute_body_ratios(self, keypoints: Dict[str, Tuple[float, float]]) -> Dict[str, float]:
        """
        Compute anthropometric body ratios from keypoints.
        
        Args:
            keypoints: Dictionary of keypoint names to (x, y) coordinates
            
        Returns:
            Dictionary of body ratio measurements
        """
        ratios = {}
        
        try:
            def calculate_distance(point1_name, point2_name):
                """Calculate Euclidean distance between two keypoints."""
                if point1_name in keypoints and point2_name in keypoints:
                    p1 = keypoints[point1_name]
                    p2 = keypoints[point2_name]
                    return euclidean(p1, p2)
                return None
            
            def calculate_ratio(numerator_points, denominator_points):
                """Calculate ratio between two measurements."""
                num_dist = calculate_distance(*numerator_points)
                den_dist = calculate_distance(*denominator_points)
                
                if num_dist is not None and den_dist is not None and den_dist > 0:
                    return num_dist / den_dist
                return None
            
            # Calculate all defined body ratios
            for ratio_name, (num_points, den_points) in self.body_ratio_pairs.items():
                ratio_value = calculate_ratio(num_points, den_points)
                if ratio_value is not None:
                    ratios[ratio_name] = ratio_value
            
            # Additional specific measurements
            
            # Body symmetry (left vs right side)
            left_arm_length = calculate_distance('left_shoulder', 'left_wrist')
            right_arm_length = calculate_distance('right_shoulder', 'right_wrist')
            if left_arm_length and right_arm_length:
                ratios['arm_symmetry'] = min(left_arm_length, right_arm_length) / max(left_arm_length, right_arm_length)
            
            left_leg_length = calculate_distance('left_hip', 'left_ankle')
            right_leg_length = calculate_distance('right_hip', 'right_ankle')
            if left_leg_length and right_leg_length:
                ratios['leg_symmetry'] = min(left_leg_length, right_leg_length) / max(left_leg_length, right_leg_length)
            
            # Shoulder slope
            if 'left_shoulder' in keypoints and 'right_shoulder' in keypoints:
                left_shoulder = keypoints['left_shoulder']
                right_shoulder = keypoints['right_shoulder']
                shoulder_slope = abs(left_shoulder[1] - right_shoulder[1]) / abs(left_shoulder[0] - right_shoulder[0]) if abs(left_shoulder[0] - right_shoulder[0]) > 0 else 0
                ratios['shoulder_slope'] = shoulder_slope
            
            # Hip alignment
            if 'left_hip' in keypoints and 'right_hip' in keypoints:
                left_hip = keypoints['left_hip']
                right_hip = keypoints['right_hip']
                hip_slope = abs(left_hip[1] - right_hip[1]) / abs(left_hip[0] - right_hip[0]) if abs(left_hip[0] - right_hip[0]) > 0 else 0
                ratios['hip_slope'] = hip_slope
            
            logger.debug(f"Computed {len(ratios)} body ratios")
            
        except Exception as e:
            logger.error(f"Body ratio computation failed: {e}")
            
        return ratios

    def assess_pose_similarity(self, original_keypoints: np.ndarray, generated_keypoints: np.ndarray) -> Dict[str, float]:
        """
        Assess pose similarity between original and generated images.
        
        Args:
            original_keypoints: Keypoints from original image (N x 3: x, y, confidence)
            generated_keypoints: Keypoints from generated image (N x 3: x, y, confidence)
            
        Returns:
            Dictionary with pose similarity metrics
        """
        similarity_metrics = {
            'overall_pose_similarity': 0.0,
            'upper_body_similarity': 0.0,
            'lower_body_similarity': 0.0,
            'keypoint_distance_score': 0.0,
            'angle_similarity': 0.0
        }
        
        try:
            if original_keypoints is None or generated_keypoints is None:
                return similarity_metrics
            
            if len(original_keypoints) != len(generated_keypoints):
                logger.warning("Keypoint arrays have different lengths")
                return similarity_metrics
            
            # Normalize keypoints to handle scale differences
            def normalize_keypoints(kpts):
                if len(kpts) == 0:
                    return kpts
                
                # Use shoulder width for normalization
                left_shoulder_idx = self.body_keypoints.get('left_shoulder', 11)
                right_shoulder_idx = self.body_keypoints.get('right_shoulder', 12)
                
                if left_shoulder_idx < len(kpts) and right_shoulder_idx < len(kpts):
                    shoulder_width = euclidean(kpts[left_shoulder_idx][:2], kpts[right_shoulder_idx][:2])
                    if shoulder_width > 0:
                        normalized_kpts = kpts.copy()
                        normalized_kpts[:, :2] = kpts[:, :2] / shoulder_width
                        return normalized_kpts
                
                return kpts
            
            orig_norm = normalize_keypoints(original_keypoints)
            gen_norm = normalize_keypoints(generated_keypoints)
            
            # 1. Keypoint distance similarity
            valid_points = (orig_norm[:, 2] > 0.5) & (gen_norm[:, 2] > 0.5)
            if np.sum(valid_points) > 0:
                distances = np.linalg.norm(orig_norm[valid_points, :2] - gen_norm[valid_points, :2], axis=1)
                avg_distance = np.mean(distances)
                # Convert distance to similarity (lower distance = higher similarity)
                similarity_metrics['keypoint_distance_score'] = max(0, 1.0 - avg_distance)
            
            # 2. Upper body similarity (shoulders, elbows, wrists)
            upper_body_indices = [
                self.body_keypoints.get('left_shoulder', 11),
                self.body_keypoints.get('right_shoulder', 12),
                self.body_keypoints.get('left_elbow', 13),
                self.body_keypoints.get('right_elbow', 14),
                self.body_keypoints.get('left_wrist', 15),
                self.body_keypoints.get('right_wrist', 16)
            ]
            
            upper_valid = np.array([i for i in upper_body_indices if i < len(orig_norm) and orig_norm[i, 2] > 0.5 and gen_norm[i, 2] > 0.5])
            if len(upper_valid) > 0:
                upper_distances = np.linalg.norm(orig_norm[upper_valid, :2] - gen_norm[upper_valid, :2], axis=1)
                similarity_metrics['upper_body_similarity'] = max(0, 1.0 - np.mean(upper_distances))
            
            # 3. Lower body similarity (hips, knees, ankles)
            lower_body_indices = [
                self.body_keypoints.get('left_hip', 23),
                self.body_keypoints.get('right_hip', 24),
                self.body_keypoints.get('left_knee', 25),
                self.body_keypoints.get('right_knee', 26),
                self.body_keypoints.get('left_ankle', 27),
                self.body_keypoints.get('right_ankle', 28)
            ]
            
            lower_valid = np.array([i for i in lower_body_indices if i < len(orig_norm) and orig_norm[i, 2] > 0.5 and gen_norm[i, 2] > 0.5])
            if len(lower_valid) > 0:
                lower_distances = np.linalg.norm(orig_norm[lower_valid, :2] - gen_norm[lower_valid, :2], axis=1)
                similarity_metrics['lower_body_similarity'] = max(0, 1.0 - np.mean(lower_distances))
            
            # 4. Angle similarity
            def calculate_angle(p1, p2, p3):
                """Calculate angle at p2 formed by p1-p2-p3."""
                v1 = p1 - p2
                v2 = p3 - p2
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                return np.arccos(cos_angle)
            
            # Calculate key joint angles
            angle_similarities = []
            
            # Elbow angles
            for side in ['left', 'right']:
                shoulder_idx = self.body_keypoints.get(f'{side}_shoulder')
                elbow_idx = self.body_keypoints.get(f'{side}_elbow')
                wrist_idx = self.body_keypoints.get(f'{side}_wrist')
                
                if all(idx is not None and idx < len(orig_norm) for idx in [shoulder_idx, elbow_idx, wrist_idx]):
                    if orig_norm[elbow_idx, 2] > 0.5 and gen_norm[elbow_idx, 2] > 0.5:
                        orig_angle = calculate_angle(orig_norm[shoulder_idx, :2], orig_norm[elbow_idx, :2], orig_norm[wrist_idx, :2])
                        gen_angle = calculate_angle(gen_norm[shoulder_idx, :2], gen_norm[elbow_idx, :2], gen_norm[wrist_idx, :2])
                        angle_diff = abs(orig_angle - gen_angle)
                        angle_sim = max(0, 1.0 - angle_diff / np.pi)  # Normalize by max possible difference
                        angle_similarities.append(angle_sim)
            
            # Knee angles
            for side in ['left', 'right']:
                hip_idx = self.body_keypoints.get(f'{side}_hip')
                knee_idx = self.body_keypoints.get(f'{side}_knee')
                ankle_idx = self.body_keypoints.get(f'{side}_ankle')
                
                if all(idx is not None and idx < len(orig_norm) for idx in [hip_idx, knee_idx, ankle_idx]):
                    if orig_norm[knee_idx, 2] > 0.5 and gen_norm[knee_idx, 2] > 0.5:
                        orig_angle = calculate_angle(orig_norm[hip_idx, :2], orig_norm[knee_idx, :2], orig_norm[ankle_idx, :2])
                        gen_angle = calculate_angle(gen_norm[hip_idx, :2], gen_norm[knee_idx, :2], gen_norm[ankle_idx, :2])
                        angle_diff = abs(orig_angle - gen_angle)
                        angle_sim = max(0, 1.0 - angle_diff / np.pi)
                        angle_similarities.append(angle_sim)
            
            if angle_similarities:
                similarity_metrics['angle_similarity'] = np.mean(angle_similarities)
            
            # 5. Overall pose similarity (weighted combination)
            weights = {
                'keypoint_distance_score': 0.4,
                'upper_body_similarity': 0.3,
                'lower_body_similarity': 0.2,
                'angle_similarity': 0.1
            }
            
            overall_score = sum(similarity_metrics[metric] * weight for metric, weight in weights.items())
            similarity_metrics['overall_pose_similarity'] = overall_score
            
        except Exception as e:
            logger.error(f"Pose similarity assessment failed: {e}")
            
        return similarity_metrics

    def compare_body_ratios(self, original_ratios: Dict[str, float], generated_ratios: Dict[str, float]) -> Dict[str, float]:
        """
        Compare body ratios between original and generated images.
        
        Args:
            original_ratios: Body ratios from original image
            generated_ratios: Body ratios from generated image
            
        Returns:
            Dictionary with ratio similarity scores
        """
        ratio_similarities = {}
        
        try:
            # Compare each ratio that exists in both sets
            common_ratios = set(original_ratios.keys()) & set(generated_ratios.keys())
            
            for ratio_name in common_ratios:
                orig_value = original_ratios[ratio_name]
                gen_value = generated_ratios[ratio_name]
                
                if orig_value > 0 and gen_value > 0:
                    # Calculate similarity as 1 - normalized absolute difference
                    ratio_diff = abs(orig_value - gen_value) / max(orig_value, gen_value)
                    similarity = max(0.0, 1.0 - ratio_diff)
                    ratio_similarities[f'{ratio_name}_similarity'] = similarity
            
            # Calculate overall ratio similarity
            if ratio_similarities:
                ratio_similarities['overall_ratio_similarity'] = np.mean(list(ratio_similarities.values()))
            else:
                ratio_similarities['overall_ratio_similarity'] = 0.0
                
        except Exception as e:
            logger.error(f"Body ratio comparison failed: {e}")
            ratio_similarities['overall_ratio_similarity'] = 0.0
            
        return ratio_similarities

    def vlm_body_shape_assessment(self, original: np.ndarray, generated: np.ndarray) -> Dict[str, float]:
        """
        Use VLM to assess body shape preservation from multiple perspectives.
        
        Args:
            original: Original image
            generated: Generated image
            
        Returns:
            Dictionary with VLM assessment scores
        """
        vlm_scores = {}
        
        try:
            if not self.vlm_backend.is_available():
                logger.warning("VLM backend not available, using fallback scoring")
                return {aspect: 0.7 for aspect in self.body_shape_prompts.keys()}
            
            # Evaluate different aspects of body shape preservation
            for aspect, prompt in self.body_shape_prompts.items():
                try:
                    response = self.vlm_backend.query(
                        prompt=prompt,
                        images=[original, generated],
                        max_tokens=50,
                        temperature=0.1
                    )
                    
                    # Extract numerical score from response
                    score = self._extract_score_from_response(response)
                    vlm_scores[aspect] = score
                    
                except Exception as e:
                    logger.error(f"VLM evaluation failed for {aspect}: {e}")
                    vlm_scores[aspect] = 0.5  # Neutral score for failed evaluations
            
            # Compute overall VLM body shape score
            if vlm_scores:
                vlm_scores['overall_vlm_body_shape'] = np.mean(list(vlm_scores.values()))
            else:
                vlm_scores['overall_vlm_body_shape'] = 0.5
                
        except Exception as e:
            logger.error(f"VLM body shape assessment failed: {e}")
            vlm_scores = {aspect: 0.5 for aspect in self.body_shape_prompts.keys()}
            vlm_scores['overall_vlm_body_shape'] = 0.5
            
        return vlm_scores

    def _extract_score_from_response(self, response: str) -> float:
        """
        Extract numerical score from VLM response.
        
        Args:
            response: VLM response text
            
        Returns:
            Extracted score (0.0 to 1.0)
        """
        import re
        
        try:
            # Look for decimal numbers between 0 and 1
            decimal_pattern = r'0\.\d+'
            decimal_matches = re.findall(decimal_pattern, response)
            
            if decimal_matches:
                score = float(decimal_matches[0])
                return max(0.0, min(1.0, score))
            
            # Look for percentages
            percentage_pattern = r'(\d+(?:\.\d+)?)%'
            percentage_matches = re.findall(percentage_pattern, response)
            
            if percentage_matches:
                score = float(percentage_matches[0]) / 100.0
                return max(0.0, min(1.0, score))
            
            # Look for any number that could be a score
            number_pattern = r'\b(\d+(?:\.\d+)?)\b'
            number_matches = re.findall(number_pattern, response)
            
            for match in number_matches:
                score = float(match)
                if 0.0 <= score <= 1.0:
                    return score
                elif 0 <= score <= 100:
                    return score / 100.0
            
            # Fallback: look for qualitative indicators
            response_lower = response.lower()
            if any(word in response_lower for word in ['excellent', 'perfect', 'identical']):
                return 0.9
            elif any(word in response_lower for word in ['good', 'similar', 'close']):
                return 0.7
            elif any(word in response_lower for word in ['fair', 'moderate', 'somewhat']):
                return 0.5
            elif any(word in response_lower for word in ['poor', 'different', 'dissimilar']):
                return 0.3
            else:
                return 0.5  # Neutral score if nothing found
                
        except Exception as e:
            logger.error(f"Score extraction failed: {e}")
            return 0.5

    def fit_3d_mesh(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Estimate 3D body mesh parameters (simplified version without SMPL-X).
        
        This is a placeholder implementation that would typically use SMPL-X
        for full 3D body mesh estimation. For now, it provides basic 3D pose estimation.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with 3D mesh estimation results
        """
        mesh_results = {
            'mesh_vertices': None,
            'mesh_faces': None,
            'body_parameters': {},
            'estimated_height': None,
            'estimated_measurements': {},
            'mesh_available': False
        }
        
        try:
            # Extract 2D keypoints first
            keypoint_data = self.extract_2d_keypoints(image)
            
            if keypoint_data['pose_detected']:
                keypoints = keypoint_data['keypoints']
                
                # Estimate basic body measurements from 2D keypoints
                measurements = {}
                
                # Estimate height (nose to ankle)
                if 'nose' in keypoints and 'left_ankle' in keypoints:
                    height_pixels = euclidean(keypoints['nose'], keypoints['left_ankle'])
                    # Assume average pixel-to-cm ratio (this would be calibrated in real implementation)
                    estimated_height_cm = height_pixels * 0.1  # Rough estimate
                    measurements['height'] = estimated_height_cm
                    mesh_results['estimated_height'] = estimated_height_cm
                
                # Estimate shoulder width
                if 'left_shoulder' in keypoints and 'right_shoulder' in keypoints:
                    shoulder_width_pixels = euclidean(keypoints['left_shoulder'], keypoints['right_shoulder'])
                    shoulder_width_cm = shoulder_width_pixels * 0.1
                    measurements['shoulder_width'] = shoulder_width_cm
                
                # Estimate hip width
                if 'left_hip' in keypoints and 'right_hip' in keypoints:
                    hip_width_pixels = euclidean(keypoints['left_hip'], keypoints['right_hip'])
                    hip_width_cm = hip_width_pixels * 0.1
                    measurements['hip_width'] = hip_width_cm
                
                mesh_results['estimated_measurements'] = measurements
                mesh_results['mesh_available'] = True
                
                logger.debug("Basic 3D mesh estimation completed")
            else:
                logger.warning("No pose detected for 3D mesh estimation")
                
        except Exception as e:
            logger.error(f"3D mesh estimation failed: {e}")
            
        return mesh_results

    def evaluate(self, task: EvaluationTask, generated_image: np.ndarray) -> Dict[str, float]:
        """
        Evaluate body shape preservation comprehensively.
        
        Args:
            task: Evaluation task containing original image path
            generated_image: Generated image to evaluate
            
        Returns:
            Dictionary with detailed body shape preservation scores
        """
        try:
            # Load original image
            original_image = cv2.imread(task.human_image)
            if original_image is None:
                logger.error(f"Could not load original image: {task.human_image}")
                return {"body_shape_score": 0.0}
            
            logger.info("Starting body shape evaluation...")
            
            # 1. Extract 2D keypoints from both images
            logger.debug("Extracting 2D keypoints...")
            original_keypoint_data = self.extract_2d_keypoints(original_image)
            generated_keypoint_data = self.extract_2d_keypoints(generated_image)
            
            # 2. Compute body ratios
            logger.debug("Computing body ratios...")
            original_ratios = self.compute_body_ratios(original_keypoint_data['keypoints'])
            generated_ratios = self.compute_body_ratios(generated_keypoint_data['keypoints'])
            
            # 3. Assess pose similarity
            logger.debug("Assessing pose similarity...")
            pose_similarities = self.assess_pose_similarity(
                original_keypoint_data['keypoints_array'],
                generated_keypoint_data['keypoints_array']
            )
            
            # 4. Compare body ratios
            logger.debug("Comparing body ratios...")
            ratio_similarities = self.compare_body_ratios(original_ratios, generated_ratios)
            
            # 5. VLM body shape assessment
            logger.debug("Performing VLM body shape assessment...")
            vlm_scores = self.vlm_body_shape_assessment(original_image, generated_image)
            
            # 6. 3D mesh estimation (optional)
            logger.debug("Estimating 3D mesh properties...")
            original_mesh = self.fit_3d_mesh(original_image)
            generated_mesh = self.fit_3d_mesh(generated_image)
            
            # 7. Combine scores with adaptive weighting
            pose_detected_both = (original_keypoint_data['pose_detected'] and 
                                generated_keypoint_data['pose_detected'])
            
            # Adaptive weighting based on detection confidence
            if pose_detected_both:
                pose_weight = 0.35
                ratio_weight = 0.25
                vlm_weight = 0.25
                keypoint_weight = 0.15
            else:
                # If pose detection fails, rely more on VLM
                pose_weight = 0.1
                ratio_weight = 0.1
                vlm_weight = 0.6
                keypoint_weight = 0.2
            
            # Calculate overall body shape score
            overall_score = (
                pose_similarities['overall_pose_similarity'] * pose_weight +
                ratio_similarities['overall_ratio_similarity'] * ratio_weight +
                vlm_scores['overall_vlm_body_shape'] * vlm_weight +
                pose_similarities['keypoint_distance_score'] * keypoint_weight
            )
            
            # Compile detailed results
            results = {
                "body_shape_score": float(overall_score),
                "pose_similarity": float(pose_similarities['overall_pose_similarity']),
                "upper_body_similarity": float(pose_similarities['upper_body_similarity']),
                "lower_body_similarity": float(pose_similarities['lower_body_similarity']),
                "ratio_similarity": float(ratio_similarities['overall_ratio_similarity']),
                "vlm_body_shape_score": float(vlm_scores['overall_vlm_body_shape']),
                "keypoint_distance_score": float(pose_similarities['keypoint_distance_score']),
                "angle_similarity": float(pose_similarities['angle_similarity']),
                "pose_detected_original": original_keypoint_data['pose_detected'],
                "pose_detected_generated": generated_keypoint_data['pose_detected'],
                "mesh_estimation_available": original_mesh['mesh_available'] and generated_mesh['mesh_available']
            }
            
            # Add individual ratio similarities
            for ratio_name, similarity in ratio_similarities.items():
                if ratio_name != 'overall_ratio_similarity':
                    results[f'ratio_{ratio_name}'] = float(similarity)
            
            # Add individual VLM aspect scores
            for aspect in self.body_shape_prompts.keys():
                if aspect in vlm_scores:
                    results[f'vlm_{aspect}'] = float(vlm_scores[aspect])
            
            # Add estimated measurements if available
            if original_mesh['estimated_measurements'] and generated_mesh['estimated_measurements']:
                for measurement in ['height', 'shoulder_width', 'hip_width']:
                    if measurement in original_mesh['estimated_measurements'] and measurement in generated_mesh['estimated_measurements']:
                        orig_val = original_mesh['estimated_measurements'][measurement]
                        gen_val = generated_mesh['estimated_measurements'][measurement]
                        if orig_val > 0 and gen_val > 0:
                            measurement_similarity = 1.0 - abs(orig_val - gen_val) / max(orig_val, gen_val)
                            results[f'{measurement}_similarity'] = float(measurement_similarity)
            
            logger.info(f"Body shape evaluation completed. Overall score: {overall_score:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Body shape evaluation failed: {e}")
            return {
                "body_shape_score": 0.0,
                "error": str(e)
            }
