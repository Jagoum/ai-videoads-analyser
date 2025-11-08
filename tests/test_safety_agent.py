"""
Tests for the SafetyAgent implementation.
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
from app.agents.safety_agent import SafetyAgent

@pytest.fixture
def mock_config():
    return {
        'safety_agent': {
            'thresholds': {
                'harmful_content': 0.7,
                'bias': 0.6,
                'adult_content': 0.7,
                'violence': 0.6
            }
        }
    }

@pytest.fixture
def safety_agent(mock_config):
    with patch('app.agents.safety_agent.ContentModeratorClient'), \
         patch('app.agents.safety_agent.vision.ImageAnnotatorClient'):
        return SafetyAgent(mock_config)

@pytest.fixture
def sample_frame():
    # Create a simple test frame
    return np.zeros((100, 100, 3), dtype=np.uint8)

def test_safety_agent_initialization(safety_agent):
    assert safety_agent.score == 0.0
    assert isinstance(safety_agent.metrics, dict)

def test_analyze_frame_structure(safety_agent, sample_frame):
    result = safety_agent.analyze(sample_frame)
    
    assert isinstance(result, dict)
    assert 'score' in result
    assert 'metrics' in result
    assert 'flags' in result
    assert 'recommendations' in result

def test_analyze_frame_metrics(safety_agent, sample_frame):
    result = safety_agent.analyze(sample_frame)
    
    required_metrics = [
        'harmful_content_confidence',
        'bias_confidence',
        'adult_content_score',
        'violence_score',
        'hate_speech_score',
        'brand_safety_score'
    ]
    
    for metric in required_metrics:
        assert metric in result['metrics']
        assert 0 <= result['metrics'][metric] <= 1.0

def test_get_flags_threshold_behavior(safety_agent):
    # Test with metrics that should trigger flags
    safety_agent.metrics = {
        'harmful_content_confidence': 0.8,
        'bias_confidence': 0.7,
        'adult_content_score': 0.8,
        'violence_score': 0.7,
        'brand_safety_score': 0.2
    }
    
    flags = safety_agent._get_flags()
    assert len(flags) > 0
    assert any('harmful content' in flag.lower() for flag in flags)
    assert any('bias' in flag.lower() for flag in flags)

def test_get_recommendations(safety_agent):
    # Test with metrics that should trigger recommendations
    safety_agent.metrics = {
        'harmful_content_confidence': 0.6,
        'bias_confidence': 0.5,
        'adult_content_score': 0.6,
        'violence_score': 0.5,
        'brand_safety_score': 0.6
    }
    
    recommendations = safety_agent._get_recommendations()
    assert len(recommendations) > 0
    assert all(isinstance(rec, str) for rec in recommendations)

@pytest.mark.asyncio
async def test_azure_analysis_error_handling(safety_agent, sample_frame):
    with patch.object(safety_agent.content_moderator.image_moderation, 
                     'evaluate_file_input', 
                     side_effect=Exception('API Error')):
        result = safety_agent._analyze_azure(cv2.imencode('.jpg', sample_frame)[1].tobytes())
        
        assert isinstance(result, dict)
        assert all(score == 0.0 for score in result.values())

@pytest.mark.asyncio
async def test_google_vision_error_handling(safety_agent, sample_frame):
    with patch.object(safety_agent.vision_client, 
                     'safe_search_detection',
                     side_effect=Exception('API Error')):
        result = safety_agent._analyze_google_vision(
            cv2.imencode('.jpg', sample_frame)[1].tobytes()
        )
        
        assert isinstance(result, dict)
        assert all(score == 0.0 for score in result.values())

def test_normalize_likelihood(safety_agent):
    # Test likelihood normalization
    test_cases = [
        (0, 0.0),  # UNKNOWN
        (1, 0.2),  # VERY_UNLIKELY
        (3, 0.6),  # POSSIBLE
        (5, 1.0)   # VERY_LIKELY
    ]
    
    for input_val, expected in test_cases:
        assert safety_agent._normalize_likelihood(input_val) == expected

def test_calculate_overall_score(safety_agent):
    # Test overall score calculation
    safety_agent.metrics = {
        'harmful_content_confidence': 0.2,
        'bias_confidence': 0.1,
        'adult_content_score': 0.3,
        'violence_score': 0.1
    }
    
    score = safety_agent._calculate_overall_score()
    assert 0 <= score <= 1.0