"""
Brand Compliance Agent for ensuring brand guidelines are followed.
"""
from typing import Any, Dict, List
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from .base_agent import BaseAgent

class BrandComplianceAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.brand_score = 0.0
        self.brand_metrics = {}
        
        # Initialize CLIP model for visual similarity
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Load brand assets
        self._load_brand_assets()
        
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze frame for brand compliance.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary containing brand compliance metrics
        """
        metrics = {
            'color_match': self._analyze_colors(frame),
            'logo_detection': self._detect_logo(frame),
            'visual_style': self._analyze_visual_style(frame),
            'tone_match': self._analyze_tone()
        }
        
        self.brand_metrics = metrics
        self.brand_score = self._calculate_overall_score(metrics)
        
        return {
            'score': self.brand_score,
            'metrics': metrics,
            'violations': self._check_violations(metrics)
        }
    
    def get_score(self) -> float:
        """
        Get the overall brand compliance score.
        
        Returns:
            Float score between 0 and 1
        """
        return self.brand_score
    
    def _load_brand_assets(self):
        """Load brand assets from config."""
        if not self.config:
            raise ValueError("Brand configuration required")
            
        self.brand_colors = self.config.get('color_palette', [])
        self.logo_template = cv2.imread(self.config['logo_path'])
        self.brand_style_examples = self.config.get('style_examples', [])
        self.tone_keywords = self.config.get('tone_of_voice', [])
    
    def _analyze_colors(self, frame: np.ndarray) -> float:
        """Analyze color palette compliance."""
        frame_colors = self._extract_dominant_colors(frame)
        return self._calculate_color_similarity(frame_colors, self.brand_colors)
    
    def _detect_logo(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect and analyze logo placement/usage."""
        if self.logo_template is None:
            return {'present': False, 'score': 0.0}
            
        result = cv2.matchTemplate(frame, self.logo_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        return {
            'present': max_val > 0.8,
            'confidence': float(max_val),
            'location': max_loc,
            'score': float(max_val)
        }
    
    def _analyze_visual_style(self, frame: np.ndarray) -> float:
        """Analyze visual style consistency using CLIP."""
        if not self.brand_style_examples:
            return 0.8  # Default score if no examples provided
            
        frame_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        inputs = self.clip_processor(images=[frame_image], return_tensors="pt")
        
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        
        # Compare with brand style examples
        # This is a simplified implementation
        return 0.85
    
    def _analyze_tone(self) -> float:
        """Analyze tone of voice in text elements."""
        # Implement tone analysis
        # This is a placeholder implementation
        return 0.9
    
    def _extract_dominant_colors(self, frame: np.ndarray) -> List[np.ndarray]:
        """Extract dominant colors from frame."""
        pixels = frame.reshape(-1, 3)
        pixels = np.float32(pixels)
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        K = 5  # Number of dominant colors to extract
        _, labels, centers = cv2.kmeans(pixels, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        return centers
    
    def _calculate_color_similarity(self, colors1: List[np.ndarray], colors2: List[str]) -> float:
        """Calculate similarity between two color palettes."""
        # Convert hex colors to RGB if needed
        if isinstance(colors2[0], str):
            colors2 = [self._hex_to_rgb(color) for color in colors2]
        
        # Calculate color distance
        min_distances = []
        for c1 in colors1:
            distances = [np.linalg.norm(c1 - c2) for c2 in colors2]
            min_distances.append(min(distances))
        
        # Normalize and convert to similarity score
        avg_distance = np.mean(min_distances)
        similarity = 1 - (avg_distance / 441.67)  # Max RGB distance is √(255² + 255² + 255²)
        return float(max(0, min(similarity, 1)))
    
    def _hex_to_rgb(self, hex_color: str) -> np.ndarray:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)])
    
    def _check_violations(self, metrics: Dict[str, Any]) -> List[str]:
        """Check for brand guideline violations."""
        violations = []
        
        if metrics['color_match'] < 0.7:
            violations.append("Color palette deviation")
        if not metrics['logo_detection']['present']:
            violations.append("Missing logo")
        if metrics['visual_style'] < 0.6:
            violations.append("Inconsistent visual style")
        if metrics['tone_match'] < 0.7:
            violations.append("Incorrect tone of voice")
            
        return violations
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall brand compliance score."""
        weights = {
            'color_match': 0.3,
            'logo_detection': 0.3,
            'visual_style': 0.2,
            'tone_match': 0.2
        }
        
        logo_score = metrics['logo_detection']['score'] if isinstance(metrics['logo_detection'], dict) else 0.0
        
        score = (
            metrics['color_match'] * weights['color_match'] +
            logo_score * weights['logo_detection'] +
            metrics['visual_style'] * weights['visual_style'] +
            metrics['tone_match'] * weights['tone_match']
        )
        
        return min(max(score, 0.0), 1.0)  # Normalize to 0-1