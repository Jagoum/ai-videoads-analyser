"""
Message Clarity Agent for analyzing advertising message effectiveness.
"""
from typing import Any, Dict, List
import numpy as np
from transformers import pipeline
from google.cloud import vision
from .base_agent import BaseAgent

class MessageAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.clarity_score = 0.0
        self.clarity_metrics = {}
        
        # Initialize required models
        self._initialize_models()
        
    def analyze(self, frame: np.ndarray, text_content: str = None) -> Dict[str, Any]:
        """
        Analyze message clarity and effectiveness.
        
        Args:
            frame: Video frame as numpy array
            text_content: Optional text content from the ad
            
        Returns:
            Dictionary containing message clarity analysis
        """
        metrics = {
            'product_visibility': self._analyze_product_visibility(frame),
            'text_clarity': self._analyze_text_clarity(frame),
            'message_coherence': self._analyze_message_coherence(text_content),
            'call_to_action': self._analyze_call_to_action(text_content)
        }
        
        self.clarity_metrics = metrics
        self.clarity_score = self._calculate_overall_score(metrics)
        
        return {
            'score': self.clarity_score,
            'metrics': metrics,
            'suggestions': self._generate_suggestions(metrics)
        }
    
    def get_score(self) -> float:
        """
        Get the overall message clarity score.
        
        Returns:
            Float score between 0 and 1
        """
        return self.clarity_score
    
    def _initialize_models(self):
        """Initialize required models and clients."""
        # Vision API client for OCR and object detection
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Text classification pipeline for message analysis
        self.text_classifier = pipeline(
            "text-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Sentiment analysis pipeline
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
    
    def _analyze_product_visibility(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze product visibility and prominence."""
        # Convert frame to Vision API format
        success, encoded_image = cv2.imencode('.jpg', frame)
        content = encoded_image.tobytes()
        
        image = vision.Image(content=content)
        
        # Detect objects and analyze their prominence
        objects = self.vision_client.object_localization(image=image).localized_object_annotations
        
        # Check if product is visible and prominent
        product_objects = [
            obj for obj in objects 
            if obj.name.lower() in self.config.get('product_keywords', [])
        ]
        
        if not product_objects:
            return {
                'visible': False,
                'prominence': 0.0,
                'score': 0.0
            }
        
        # Calculate prominence based on object size and position
        max_prominence = max(obj.score for obj in product_objects)
        
        return {
            'visible': True,
            'prominence': float(max_prominence),
            'score': float(max_prominence)
        }
    
    def _analyze_text_clarity(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze text clarity and readability."""
        # Perform OCR
        success, encoded_image = cv2.imencode('.jpg', frame)
        content = encoded_image.tobytes()
        
        image = vision.Image(content=content)
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            return {
                'detected_text': "",
                'readability': 0.0,
                'score': 0.0
            }
        
        # Analyze text properties
        main_text = texts[0].description
        
        # Calculate readability score
        readability = self._calculate_readability(main_text)
        
        return {
            'detected_text': main_text,
            'readability': readability,
            'score': readability
        }
    
    def _analyze_message_coherence(self, text_content: str) -> Dict[str, Any]:
        """Analyze message coherence and alignment with brand message."""
        if not text_content:
            return {
                'coherence': 0.0,
                'alignment': 0.0,
                'score': 0.0
            }
        
        # Check message alignment with brand values
        brand_values = self.config.get('brand_values', [])
        if brand_values:
            alignments = [
                self._check_text_alignment(text_content, value)
                for value in brand_values
            ]
            alignment_score = np.mean(alignments)
        else:
            alignment_score = 0.8  # Default if no brand values specified
        
        # Analyze message coherence
        coherence_score = self._analyze_text_coherence(text_content)
        
        return {
            'coherence': coherence_score,
            'alignment': alignment_score,
            'score': (coherence_score + alignment_score) / 2
        }
    
    def _analyze_call_to_action(self, text_content: str) -> Dict[str, Any]:
        """Analyze effectiveness of call to action."""
        if not text_content:
            return {
                'cta_present': False,
                'strength': 0.0,
                'score': 0.0
            }
        
        # Check for CTA phrases
        cta_phrases = self.config.get('cta_phrases', [
            "buy now", "learn more", "sign up", "get started",
            "shop now", "discover", "try now", "join now"
        ])
        
        text_lower = text_content.lower()
        detected_ctas = [
            phrase for phrase in cta_phrases
            if phrase in text_lower
        ]
        
        if not detected_ctas:
            return {
                'cta_present': False,
                'strength': 0.0,
                'score': 0.0
            }
        
        # Analyze CTA strength
        strength = self._analyze_cta_strength(text_content)
        
        return {
            'cta_present': True,
            'detected_ctas': detected_ctas,
            'strength': strength,
            'score': strength
        }
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate text readability score."""
        # Simplified implementation
        # Could be extended with more sophisticated readability metrics
        words = text.split()
        if not words:
            return 0.0
            
        avg_word_length = sum(len(word) for word in words) / len(words)
        readability = 1.0 - min(avg_word_length / 10.0, 1.0)
        
        return readability
    
    def _check_text_alignment(self, text: str, target: str) -> float:
        """Check text alignment with target concept."""
        result = self.text_classifier(text, target)
        return float(result[0]['score'])
    
    def _analyze_text_coherence(self, text: str) -> float:
        """Analyze coherence of the message."""
        # Simplified coherence analysis
        # Could be extended with more sophisticated NLP metrics
        sentences = text.split('.')
        if len(sentences) <= 1:
            return 0.8
            
        return 0.9  # Placeholder score
    
    def _analyze_cta_strength(self, text: str) -> float:
        """Analyze the strength of the call to action."""
        sentiment_result = self.sentiment_analyzer(text)[0]
        
        # Convert sentiment to strength score
        if sentiment_result['label'] == 'POSITIVE':
            strength = sentiment_result['score']
        else:
            strength = 1 - sentiment_result['score']
            
        return float(strength)
    
    def _generate_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on metrics."""
        suggestions = []
        
        # Product visibility suggestions
        if metrics['product_visibility']['score'] < 0.7:
            suggestions.append("Increase product visibility and prominence")
            
        # Text clarity suggestions
        if metrics['text_clarity']['score'] < 0.7:
            suggestions.append("Improve text readability and contrast")
            
        # Message coherence suggestions
        if metrics['message_coherence']['score'] < 0.7:
            suggestions.append("Strengthen message alignment with brand values")
            
        # CTA suggestions
        if not metrics['call_to_action']['cta_present']:
            suggestions.append("Add a clear call to action")
        elif metrics['call_to_action']['strength'] < 0.7:
            suggestions.append("Make call to action more compelling")
            
        return suggestions
    
    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall message clarity score."""
        weights = {
            'product_visibility': 0.3,
            'text_clarity': 0.25,
            'message_coherence': 0.25,
            'call_to_action': 0.2
        }
        
        score = sum(
            metrics[key]['score'] * weights[key]
            for key in weights
        )
        
        return min(max(score, 0.0), 1.0)  # Normalize to 0-1