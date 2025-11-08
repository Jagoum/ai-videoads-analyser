"""
Brand Agent for analyzing brand alignment in video ads.
"""
from typing import Any, Dict, List
import cv2
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
from .base_agent import BaseAgent

class BrandAgent(BaseAgent):
    """
    Analyzes brand alignment, including color palette, logo, and visual style.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.score = 0.0
        self.metrics = {}
        
        # Initialize CLIP model
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        self._load_brand_assets()

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single video frame for brand compliance.

        Args:
            frame (np.ndarray): The video frame to analyze.

        Returns:
            Dict[str, Any]: A dictionary with the analysis results.
        """
        self.metrics = {
            'color_match': self._analyze_colors(frame),
            'logo_detection': self._detect_logo(frame),
            'visual_style_match': self._analyze_visual_style(frame),
        }
        self.score = self._calculate_overall_score()
        
        return {
            'score': self.score,
            'metrics': self.metrics,
            'violations': self._get_violations()
        }

    def get_score(self) -> float:
        """
        Returns the overall brand alignment score.
        """
        return self.score

    def _load_brand_assets(self):
        """
        Loads brand assets from the configuration.
        """
        self.brand_colors = self.config.get('color_palette', [])
        self.logo_template = cv2.imread(self.config.get('logo_path', ''))
        
        # Load style images
        style_image_paths = self.config.get('style_images', [])
        self.style_images = [Image.open(p) for p in style_image_paths]

    def _analyze_colors(self, frame: np.ndarray) -> float:
        """
        Analyzes the color palette of the frame.
        """
        if not self.brand_colors:
            return 1.0

        dominant_colors = self._extract_dominant_colors(frame)
        return self._calculate_color_similarity(dominant_colors, self.brand_colors)

    def _detect_logo(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detects the brand logo in the frame.
        """
        if self.logo_template is None:
            return {'present': False, 'confidence': 0.0}

        result = cv2.matchTemplate(frame, self.logo_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        return {
            'present': max_val > 0.8,
            'confidence': float(max_val),
            'location': max_loc
        }

    def _analyze_visual_style(self, frame: np.ndarray) -> float:
        """
        Analyzes the visual style using CLIP.
        """
        if not self.style_images:
            return 1.0

        frame_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Process frame and style images
        inputs = self.clip_processor(images=[frame_image] + self.style_images, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            image_features = self.clip_model.get_image_features(**inputs)
        
        # Compare frame feature to style features
        frame_feature = image_features
        style_features = image_features[1:]
        
        # Cosine similarity
        similarities = torch.nn.functional.cosine_similarity(frame_feature, style_features)
        
        return float(similarities.mean())

    def _calculate_overall_score(self) -> float:
        """
        Calculates the weighted average score for brand alignment.
        """
        weights = {'color_match': 0.4, 'logo_detection': 0.4, 'visual_style_match': 0.2}
        
        logo_score = self.metrics['logo_detection']['confidence']
        
        score = (self.metrics['color_match'] * weights['color_match'] +
                 logo_score * weights['logo_detection'] +
                 self.metrics['visual_style_match'] * weights['visual_style_match'])
        
        return float(score)

    def _get_violations(self) -> List[str]:
        """
        Identifies any brand guideline violations.
        """
        violations = []
        if self.metrics['color_match'] < 0.7:
            violations.append("Color palette does not match brand guidelines.")
        if not self.metrics['logo_detection']['present']:
            violations.append("Brand logo is not detected.")
        if self.metrics['visual_style_match'] < 0.6:
            violations.append("Visual style is inconsistent with the brand.")
        return violations

    def _extract_dominant_colors(self, frame: np.ndarray, k=5) -> List[np.ndarray]:
        """
        Extracts the k dominant colors from a frame.
        """
        pixels = frame.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        return centers

    def _calculate_color_similarity(self, frame_colors: List[np.ndarray], brand_colors_hex: List[str]) -> float:
        """
        Calculates the similarity between the frame's colors and the brand's colors.
        """
        brand_colors_rgb = [self._hex_to_rgb(c) for c in brand_colors_hex]
        
        total_similarity = 0
        for frame_color in frame_colors:
            distances = [np.linalg.norm(frame_color - brand_color) for brand_color in brand_colors_rgb]
            min_distance = min(distances)
            total_similarity += 1 - (min_distance / np.sqrt(3 * 255**2))
            
        return total_similarity / len(frame_colors)

    def _hex_to_rgb(self, hex_color: str) -> np.ndarray:
        """
        Converts a hex color string to an RGB numpy array.
        """
        hex_color = hex_color.lstrip('#')
        return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)])