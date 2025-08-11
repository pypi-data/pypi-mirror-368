from vton_eval.evaluators.base import BaseEvaluator
from vton_eval.core.config import VTONConfig
from vton_eval.core.data_models import EvaluationTask
from vton_eval.vlm.base import VLMBackend
from vton_eval.models.sam_wrapper import SAMWrapper
import numpy as np
import torch
import cv2
from typing import Dict, List, Optional, Tuple
from torchmetrics.image.lpip import LearnedPerceptualImagePatchSimilarity
from torchvision import transforms
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class GarmentPreservationEvaluator(BaseEvaluator):
    """
    Evaluates how well the generated image preserves the garment's appearance,
    texture, color, and semantic attributes from the reference garment image.
    """
    
    def __init__(self, config: VTONConfig, vlm_backend: VLMBackend):
        super().__init__(config, vlm_backend)
        
        # Initialize model wrappers
        model_configs = config.get_model_paths()
        self.sam_model = SAMWrapper(model_configs.get('sam', {}))
        
        # Initialize LPIPS model using torchmetrics
        self.device = torch.device('cpu')
        self.lpips_model = LearnedPerceptualImagePatchSimilarity(
            net_type='alex',  # 'alex', 'vgg', or 'squeeze' - alex is good balance of speed/accuracy
            reduction='mean',
            normalize=True  # Expects input in [0,1] range
        ).to(self.device)
        
        # Image preprocessing transforms
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ])
        
        # Garment categories for segmentation
        self.garment_categories = {
            'shirt': ['shirt', 'blouse', 'top', 'sweater', 'jacket'],
            'pants': ['pants', 'trousers', 'jeans', 'shorts'],
            'dress': ['dress', 'gown', 'skirt'],
            'outerwear': ['coat', 'jacket', 'blazer', 'cardigan']
        }
        
        # VLM prompts for semantic evaluation
        self.semantic_prompts = {
            'color_preservation': """
            Compare the color of the garment in these two images. 
            Rate how well the color is preserved from the reference to the generated image.
            Focus on hue, saturation, and brightness consistency.
            Provide a score from 0.0 to 1.0 where 1.0 means perfect color preservation.
            """,
            'texture_preservation': """
            Compare the texture and fabric appearance of the garment in these two images.
            Rate how well the texture details, fabric patterns, and surface properties are preserved.
            Provide a score from 0.0 to 1.0 where 1.0 means perfect texture preservation.
            """,
            'pattern_preservation': """
            Compare any patterns, prints, or designs on the garment in these two images.
            Rate how well patterns, logos, text, or decorative elements are preserved.
            Provide a score from 0.0 to 1.0 where 1.0 means perfect pattern preservation.
            """,
            'overall_appearance': """
            Compare the overall visual appearance of the garment in these two images.
            Consider shape, style, design elements, and general visual fidelity.
            Provide a score from 0.0 to 1.0 where 1.0 means the garments look identical.
            """
        }
    
    def segment_garment(self, image: np.ndarray, category: str = "clothing") -> np.ndarray:
        """
        Segment the garment from the image using SAM.
        
        Args:
            image: Input image as numpy array (H, W, 3)
            category: Garment category for targeted segmentation
            
        Returns:
            Binary mask of the segmented garment (H, W)
        """
        try:
            if not self.sam_model.is_loaded():
                self.sam_model.load_model()
            
            # Use SAM to segment the garment
            mask = self.sam_model.segment_garment(image, category)
            
            if mask is None or mask.size == 0:
                logger.warning("SAM segmentation failed, using fallback method")
                # Fallback: simple color-based segmentation for clothing
                mask = self._fallback_garment_segmentation(image)
            
            return mask
            
        except Exception as e:
            logger.error(f"Garment segmentation failed: {e}")
            # Return a mask covering the center region as last resort
            h, w = image.shape[:2]
            mask = np.zeros((h, w), dtype=np.uint8)
            mask[h//4:3*h//4, w//4:3*w//4] = 1
            return mask
    
    def _fallback_garment_segmentation(self, image: np.ndarray) -> np.ndarray:
        """
        Fallback segmentation method using color and edge detection.
        """
        # Convert to different color spaces for better segmentation
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        
        # Apply GrabCut algorithm for foreground extraction
        height, width = image.shape[:2]
        mask = np.zeros((height, width), np.uint8)
        
        # Define rectangle around center region (likely garment area)
        rect = (width//6, height//6, 2*width//3, 2*height//3)
        
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        
        try:
            cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            return mask2
        except:
            # If GrabCut fails, return center region mask
            mask = np.zeros((height, width), dtype=np.uint8)
            mask[height//4:3*height//4, width//4:3*width//4] = 1
            return mask
    
    def compute_appearance_similarity(self, generated: np.ndarray, reference: np.ndarray) -> Dict[str, float]:
        """
        Compute appearance similarity between generated and reference garment regions.
        
        Args:
            generated: Generated image with garment
            reference: Reference garment image
            
        Returns:
            Dictionary with similarity scores
        """
        try:
            # Segment garments in both images
            gen_mask = self.segment_garment(generated)
            ref_mask = self.segment_garment(reference)
            
            # Extract garment regions
            gen_garment = self._extract_garment_region(generated, gen_mask)
            ref_garment = self._extract_garment_region(reference, ref_mask)
            
            # Convert to PIL Images and then to tensors
            gen_pil = Image.fromarray(gen_garment.astype(np.uint8))
            ref_pil = Image.fromarray(ref_garment.astype(np.uint8))
            
            gen_tensor = self.transform(gen_pil).unsqueeze(0).to(self.device)
            ref_tensor = self.transform(ref_pil).unsqueeze(0).to(self.device)
            
            # Compute LPIPS score (lower is better, so we invert it)
            with torch.no_grad():
                lpips_score = self.lpips_model(gen_tensor, ref_tensor).item()
                # Convert to similarity score (higher is better)
                lpips_similarity = max(0.0, 1.0 - lpips_score)
            
            # Compute additional pixel-level metrics
            color_similarity = self._compute_color_similarity(gen_garment, ref_garment)
            texture_similarity = self._compute_texture_similarity(gen_garment, ref_garment)
            
            return {
                'lpips_similarity': lpips_similarity,
                'color_similarity': color_similarity,
                'texture_similarity': texture_similarity,
                'overall_appearance': (lpips_similarity + color_similarity + texture_similarity) / 3.0
            }
            
        except Exception as e:
            logger.error(f"Appearance similarity computation failed: {e}")
            return {
                'lpips_similarity': 0.0,
                'color_similarity': 0.0,
                'texture_similarity': 0.0,
                'overall_appearance': 0.0
            }
    
    def _extract_garment_region(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Extract garment region using the provided mask."""
        # Apply mask to extract garment region
        masked_image = image.copy()
        
        # Create 3-channel mask
        if len(mask.shape) == 2:
            mask_3d = np.stack([mask, mask, mask], axis=2)
        else:
            mask_3d = mask
        
        # Apply mask
        masked_image = masked_image * mask_3d
        
        # Find bounding box of the masked region
        coords = np.argwhere(mask > 0)
        if len(coords) == 0:
            return image  # Return original if no mask
        
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        # Extract and resize the region
        garment_region = masked_image[y_min:y_max+1, x_min:x_max+1]
        
        # Resize to standard size for comparison
        if garment_region.size > 0:
            garment_region = cv2.resize(garment_region, (256, 256))
        else:
            garment_region = cv2.resize(image, (256, 256))
        
        return garment_region
    
    def _compute_color_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compute color similarity using histogram comparison."""
        try:
            # Convert to LAB color space for perceptual color comparison
            lab1 = cv2.cvtColor(img1, cv2.COLOR_RGB2LAB)
            lab2 = cv2.cvtColor(img2, cv2.COLOR_RGB2LAB)
            
            # Compute histograms for each channel
            hist1_l = cv2.calcHist([lab1], [0], None, [256], [0, 256])
            hist1_a = cv2.calcHist([lab1], [1], None, [256], [0, 256])
            hist1_b = cv2.calcHist([lab1], [2], None, [256], [0, 256])
            
            hist2_l = cv2.calcHist([lab2], [0], None, [256], [0, 256])
            hist2_a = cv2.calcHist([lab2], [1], None, [256], [0, 256])
            hist2_b = cv2.calcHist([lab2], [2], None, [256], [0, 256])
            
            # Compute correlation for each channel
            corr_l = cv2.compareHist(hist1_l, hist2_l, cv2.HISTCMP_CORREL)
            corr_a = cv2.compareHist(hist1_a, hist2_a, cv2.HISTCMP_CORREL)
            corr_b = cv2.compareHist(hist1_b, hist2_b, cv2.HISTCMP_CORREL)
            
            # Average correlation across channels
            color_similarity = (corr_l + corr_a + corr_b) / 3.0
            return max(0.0, color_similarity)
            
        except Exception as e:
            logger.error(f"Color similarity computation failed: {e}")
            return 0.0
    
    def _compute_texture_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Compute texture similarity using Local Binary Patterns."""
        try:
            from skimage.feature import local_binary_pattern
            from scipy.spatial.distance import cosine
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY) if len(img1.shape) == 3 else img1
            gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY) if len(img2.shape) == 3 else img2
            
            # Compute LBP
            radius = 3
            n_points = 8 * radius
            lbp1 = local_binary_pattern(gray1, n_points, radius, method='uniform')
            lbp2 = local_binary_pattern(gray2, n_points, radius, method='uniform')
            
            # Compute histograms
            hist1, _ = np.histogram(lbp1.ravel(), bins=n_points + 2, range=(0, n_points + 2))
            hist2, _ = np.histogram(lbp2.ravel(), bins=n_points + 2, range=(0, n_points + 2))
            
            # Normalize histograms
            hist1 = hist1.astype(float)
            hist2 = hist2.astype(float)
            hist1 /= (hist1.sum() + 1e-8)
            hist2 /= (hist2.sum() + 1e-8)
            
            # Compute cosine similarity
            similarity = 1 - cosine(hist1, hist2)
            return max(0.0, similarity)
            
        except Exception as e:
            logger.error(f"Texture similarity computation failed: {e}")
            return 0.0
    
    def evaluate_semantic_attributes(self, generated: np.ndarray, reference: np.ndarray) -> float:
        """
        Evaluate semantic attributes using VLM.
        
        Args:
            generated: Generated image with garment
            reference: Reference garment image
            
        Returns:
            Semantic similarity score (0.0 to 1.0)
        """
        try:
            if not self.vlm_backend.is_available():
                logger.warning("VLM backend not available, using fallback scoring")
                return 0.7  # Fallback score
            
            semantic_scores = []
            
            # Evaluate different semantic aspects
            for aspect, prompt in self.semantic_prompts.items():
                try:
                    response = self.vlm_backend.query(
                        prompt=prompt,
                        images=[reference, generated],
                        max_tokens=50,
                        temperature=0.1
                    )
                    
                    # Extract numerical score from response
                    score = self._extract_score_from_response(response)
                    semantic_scores.append(score)
                    
                except Exception as e:
                    logger.error(f"VLM evaluation failed for {aspect}: {e}")
                    semantic_scores.append(0.5)  # Neutral score for failed evaluations
            
            # Return average semantic score
            return np.mean(semantic_scores) if semantic_scores else 0.5
            
        except Exception as e:
            logger.error(f"Semantic evaluation failed: {e}")
            return 0.5
    
    def _extract_score_from_response(self, response: str) -> float:
        """Extract numerical score from VLM response."""
        import re
        
        # Look for decimal numbers between 0 and 1
        pattern = r'(?:score|rating)?\s*:?\s*([0-1](?:\.[0-9]+)?)'
        matches = re.findall(pattern, response.lower())
        
        if matches:
            try:
                score = float(matches[0])
                return max(0.0, min(1.0, score))
            except ValueError:
                pass
        
        # Fallback: look for percentages
        pattern = r'([0-9]{1,3})%'
        matches = re.findall(pattern, response)
        if matches:
            try:
                score = float(matches[0]) / 100.0
                return max(0.0, min(1.0, score))
            except ValueError:
                pass
        
        # Default neutral score if no valid score found
        return 0.5
    
    def evaluate(self, task: EvaluationTask, generated_image: np.ndarray) -> Dict[str, float]:
        """
        Main evaluation method for garment preservation.
        
        Args:
            task: Evaluation task containing reference garment image path
            generated_image: Generated VTON image as numpy array
            
        Returns:
            Dictionary with garment preservation scores
        """
        try:
            # Load reference garment image
            reference_image = self._load_image(task.garment_image)
            if reference_image is None:
                logger.error(f"Failed to load reference garment image: {task.garment_image}")
                return {"garment_preservation_score": 0.0}
            
            # Compute appearance similarity metrics
            appearance_scores = self.compute_appearance_similarity(generated_image, reference_image)
            
            # Evaluate semantic attributes using VLM
            semantic_score = self.evaluate_semantic_attributes(generated_image, reference_image)
            
            # Combine scores with weights
            weights = {
                'lpips_similarity': 0.3,
                'color_similarity': 0.2,
                'texture_similarity': 0.2,
                'semantic_score': 0.3
            }
            
            # Calculate overall garment preservation score
            overall_score = (
                appearance_scores['lpips_similarity'] * weights['lpips_similarity'] +
                appearance_scores['color_similarity'] * weights['color_similarity'] +
                appearance_scores['texture_similarity'] * weights['texture_similarity'] +
                semantic_score * weights['semantic_score']
            )
            
            # Return detailed scores
            result = {
                'garment_preservation_score': overall_score,
                'lpips_similarity': appearance_scores['lpips_similarity'],
                'color_similarity': appearance_scores['color_similarity'],
                'texture_similarity': appearance_scores['texture_similarity'],
                'semantic_score': semantic_score,
                'overall_appearance': appearance_scores['overall_appearance']
            }
            
            logger.info(f"Garment preservation evaluation completed. Overall score: {overall_score:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Garment preservation evaluation failed: {e}")
            return {"garment_preservation_score": 0.0}
    
    def _load_image(self, image_path: str) -> Optional[np.ndarray]:
        """Load image from file path."""
        try:
            image = cv2.imread(image_path)
            if image is not None:
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return image
            else:
                logger.error(f"Failed to load image: {image_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
