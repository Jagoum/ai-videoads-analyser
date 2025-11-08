"""
Clarity Agent for analyzing the clarity of the message in video ads.
"""
from typing import Any, Dict, List
import cv2
import numpy as np
from .base_agent import BaseAgent

class ClarityAgent(BaseAgent):
    """
    Analyzes message clarity, focusing on product visibility.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.score = 0.0
        self.metrics = {}
        self._load_assets()

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single video frame for message clarity.

        Args:
            frame (np.ndarray): The video frame to analyze.

        Returns:
            Dict[str, Any]: A dictionary with the analysis results.
        """
        self.metrics = {
            'product_detection': self._detect_product(frame),
        }
        self.score = self._calculate_overall_score()
        
        return {
            'score': self.score,
            'metrics': self.metrics,
            'suggestions': self._get_suggestions()
        }

    def get_score(self) -> float:
        """
        Returns the overall message clarity score.
        """
        return self.score

    def _load_assets(self):
        """
        Loads assets needed for clarity analysis from the configuration.
        """
        self.product_template = cv2.imread(self.config.get('product_image_path', ''))

    def _detect_product(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Detects the product in the frame using template matching.
        """
        if self.product_template is None:
            return {'present': False, 'confidence': 0.0}

        result = cv2.matchTemplate(frame, self.product_template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        return {
            'present': max_val > 0.7, # Lower threshold for products
            'confidence': float(max_val),
            'location': max_loc
        }

    def _calculate_overall_score(self) -> float:
        """
        Calculates the overall clarity score.
        """
        return float(self.metrics['product_detection']['confidence'])

    def _get_suggestions(self) -> List[str]:
        """
        Provides suggestions for improving message clarity.
        """
        suggestions = []
        if not self.metrics['product_detection']['present']:
            suggestions.append("Product is not clearly visible. Ensure it is prominently displayed.")
        return suggestions