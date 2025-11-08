"""
Safety & Ethics Agent for content moderation and safety analysis.
"""
from typing import Any, Dict, List
import numpy as np
from google.cloud import vision
from transformers import pipeline
from .base_agent import BaseAgent

class SafetyAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.safety_score = 0.0
        self.safety_metrics = {}
        
        # Initialize content moderation models
        self._initialize_models()
        
    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyze frame for safety and ethical concerns.
        
        Args:
            frame: Video frame as numpy array
            
        Returns:
            Dictionary containing safety analysis results
        """
        metrics = {
            'explicit_content': self._check_explicit_content(frame),
            'harmful_objects': self._detect_harmful_objects(frame),
            'bias_check': self._analyze_bias(frame),
            'misleading_elements': self._check_misleading_content(frame)
        }
        
        self.safety_metrics = metrics
        self.safety_score = self._calculate_overall_score(metrics)
        
        return {
            'score': self.safety_score,
            'metrics': metrics,
            'flags': self._identify_safety_flags(metrics)
        }
    
    def get_score(self) -> float:
        """
        Get the overall safety score.
        
        Returns:
            Float score between 0 and 1
        """
        return self.safety_score
    
    def _initialize_models(self):
        """Initialize all required models for safety analysis."""
        # Initialize Google Cloud Vision client
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Initialize hate speech detection
        self.toxic_classifier = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            return_all_scores=True
        )
        
        # Initialize object detection
        self.object_detector = pipeline(
            "object-detection",
            model="facebook/detr-resnet-50"
        )
    
    def _check_explicit_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Check for explicit or inappropriate content."""
        # Convert frame to Vision API format
        success, encoded_image = cv2.imencode('.jpg', frame)
        content = encoded_image.tobytes()
        
        image = vision.Image(content=content)
        
        # Perform safe search detection
        response = self.vision_client.safe_search_detection(image=image)
        safe_search = response.safe_search_annotation
        
        scores = {
            'adult': safe_search.adult,
            'violence': safe_search.violence,
            'medical': safe_search.medical,
            'spoof': safe_search.spoof,
            'racy': safe_search.racy
        }
        
        return {
            'flags': [k for k, v in scores.items() if v >= 3],  # Likelihood >= POSSIBLE
            'score': self._calculate_safety_score(scores)
        }
    
    def _detect_harmful_objects(self, frame: np.ndarray) -> Dict[str, Any]:
        """Detect potentially harmful or dangerous objects."""
        results = self.object_detector(frame)
        
        harmful_objects = [
            result for result in results 
            if result['label'] in self.config.get('harmful_objects', [])
        ]
        
        return {
            'detected_objects': harmful_objects,
            'score': 1.0 if not harmful_objects else 0.5
        }
    
    def _analyze_bias(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze content for potential bias or stereotypes."""
        # This would require more sophisticated analysis
        # Current implementation is a placeholder
        return {
            'detected_bias': [],
            'score': 0.9
        }
    
    def _check_misleading_content(self, frame: np.ndarray) -> Dict[str, Any]:
        """Check for potentially misleading or deceptive content."""
        # Implement checks for:
        # - Unrealistic claims
        # - Manipulated imagery
        # - Deceptive practices
        return {
            'misleading_elements': [],
            'score': 0.95
        }
    
    def _calculate_safety_score(self, scores: Dict[str, int]) -> float:
        """Calculate safety score from Safe Search API results."""
        # Convert likelihood enum to scores (UNLIKELY=1, POSSIBLE=2, LIKELY=3, VERY_LIKELY=4)
        max_score = max(scores.values())
        return 1.0 - (max_score / 4.0)
    
    def _identify_safety_flags(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify specific safety concerns that need attention."""
        flags = []
        
        # Check explicit content
        if metrics['explicit_content']['flags']:
            flags.extend(metrics['explicit_content']['flags'])
        
        # Check harmful objects
        if metrics['harmful_objects']['detected_objects']:
            flags.append("Harmful objects detected")
            
        # Check bias
        if metrics['bias_check']['detected_bias']:
            flags.extend(metrics['bias_check']['detected_bias'])
            
        # Check misleading content
        if metrics['misleading_elements']['misleading_elements']:
            flags.extend(metrics['misleading_elements']['misleading_elements'])
            
        return flags
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall safety score."""
        weights = {
            'explicit_content': 0.4,
            'harmful_objects': 0.2,
            'bias_check': 0.2,
            'misleading_elements': 0.2
        }
        
        score = (
            metrics['explicit_content']['score'] * weights['explicit_content'] +
            metrics['harmful_objects']['score'] * weights['harmful_objects'] +
            metrics['bias_check']['score'] * weights['bias_check'] +
            metrics['misleading_elements']['score'] * weights['misleading_elements']
        )
        
        return min(max(score, 0.0), 1.0)  # Normalize to 0-1