"""
Safety Agent for analyzing the safety and ethics of video ads.
Uses Azure Content Moderator and Google Cloud Vision AI for comprehensive safety analysis.
"""
from typing import Any, Dict, List
import numpy as np
import cv2
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from azure.cognitiveservices.vision.contentmoderator.models import Screen
from msrest.authentication import CognitiveServicesCredentials
from google.cloud import vision
import os
from .base_agent import BaseAgent

class SafetyAgent(BaseAgent):
    """
    Analyzes video content for safety and ethical concerns using multiple AI services.
    Covers harmful content, bias, violence, adult content, and brand safety.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.score = 0.0
        self.metrics = {}
        
        # Initialize Azure Content Moderator
        self.content_moderator = ContentModeratorClient(
            endpoint=os.getenv('AZURE_COGNITIVE_ENDPOINT'),
            credentials=CognitiveServicesCredentials(os.getenv('AZURE_COGNITIVE_KEY'))
        )
        
        # Initialize Google Cloud Vision
        self.vision_client = vision.ImageAnnotatorClient()

    def analyze(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single video frame for safety using multiple AI services.

        Args:
            frame (np.ndarray): The video frame to analyze.

        Returns:
            Dict[str, Any]: A dictionary with comprehensive analysis results.
        """
        # Convert frame to format suitable for API calls
        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            raise ValueError("Failed to encode image")
        
        image_bytes = encoded_image.tobytes()
        
        # Azure Content Moderator Analysis
        azure_results = self._analyze_azure(image_bytes)
        
        # Google Cloud Vision Analysis
        google_results = self._analyze_google_vision(image_bytes)
        
        # Combine and process results
        self.metrics = {
            'harmful_content_confidence': self._get_harmful_content_score(azure_results, google_results),
            'bias_confidence': self._get_bias_score(google_results),
            'adult_content_score': azure_results.get('adult_score', 0.0),
            'violence_score': azure_results.get('violence_score', 0.0),
            'hate_speech_score': google_results.get('hate_speech_score', 0.0),
            'brand_safety_score': self._calculate_brand_safety_score(azure_results, google_results)
        }
        
        self.score = self._calculate_overall_score()
        
        return {
            'score': self.score,
            'metrics': self.metrics,
            'flags': self._get_flags(),
            'recommendations': self._get_recommendations()
        }
        
    def _analyze_azure(self, image_bytes: bytes) -> Dict[str, float]:
        """
        Analyzes image using Azure Content Moderator.
        """
        try:
            screen = self.content_moderator.image_moderation.evaluate_file_input(
                image_stream=image_bytes,
                cache_image=True
            )
            
            return {
                'adult_score': float(screen.adult_classification_score or 0.0),
                'racy_score': float(screen.racy_classification_score or 0.0),
                'violence_score': float(screen.violence_score or 0.0)
            }
        except Exception as e:
            print(f"Azure Content Moderator error: {str(e)}")
            return {'adult_score': 0.0, 'racy_score': 0.0, 'violence_score': 0.0}
            
    def _analyze_google_vision(self, image_bytes: bytes) -> Dict[str, float]:
        """
        Analyzes image using Google Cloud Vision AI.
        """
        try:
            image = vision.Image(content=image_bytes)
            
            # Run multiple detection types
            safe_search = self.vision_client.safe_search_detection(image=image)
            labels = self.vision_client.label_detection(image=image)
            
            # Process safe search results
            safe_search_results = safe_search.safe_search_annotation
            
            return {
                'explicit_score': self._normalize_likelihood(safe_search_results.adult),
                'violence_score': self._normalize_likelihood(safe_search_results.violence),
                'hate_speech_score': self._analyze_labels_for_bias(labels.label_annotations)
            }
        except Exception as e:
            print(f"Google Cloud Vision error: {str(e)}")
            return {'explicit_score': 0.0, 'violence_score': 0.0, 'hate_speech_score': 0.0}
            
    def _normalize_likelihood(self, likelihood: int) -> float:
        """
        Converts Google Cloud Vision likelihood enum to float score.
        """
        # Likelihood enum values: UNKNOWN=0, VERY_UNLIKELY=1, UNLIKELY=2, POSSIBLE=3, LIKELY=4, VERY_LIKELY=5
        return min(1.0, likelihood / 5.0)

    def get_score(self) -> float:
        """
        Returns the overall safety score.
        """
        return self.score

    def _analyze_labels_for_bias(self, labels: List[Any]) -> float:
        """
        Analyzes image labels to detect potential bias or controversial content.
        """
        # List of sensitive terms that might indicate bias
        sensitive_terms = {
            'stereotype', 'discrimination', 'offensive', 'controversial',
            'racist', 'sexist', 'prejudice', 'bigotry', 'hate'
        }
        
        bias_score = 0.0
        for label in labels:
            description = label.description.lower()
            if any(term in description for term in sensitive_terms):
                bias_score = max(bias_score, label.score)
        
        return bias_score
        
    def _get_harmful_content_score(self, azure_results: Dict[str, float], 
                                 google_results: Dict[str, float]) -> float:
        """
        Combines harmful content scores from multiple sources.
        """
        scores = [
            azure_results.get('adult_score', 0.0),
            azure_results.get('violence_score', 0.0),
            google_results.get('explicit_score', 0.0),
            google_results.get('violence_score', 0.0)
        ]
        return max(scores)  # Use the highest risk score
        
    def _get_bias_score(self, google_results: Dict[str, float]) -> float:
        """
        Determines the bias score from analysis results.
        """
        return google_results.get('hate_speech_score', 0.0)
        
    def _calculate_brand_safety_score(self, azure_results: Dict[str, float],
                                    google_results: Dict[str, float]) -> float:
        """
        Calculates an overall brand safety score.
        """
        weights = {
            'adult': 0.3,
            'violence': 0.3,
            'hate_speech': 0.2,
            'racy': 0.2
        }
        
        return 1.0 - (
            weights['adult'] * azure_results.get('adult_score', 0.0) +
            weights['violence'] * max(azure_results.get('violence_score', 0.0),
                                    google_results.get('violence_score', 0.0)) +
            weights['hate_speech'] * google_results.get('hate_speech_score', 0.0) +
            weights['racy'] * azure_results.get('racy_score', 0.0)
        )

    def _calculate_overall_score(self) -> float:
        """
        Calculates the overall safety score with weighted components.
        A higher score means safer content.
        """
        weights = {
            'harmful_content': 0.35,
            'bias': 0.25,
            'adult_content': 0.20,
            'violence': 0.20
        }
        
        return 1.0 - (
            weights['harmful_content'] * self.metrics['harmful_content_confidence'] +
            weights['bias'] * self.metrics['bias_confidence'] +
            weights['adult_content'] * self.metrics['adult_content_score'] +
            weights['violence'] * self.metrics['violence_score']
        )

    def _get_flags(self) -> List[str]:
        """
        Identifies any safety or ethical flags with detailed explanations.
        """
        flags = []
        thresholds = {
            'harmful_content': 0.7,
            'bias': 0.6,
            'adult_content': 0.7,
            'violence': 0.6,
            'brand_safety': 0.7
        }
        
        if self.metrics['harmful_content_confidence'] > thresholds['harmful_content']:
            flags.append("HIGH RISK: Potentially harmful content detected")
            
        if self.metrics['bias_confidence'] > thresholds['bias']:
            flags.append("CAUTION: Potential bias or stereotypes present")
            
        if self.metrics['adult_content_score'] > thresholds['adult_content']:
            flags.append("WARNING: Adult content detected")
            
        if self.metrics['violence_score'] > thresholds['violence']:
            flags.append("WARNING: Violent content detected")
            
        if 1.0 - self.metrics['brand_safety_score'] > thresholds['brand_safety']:
            flags.append("BRAND RISK: Content may not be brand-safe")
            
        return flags
        
    def _get_recommendations(self) -> List[str]:
        """
        Provides specific recommendations for improving content safety.
        """
        recommendations = []
        
        if self.metrics['harmful_content_confidence'] > 0.5:
            recommendations.append(
                "Review and modify any content that could be interpreted as harmful"
            )
            
        if self.metrics['bias_confidence'] > 0.4:
            recommendations.append(
                "Consider revising content to be more inclusive and avoid stereotypes"
            )
            
        if self.metrics['adult_content_score'] > 0.5:
            recommendations.append(
                "Modify or remove content that may be interpreted as adult-oriented"
            )
            
        if self.metrics['violence_score'] > 0.4:
            recommendations.append(
                "Consider toning down or removing potentially violent imagery"
            )
            
        if self.metrics['brand_safety_score'] < 0.7:
            recommendations.append(
                "Review content against brand safety guidelines and make necessary adjustments"
            )
            
        return recommendations