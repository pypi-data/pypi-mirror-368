from vton_eval.vlm.base import VLMBackend
from typing import List, Dict, Any
import numpy as np
import logging
from PIL import Image
import io

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

logger = logging.getLogger(__name__)


class GeminiBackend(VLMBackend):
    """Google Gemini 2.5 Flash backend for vision-language model tasks."""
    
    def __init__(self, api_key: str, config: Dict[str, Any]):
        super().__init__("gemini", config)
        self.api_key = api_key
        self.model_name = config.get('model_name', 'gemini-2.5-flash')
        self.client = None
        self._initialized = False
        
        if GENAI_AVAILABLE:
            try:
                # Initialize the Gemini client
                self.client = genai.Client(api_key=self.api_key)
                self._initialized = True
                logger.info(f"Initialized Gemini backend with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                self._initialized = False
        else:
            logger.error("google-genai package not installed. Please install with: pip install google-genai")
    
    def _numpy_to_pil(self, image: np.ndarray) -> Image.Image:
        """Convert numpy array to PIL Image."""
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        if len(image.shape) == 2:
            # Grayscale image
            return Image.fromarray(image, mode='L')
        elif len(image.shape) == 3:
            if image.shape[2] == 3:
                # RGB image
                return Image.fromarray(image, mode='RGB')
            elif image.shape[2] == 4:
                # RGBA image
                return Image.fromarray(image, mode='RGBA')
        
        raise ValueError(f"Unsupported image shape: {image.shape}")
    
    def _prepare_image(self, image: np.ndarray) -> types.Part:
        """Prepare image for Gemini API."""
        # Convert numpy array to PIL Image
        pil_image = self._numpy_to_pil(image)
        
        # Convert to JPEG bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format='JPEG', quality=95)
        image_bytes = buffer.getvalue()
        
        # Create Part object for Gemini
        return types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
    
    def query(self, prompt: str, images: List[np.ndarray], **kwargs) -> str:
        """Query Gemini with prompt and images.
        
        Args:
            prompt: Text prompt for the model
            images: List of images as numpy arrays
            **kwargs: Additional parameters like temperature, max_tokens
            
        Returns:
            Model response as string
        """
        if not self._initialized or not self.client:
            logger.error("Gemini client not initialized")
            return "Error: Gemini client not available"
        
        try:
            # Prepare the content parts
            contents = []
            
            # Add images first
            for image in images:
                contents.append(self._prepare_image(image))
            
            # Add the text prompt
            contents.append(prompt)
            
            # Configure generation parameters
            generation_config = types.GenerateContentConfig(
                temperature=kwargs.get('temperature', 0.1),
                max_output_tokens=kwargs.get('max_tokens', 1000),
                candidate_count=1
            )
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generation_config
            )
            
            # Extract text from response
            if response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini")
                return "No response generated"
            
        except Exception as e:
            logger.error(f"Error querying Gemini: {e}")
            return f"Error: {str(e)}"
    
    def batch_query(self, queries: List[Dict[str, Any]]) -> List[str]:
        """Process multiple queries in batch.
        
        Args:
            queries: List of query dictionaries with 'prompt' and 'images' keys
            
        Returns:
            List of responses
        """
        responses = []
        for query in queries:
            response = self.query(
                prompt=query.get('prompt', ''),
                images=query.get('images', []),
                **query.get('kwargs', {})
            )
            responses.append(response)
        return responses
    
    def get_confidence_score(self, response: str) -> float:
        """Extract confidence score from response.
        
        Args:
            response: Model response text
            
        Returns:
            Confidence score between 0 and 1
        """
        import re
        
        # Look for confidence patterns in the response
        patterns = [
            r'confidence[:\s]*([0-9\.]+)',
            r'score[:\s]*([0-9\.]+)',
            r'([0-9\.]+)\s*(?:confidence|certainty)',
            r'([0-9]+)%',  # Percentage
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    score = float(match.group(1))
                    # Convert percentage to decimal if needed
                    if score > 1.0:
                        score = score / 100.0
                    return min(max(score, 0.0), 1.0)
                except ValueError:
                    continue
        
        # Default confidence if no score found
        return 0.5
    
    def is_available(self) -> bool:
        """Check if the backend is available and configured.
        
        Returns:
            True if backend is ready to use
        """
        return self._initialized and self.client is not None
