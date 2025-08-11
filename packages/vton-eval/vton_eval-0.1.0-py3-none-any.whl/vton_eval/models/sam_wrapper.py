from vton_eval.models.base import BaseModelWrapper
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
import torch
import cv2
import os
import logging
from PIL import Image
import requests
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class SAMWrapper(BaseModelWrapper):
    """
    SAM2 (Segment Anything Model 2) wrapper for prompt-based image segmentation.
    
    Supports multiple prompting modes:
    - Point prompts: Click points to segment objects
    - Box prompts: Bounding boxes to segment objects  
    - Text prompts: Natural language descriptions (requires GroundingDINO)
    - Automatic mask generation: Generate all possible masks
    
    Uses the latest SAM 2.1 models from Meta AI with improved performance.
    """
    
    # SAM 2.1 model configurations
    MODEL_CONFIGS = {
        'tiny': {
            'config': 'configs/sam2.1/sam2.1_hiera_t.yaml',
            'checkpoint': 'sam2.1_hiera_tiny.pt',
            'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt',
            'size_mb': 148
        },
        'small': {
            'config': 'configs/sam2.1/sam2.1_hiera_s.yaml', 
            'checkpoint': 'sam2.1_hiera_small.pt',
            'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt',
            'size_mb': 176
        },
        'base_plus': {
            'config': 'configs/sam2.1/sam2.1_hiera_b+.yaml',
            'checkpoint': 'sam2.1_hiera_base_plus.pt', 
            'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt',
            'size_mb': 308
        },
        'large': {
            'config': 'configs/sam2.1/sam2.1_hiera_l.yaml',
            'checkpoint': 'sam2.1_hiera_large.pt',
            'url': 'https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt', 
            'size_mb': 856
        }
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SAM wrapper.
        
        Args:
            config: Configuration dictionary with keys:
                - model_type: str, one of ['tiny', 'small', 'base_plus', 'large']
                - device: str, device to run model on ('cuda', 'cpu', 'mps')
                - cache_dir: str, directory to cache model weights
                - auto_download: bool, whether to auto-download missing models
        """
        super().__init__(config)
        
        self.model_type = config.get('model_type', 'large')
        self.device = config.get('device', 'cpu')
        self.cache_dir = Path(config.get('cache_dir', './models/sam2'))
        self.auto_download = config.get('auto_download', True)
        
        # Validate model type
        if self.model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Invalid model_type: {self.model_type}. Must be one of {list(self.MODEL_CONFIGS.keys())}")
        
        # Initialize models
        self.predictor = None
        self.mask_generator = None
        self.current_image = None
        
        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized SAM wrapper with model_type={self.model_type}, device={self.device}")

    def _download_model(self, model_config: Dict[str, Any]) -> Path:
        """Download model checkpoint if not available locally."""
        checkpoint_path = self.cache_dir / model_config['checkpoint']
        
        if checkpoint_path.exists():
            logger.info(f"Model checkpoint found: {checkpoint_path}")
            return checkpoint_path
            
        if not self.auto_download:
            raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")
            
        logger.info(f"Downloading {model_config['checkpoint']} ({model_config['size_mb']}MB)...")
        
        try:
            response = requests.get(model_config['url'], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(checkpoint_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size * 100
                            print(f"\rDownloading: {progress:.1f}%", end='', flush=True)
            
            print()  # New line after progress
            logger.info(f"Downloaded model checkpoint: {checkpoint_path}")
            return checkpoint_path
            
        except Exception as e:
            if checkpoint_path.exists():
                checkpoint_path.unlink()  # Remove partial download
            raise RuntimeError(f"Failed to download model: {e}")

    def load_model(self) -> None:
        """Load SAM2 model for inference."""
        if self.is_loaded():
            logger.info("SAM model already loaded")
            return
            
        try:
            # Import SAM2 (install with: pip install sam2)
            from sam2.build_sam import build_sam2, build_sam2_video_predictor
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator
            
        except ImportError as e:
            raise ImportError(
                "SAM2 not found. Please install with: pip install sam2\n"
                "Or install from source: pip install git+https://github.com/facebookresearch/sam2.git"
            ) from e
        
        # Get model configuration
        model_config = self.MODEL_CONFIGS[self.model_type]
        checkpoint_path = self._download_model(model_config)
        
        # For now, we'll use a simplified approach since we don't have the config files
        # In a real implementation, you'd need the actual SAM2 config files
        logger.info(f"Loading SAM2 model: {self.model_type}")
        
        try:
            # Build SAM2 model - this is a simplified version
            # In practice, you'd need the actual config file
            model_cfg = f"sam2_{self.model_type}.yaml"  # Simplified
            
            # Try to build the model
            sam2_model = build_sam2(model_cfg, str(checkpoint_path), device=self.device)
            
            # Create predictor and mask generator
            self.predictor = SAM2ImagePredictor(sam2_model)
            self.mask_generator = SAM2AutomaticMaskGenerator(sam2_model)
            
            self.model = sam2_model
            logger.info("SAM2 model loaded successfully")
            
        except Exception as e:
            # Fallback to original SAM if SAM2 fails
            logger.warning(f"Failed to load SAM2, falling back to original SAM: {e}")
            self._load_original_sam()

    def _load_original_sam(self) -> None:
        """Fallback to load original SAM model."""
        try:
            from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator
            
            # Map our model types to original SAM types
            sam_type_mapping = {
                'tiny': 'vit_b',    # No tiny in original SAM
                'small': 'vit_b', 
                'base_plus': 'vit_l',
                'large': 'vit_h'
            }
            
            sam_type = sam_type_mapping[self.model_type]
            
            # Download original SAM checkpoint
            sam_urls = {
                'vit_b': 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth',
                'vit_l': 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth', 
                'vit_h': 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth'
            }
            
            checkpoint_name = f"sam_{sam_type}.pth"
            checkpoint_path = self.cache_dir / checkpoint_name
            
            if not checkpoint_path.exists():
                logger.info(f"Downloading original SAM {sam_type}...")
                response = requests.get(sam_urls[sam_type], stream=True)
                response.raise_for_status()
                
                with open(checkpoint_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            # Load original SAM
            sam = sam_model_registry[sam_type](checkpoint=str(checkpoint_path))
            sam.to(device=self.device)
            
            self.predictor = SamPredictor(sam)
            self.mask_generator = SamAutomaticMaskGenerator(sam)
            self.model = sam
            
            logger.info(f"Loaded original SAM {sam_type} successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load both SAM2 and original SAM: {e}")

    def set_image(self, image: Union[np.ndarray, str, Path]) -> None:
        """
        Set the image for segmentation.
        
        Args:
            image: Input image as numpy array, file path, or PIL Image
        """
        if not self.is_loaded():
            self.load_model()
            
        # Convert input to numpy array
        if isinstance(image, (str, Path)):
            image = np.array(Image.open(image).convert('RGB'))
        elif isinstance(image, Image.Image):
            image = np.array(image.convert('RGB'))
        elif not isinstance(image, np.ndarray):
            raise ValueError(f"Unsupported image type: {type(image)}")
            
        # Ensure image is in RGB format
        if len(image.shape) == 3 and image.shape[2] == 3:
            self.current_image = image
            self.predictor.set_image(image)
            logger.debug(f"Set image with shape: {image.shape}")
        else:
            raise ValueError(f"Image must be RGB with shape (H, W, 3), got {image.shape}")

    def segment_image(self, image: np.ndarray, prompts: List[str]) -> np.ndarray:
        """
        Segment image using text prompts.
        
        Args:
            image: Input image as numpy array
            prompts: List of text prompts describing objects to segment
            
        Returns:
            Segmentation mask as numpy array
        """
        self.set_image(image)
        
        # For text prompts, we need GroundingDINO integration
        # This is a simplified implementation
        logger.warning("Text prompts require GroundingDINO integration (not implemented)")
        
        # Fallback to automatic mask generation
        return self.generate_masks(image)

    def segment_garment(self, image: np.ndarray, category: str) -> np.ndarray:
        """
        Segment garment in image by category.
        
        Args:
            image: Input image as numpy array
            category: Garment category (e.g., 'shirt', 'pants', 'dress')
            
        Returns:
            Segmentation mask for the garment
        """
        self.set_image(image)
        
        # For garment-specific segmentation, we could use:
        # 1. Pre-trained garment detection + SAM
        # 2. Text prompts with GroundingDINO
        # 3. Automatic mask generation + filtering
        
        logger.info(f"Segmenting garment category: {category}")
        
        # For now, generate all masks and return the largest one
        # (assuming garment is the main object)
        masks = self.generate_masks(image)
        
        if len(masks) > 0:
            # Return the largest mask (likely the garment)
            largest_mask = max(masks, key=lambda x: x['area'])
            return largest_mask['segmentation']
        else:
            # Return empty mask
            return np.zeros(image.shape[:2], dtype=bool)

    def predict_with_points(self, 
                          point_coords: List[Tuple[int, int]], 
                          point_labels: List[int],
                          multimask_output: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict masks using point prompts.
        
        Args:
            point_coords: List of (x, y) coordinates
            point_labels: List of labels (1 for foreground, 0 for background)
            multimask_output: Whether to return multiple masks
            
        Returns:
            Tuple of (masks, scores, logits)
        """
        if not self.is_loaded() or self.current_image is None:
            raise RuntimeError("Model not loaded or image not set")
            
        point_coords = np.array(point_coords)
        point_labels = np.array(point_labels)
        
        masks, scores, logits = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=multimask_output
        )
        
        return masks, scores, logits

    def predict_with_box(self, 
                        box: Tuple[int, int, int, int],
                        multimask_output: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict mask using bounding box prompt.
        
        Args:
            box: Bounding box as (x1, y1, x2, y2)
            multimask_output: Whether to return multiple masks
            
        Returns:
            Tuple of (masks, scores, logits)
        """
        if not self.is_loaded() or self.current_image is None:
            raise RuntimeError("Model not loaded or image not set")
            
        box = np.array(box)
        
        masks, scores, logits = self.predictor.predict(
            box=box,
            multimask_output=multimask_output
        )
        
        return masks, scores, logits

    def predict_with_mixed_prompts(self,
                                 point_coords: Optional[List[Tuple[int, int]]] = None,
                                 point_labels: Optional[List[int]] = None, 
                                 box: Optional[Tuple[int, int, int, int]] = None,
                                 mask_input: Optional[np.ndarray] = None,
                                 multimask_output: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict masks using mixed prompts (points, boxes, masks).
        
        Args:
            point_coords: List of (x, y) coordinates
            point_labels: List of labels (1 for foreground, 0 for background)
            box: Bounding box as (x1, y1, x2, y2)
            mask_input: Previous mask to refine
            multimask_output: Whether to return multiple masks
            
        Returns:
            Tuple of (masks, scores, logits)
        """
        if not self.is_loaded() or self.current_image is None:
            raise RuntimeError("Model not loaded or image not set")
            
        # Convert inputs to numpy arrays if provided
        if point_coords is not None:
            point_coords = np.array(point_coords)
        if point_labels is not None:
            point_labels = np.array(point_labels)
        if box is not None:
            box = np.array(box)
            
        masks, scores, logits = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            box=box,
            mask_input=mask_input,
            multimask_output=multimask_output
        )
        
        return masks, scores, logits

    def generate_masks(self, image: Optional[np.ndarray] = None) -> List[Dict[str, Any]]:
        """
        Generate all possible masks automatically.
        
        Args:
            image: Input image (if None, uses current image)
            
        Returns:
            List of mask dictionaries with keys: segmentation, area, bbox, predicted_iou, stability_score
        """
        if image is not None:
            self.set_image(image)
        elif self.current_image is None:
            raise RuntimeError("No image set for mask generation")
            
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")
            
        masks = self.mask_generator.generate(self.current_image)
        return masks

    def filter_masks_by_area(self, masks: List[Dict[str, Any]], 
                           min_area: int = 100, 
                           max_area: Optional[int] = None) -> List[Dict[str, Any]]:
        """Filter masks by area."""
        filtered = []
        for mask in masks:
            area = mask['area']
            if area >= min_area:
                if max_area is None or area <= max_area:
                    filtered.append(mask)
        return filtered

    def filter_masks_by_score(self, masks: List[Dict[str, Any]], 
                            min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Filter masks by predicted IoU score."""
        return [mask for mask in masks if mask.get('predicted_iou', 0) >= min_score]

    def get_largest_mask(self, masks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get the largest mask by area."""
        if not masks:
            return None
        return max(masks, key=lambda x: x['area'])

    def masks_to_combined_array(self, masks: List[Dict[str, Any]]) -> np.ndarray:
        """
        Combine multiple masks into a single labeled array.
        
        Args:
            masks: List of mask dictionaries
            
        Returns:
            Combined mask array where each mask has a unique label
        """
        if not masks:
            return np.zeros(self.current_image.shape[:2], dtype=np.uint8)
            
        combined = np.zeros(self.current_image.shape[:2], dtype=np.uint8)
        
        for i, mask in enumerate(masks, 1):
            combined[mask['segmentation']] = i
            
        return combined

    def visualize_masks(self, masks: List[Dict[str, Any]], 
                       show_points: bool = True,
                       show_boxes: bool = True) -> np.ndarray:
        """
        Visualize masks overlaid on the image.
        
        Args:
            masks: List of mask dictionaries
            show_points: Whether to show point prompts
            show_boxes: Whether to show bounding boxes
            
        Returns:
            Visualization image as numpy array
        """
        if self.current_image is None:
            raise RuntimeError("No image set for visualization")
            
        # Create visualization
        vis_image = self.current_image.copy()
        
        # Overlay masks with different colors
        colors = np.random.randint(0, 255, size=(len(masks), 3))
        
        for i, mask in enumerate(masks):
            mask_area = mask['segmentation']
            color = colors[i]
            
            # Apply colored overlay
            vis_image[mask_area] = vis_image[mask_area] * 0.6 + color * 0.4
            
            if show_boxes and 'bbox' in mask:
                bbox = mask['bbox']
                x, y, w, h = bbox
                cv2.rectangle(vis_image, (int(x), int(y)), (int(x+w), int(y+h)), color.tolist(), 2)
                
        return vis_image.astype(np.uint8)

    def unload_model(self) -> None:
        """Unload the model to free memory."""
        self.model = None
        self.predictor = None
        self.mask_generator = None
        self.current_image = None
        
        # GPU memory cleanup removed - running on CPU only
            
        logger.info("SAM model unloaded")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        model_config = self.MODEL_CONFIGS[self.model_type]
        return {
            'model_type': self.model_type,
            'device': self.device,
            'checkpoint': model_config['checkpoint'],
            'size_mb': model_config['size_mb'],
            'is_loaded': self.is_loaded(),
            'has_image': self.current_image is not None
        }
