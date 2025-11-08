"""
Quality Agent for analyzing the visual quality of video ads.
"""
from typing import Any, Dict, List
import cv2
import numpy as np
from .base_agent import BaseAgent

class QualityAgent(BaseAgent):
    """
    Analyzes visual quality metrics like blur, contrast, and brightness.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.score = 0.0
        self.metrics = {}

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single video frame for visual quality.

        Args:
            frame (np.ndarray): The video frame to analyze.

        Returns:
            Dict[str, Any]: A dictionary with the analysis results.
        """
        self.metrics = {
            'blur_level': self._calculate_blur(frame),
            'contrast_level': self._calculate_contrast(frame),
            'brightness_level': self._calculate_brightness(frame),
        }
        self.score = self._calculate_overall_score()
        
        return {
            'score': self.score,
            'metrics': self.metrics,
            'issues': self._get_issues()
        }

    def get_score(self) -> float:
        """
        Returns the overall visual quality score.
        """
        return self.score

    def _calculate_blur(self, frame: np.ndarray) -> float:
        """
        Calculates the blur level using the variance of the Laplacian.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """
        Calculates the contrast level using RMS contrast.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray.std()

    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """
        Calculates the average brightness level.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray.mean()

    def _calculate_overall_score(self) -> float:
        """
        Calculates the overall quality score based on metrics.
        This is a simplified scoring model.
        """
        # Normalize metrics to a 0-1 scale (values are examples)
        blur_score = 1 - min(self.metrics['blur_level'] / 100, 1)
        contrast_score = min(self.metrics['contrast_level'] / 100, 1)
        
        # Brightness is optimal around 128
        brightness_score = 1 - abs(self.metrics['brightness_level'] - 128) / 128
        
        # Weighted average
        score = (blur_score * 0.4 + 
                 contrast_score * 0.3 + 
                 brightness_score * 0.3)
                 
        return float(score)

    def _get_issues(self) -> List[str]:
        """
        Identifies any visual quality issues.
        """
        issues = []
        if self.metrics['blur_level'] < 20:
            issues.append("Video may be blurry.")
        if self.metrics['contrast_level'] < 30:
            issues.append("Video has low contrast.")
        if self.metrics['brightness_level'] < 50:
            issues.append("Video is too dark.")
        if self.metrics['brightness_level'] > 200:
            issues.append("Video is too bright.")
        return issues