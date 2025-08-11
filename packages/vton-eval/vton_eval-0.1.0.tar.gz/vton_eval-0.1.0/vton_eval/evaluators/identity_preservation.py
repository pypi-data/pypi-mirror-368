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
import open_clip
from deepface import DeepFace
from deepface.commons import functions
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import warnings

# Suppress DeepFace warnings
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger('deepface').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

class IdentityPreservationEvaluator(BaseEvaluator):
    """
    Evaluates how well the generated image preserves the person's identity,
    including facial features, body characteristics, and overall appearance.
    
    Uses multiple evaluation methods:
    1. Face Recognition (DeepFace with ArcFace)
    2. Visual Similarity (OpenCLIP)
    3. VLM-based Identity Assessment
    4. Pose and Body Structure Consistency
    """
    
    def __init__(self, config: VTONConfig, vlm_backend: VLMBackend):
        super().__init__(config, vlm_backend)
        
        # Initialize device
        self.device = torch.device('cpu')
        
        # Initialize face recognition models
        self.face_models = ['ArcFace', 'Facenet512', 'VGG-Face']  # Multiple models for robustness
        self.face_detectors = ['retinaface', 'mtcnn', 'opencv']  # Fallback detectors
        
        # Initialize CLIP model for visual similarity
        self._init_clip_model()
        
        # Face detection and alignment parameters
        self.face_detection_params = {
            'enforce_detection': False,  # Don't fail if no face detected
            'align': True,
            'expand_percentage': 20  # Expand face region
        }
        
        # Identity similarity thresholds
        self.similarity_thresholds = {
            'face_high': 0.7,    # High confidence face match
            'face_medium': 0.5,  # Medium confidence face match
            'clip_high': 0.85,   # High CLIP similarity
            'clip_medium': 0.7   # Medium CLIP similarity
        }
        
        # VLM prompts for identity assessment
        self.identity_prompts = {
            'face_similarity': """
            Compare the facial features of the person in these two images.
            Focus on facial structure, eye shape, nose, mouth, and overall facial appearance.
            Are these the same person? Rate the facial similarity from 0.0 to 1.0.
            Consider lighting and angle differences. Provide only the numerical score.
            """,
            'body_consistency': """
            Compare the body characteristics and posture of the person in these two images.
            Focus on body proportions, height, build, and overall physical appearance.
            Rate how consistent the person's body appears from 0.0 to 1.0.
            Ignore clothing differences and focus on the person's physical characteristics.
            """,
            'overall_identity': """
            Looking at both images, do they show the same person?
            Consider facial features, body characteristics, and overall appearance.
            Rate the overall identity preservation from 0.0 to 1.0 where 1.0 means 
            definitely the same person and 0.0 means definitely different people.
            """,
            'pose_consistency': """
            Compare the pose and positioning of the person in these two images.
            Rate how well the person's pose, stance, and body positioning are preserved.
            Focus on natural pose consistency from 0.0 to 1.0.
            """
        }
        
    def _init_clip_model(self):
        """Initialize OpenCLIP model for visual similarity."""
        try:
            # Use a robust CLIP model
            model_name = 'ViT-B-32'
            pretrained = 'laion2b_s34b_b79k'
            
            self.clip_model, _, self.clip_preprocess = open_clip.create_model_and_transforms(
                model_name, 
                pretrained=pretrained,
                device=self.device
            )
            self.clip_model.eval()
            
            # Get tokenizer
            self.clip_tokenizer = open_clip.get_tokenizer(model_name)
            
            logger.info(f"Initialized CLIP model: {model_name} with {pretrained}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CLIP model: {e}")
            self.clip_model = None
            self.clip_preprocess = None
            self.clip_tokenizer = None

    def extract_face_embeddings(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract face embeddings using multiple models for robustness.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            Dictionary containing embeddings from different models and metadata
        """
        results = {
            'embeddings': {},
            'face_detected': False,
            'face_region': None,
            'confidence': 0.0
        }
        
        try:
            # Convert BGR to RGB for DeepFace
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Try different face detection backends
            for detector in self.face_detectors:
                try:
                    # Try each face recognition model
                    for model_name in self.face_models:
                        try:
                            # Extract embedding
                            embedding_result = DeepFace.represent(
                                img_path=image_rgb,
                                model_name=model_name,
                                detector_backend=detector,
                                **self.face_detection_params
                            )
                            
                            if embedding_result and len(embedding_result) > 0:
                                # Get the first (best) face detection
                                face_data = embedding_result[0]
                                
                                results['embeddings'][model_name] = np.array(face_data['embedding'])
                                results['face_detected'] = True
                                results['face_region'] = face_data.get('facial_area', {})
                                results['confidence'] = max(results['confidence'], 0.8)  # High confidence if face found
                                
                                logger.debug(f"Successfully extracted {model_name} embedding using {detector}")
                                
                        except Exception as e:
                            logger.debug(f"Failed to extract {model_name} embedding: {e}")
                            continue
                    
                    # If we found at least one face, break
                    if results['face_detected']:
                        break
                        
                except Exception as e:
                    logger.debug(f"Face detection failed with {detector}: {e}")
                    continue
            
            if not results['face_detected']:
                logger.warning("No face detected in image")
                
        except Exception as e:
            logger.error(f"Face embedding extraction failed: {e}")
            
        return results

    def compute_face_similarity(self, original_embeddings: Dict[str, Any], 
                               generated_embeddings: Dict[str, Any]) -> Dict[str, float]:
        """
        Compute face similarity using multiple models.
        
        Args:
            original_embeddings: Face embeddings from original image
            generated_embeddings: Face embeddings from generated image
            
        Returns:
            Dictionary with similarity scores from different models
        """
        similarities = {}
        
        if not (original_embeddings['face_detected'] and generated_embeddings['face_detected']):
            logger.warning("Face not detected in one or both images")
            return {'overall_face_similarity': 0.0}
        
        try:
            # Compare embeddings from each model
            for model_name in self.face_models:
                if (model_name in original_embeddings['embeddings'] and 
                    model_name in generated_embeddings['embeddings']):
                    
                    emb1 = original_embeddings['embeddings'][model_name].reshape(1, -1)
                    emb2 = generated_embeddings['embeddings'][model_name].reshape(1, -1)
                    
                    # Compute cosine similarity
                    similarity = cosine_similarity(emb1, emb2)[0][0]
                    
                    # Convert to 0-1 range (cosine similarity is -1 to 1)
                    similarity = (similarity + 1) / 2
                    
                    similarities[f'{model_name}_similarity'] = float(similarity)
            
            # Compute overall face similarity (weighted average)
            if similarities:
                # Weight ArcFace higher as it's generally more robust
                weights = {'ArcFace_similarity': 0.5, 'Facenet512_similarity': 0.3, 'VGG-Face_similarity': 0.2}
                
                weighted_sum = 0.0
                total_weight = 0.0
                
                for sim_name, sim_value in similarities.items():
                    weight = weights.get(sim_name, 0.33)  # Equal weight if not specified
                    weighted_sum += sim_value * weight
                    total_weight += weight
                
                similarities['overall_face_similarity'] = weighted_sum / total_weight if total_weight > 0 else 0.0
            else:
                similarities['overall_face_similarity'] = 0.0
                
        except Exception as e:
            logger.error(f"Face similarity computation failed: {e}")
            similarities['overall_face_similarity'] = 0.0
            
        return similarities

    def compute_clip_similarity(self, original: np.ndarray, generated: np.ndarray) -> float:
        """
        Compute visual similarity using CLIP embeddings.
        
        Args:
            original: Original image
            generated: Generated image
            
        Returns:
            CLIP similarity score (0.0 to 1.0)
        """
        if self.clip_model is None:
            logger.warning("CLIP model not available")
            return 0.5  # Neutral score
        
        try:
            # Convert BGR to RGB and create PIL images
            original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
            generated_rgb = cv2.cvtColor(generated, cv2.COLOR_BGR2RGB)
            
            original_pil = Image.fromarray(original_rgb)
            generated_pil = Image.fromarray(generated_rgb)
            
            # Preprocess images
            original_tensor = self.clip_preprocess(original_pil).unsqueeze(0).to(self.device)
            generated_tensor = self.clip_preprocess(generated_pil).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Get image features
                original_features = self.clip_model.encode_image(original_tensor)
                generated_features = self.clip_model.encode_image(generated_tensor)
                
                # Normalize features
                original_features = original_features / original_features.norm(dim=-1, keepdim=True)
                generated_features = generated_features / generated_features.norm(dim=-1, keepdim=True)
                
                # Compute cosine similarity
                similarity = torch.cosine_similarity(original_features, generated_features, dim=-1)
                
                # Convert to 0-1 range
                similarity = (similarity + 1) / 2
                
                return float(similarity.cpu().item())
                
        except Exception as e:
            logger.error(f"CLIP similarity computation failed: {e}")
            return 0.5

    def vlm_identity_check(self, original: np.ndarray, generated: np.ndarray) -> Dict[str, float]:
        """
        Use VLM to assess identity preservation from multiple perspectives.
        
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
                return {aspect: 0.7 for aspect in self.identity_prompts.keys()}
            
            # Evaluate different aspects of identity preservation
            for aspect, prompt in self.identity_prompts.items():
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
            
            # Compute overall VLM identity score
            if vlm_scores:
                vlm_scores['overall_vlm_identity'] = np.mean(list(vlm_scores.values()))
            else:
                vlm_scores['overall_vlm_identity'] = 0.5
                
        except Exception as e:
            logger.error(f"VLM identity assessment failed: {e}")
            vlm_scores = {aspect: 0.5 for aspect in self.identity_prompts.keys()}
            vlm_scores['overall_vlm_identity'] = 0.5
            
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

    def assess_pose_consistency(self, original: np.ndarray, generated: np.ndarray) -> float:
        """
        Assess pose and body positioning consistency using simple image analysis.
        
        Args:
            original: Original image
            generated: Generated image
            
        Returns:
            Pose consistency score (0.0 to 1.0)
        """
        try:
            # Simple pose assessment using image moments and contours
            def get_pose_features(image):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Edge detection
                edges = cv2.Canny(gray, 50, 150)
                
                # Find contours
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if not contours:
                    return None
                
                # Get largest contour (likely the person)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Calculate moments
                moments = cv2.moments(largest_contour)
                
                if moments['m00'] == 0:
                    return None
                
                # Centroid
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
                
                # Contour area and perimeter
                area = cv2.contourArea(largest_contour)
                perimeter = cv2.arcLength(largest_contour, True)
                
                # Bounding rectangle
                x, y, w, h = cv2.boundingRect(largest_contour)
                aspect_ratio = w / h if h > 0 else 0
                
                return {
                    'centroid': (cx, cy),
                    'area': area,
                    'perimeter': perimeter,
                    'aspect_ratio': aspect_ratio,
                    'bounding_rect': (x, y, w, h)
                }
            
            # Get pose features for both images
            original_features = get_pose_features(original)
            generated_features = get_pose_features(generated)
            
            if original_features is None or generated_features is None:
                return 0.5  # Neutral score if pose detection fails
            
            # Compare features
            height, width = original.shape[:2]
            
            # Centroid similarity (normalized by image size)
            centroid_diff = np.sqrt(
                ((original_features['centroid'][0] - generated_features['centroid'][0]) / width) ** 2 +
                ((original_features['centroid'][1] - generated_features['centroid'][1]) / height) ** 2
            )
            centroid_similarity = max(0, 1 - centroid_diff * 2)  # Scale difference
            
            # Aspect ratio similarity
            aspect_diff = abs(original_features['aspect_ratio'] - generated_features['aspect_ratio'])
            aspect_similarity = max(0, 1 - aspect_diff)
            
            # Area similarity (normalized)
            area_ratio = min(original_features['area'], generated_features['area']) / max(original_features['area'], generated_features['area'])
            
            # Combine similarities
            pose_score = (centroid_similarity * 0.4 + aspect_similarity * 0.3 + area_ratio * 0.3)
            
            return float(pose_score)
            
        except Exception as e:
            logger.error(f"Pose consistency assessment failed: {e}")
            return 0.5

    def evaluate(self, task: EvaluationTask, generated_image: np.ndarray) -> Dict[str, float]:
        """
        Evaluate identity preservation comprehensively.
        
        Args:
            task: Evaluation task containing original image path
            generated_image: Generated image to evaluate
            
        Returns:
            Dictionary with detailed identity preservation scores
        """
        try:
            # Load original image
            original_image = cv2.imread(task.human_image)
            if original_image is None:
                logger.error(f"Could not load original image: {task.human_image}")
                return {"identity_preservation_score": 0.0}
            
            logger.info("Starting identity preservation evaluation...")
            
            # 1. Face Recognition Analysis
            logger.debug("Extracting face embeddings...")
            original_face_data = self.extract_face_embeddings(original_image)
            generated_face_data = self.extract_face_embeddings(generated_image)
            
            face_similarities = self.compute_face_similarity(original_face_data, generated_face_data)
            
            # 2. CLIP Visual Similarity
            logger.debug("Computing CLIP similarity...")
            clip_similarity = self.compute_clip_similarity(original_image, generated_image)
            
            # 3. VLM Identity Assessment
            logger.debug("Performing VLM identity assessment...")
            vlm_scores = self.vlm_identity_check(original_image, generated_image)
            
            # 4. Pose Consistency
            logger.debug("Assessing pose consistency...")
            pose_consistency = self.assess_pose_consistency(original_image, generated_image)
            
            # 5. Combine scores with weights
            face_score = face_similarities.get('overall_face_similarity', 0.0)
            vlm_score = vlm_scores.get('overall_vlm_identity', 0.5)
            
            # Adaptive weighting based on face detection confidence
            face_weight = 0.4 if original_face_data['face_detected'] and generated_face_data['face_detected'] else 0.1
            clip_weight = 0.3
            vlm_weight = 0.2
            pose_weight = 0.1
            
            # Normalize weights
            total_weight = face_weight + clip_weight + vlm_weight + pose_weight
            face_weight /= total_weight
            clip_weight /= total_weight
            vlm_weight /= total_weight
            pose_weight /= total_weight
            
            # Calculate overall identity preservation score
            overall_score = (
                face_score * face_weight +
                clip_similarity * clip_weight +
                vlm_score * vlm_weight +
                pose_consistency * pose_weight
            )
            
            # Compile detailed results
            results = {
                "identity_preservation_score": float(overall_score),
                "face_similarity": float(face_score),
                "clip_similarity": float(clip_similarity),
                "vlm_identity_score": float(vlm_score),
                "pose_consistency": float(pose_consistency),
                "face_detected_original": original_face_data['face_detected'],
                "face_detected_generated": generated_face_data['face_detected'],
                "face_confidence": float((original_face_data['confidence'] + generated_face_data['confidence']) / 2)
            }
            
            # Add individual face model scores
            for model_name in self.face_models:
                score_key = f'{model_name}_similarity'
                if score_key in face_similarities:
                    results[score_key.lower()] = float(face_similarities[score_key])
            
            # Add individual VLM aspect scores
            for aspect in self.identity_prompts.keys():
                if aspect in vlm_scores:
                    results[f'vlm_{aspect}'] = float(vlm_scores[aspect])
            
            logger.info(f"Identity preservation evaluation completed. Overall score: {overall_score:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Identity preservation evaluation failed: {e}")
            return {
                "identity_preservation_score": 0.0,
                "error": str(e)
            }
