"""
Tests for the Brand Agent.
"""
import pytest
import numpy as np
import cv2
from app.agents.brand_agent import BrandAgent

@pytest.fixture
def brand_config():
    return {
        'color_palette': ['#FF0000', '#00FF00', '#0000FF'],
        'logo_path': 'tests/fixtures/test_logo.png',
        'style_images': ['tests/fixtures/test_style.jpg']
    }

@pytest.fixture
def test_frame():
    # Create a test frame with known colors
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    frame[:50, :50] = [255, 0, 0]  # Red
    frame[:50, 50:] = [0, 255, 0]  # Green
    frame[50:, :50] = [0, 0, 255]  # Blue
    frame[50:, 50:] = [255, 255, 255]  # White
    return frame

def test_brand_agent_initialization(brand_config):
    agent = BrandAgent(brand_config)
    assert agent is not None
    assert agent.brand_colors == brand_config['color_palette']

def test_color_analysis(brand_config, test_frame):
    agent = BrandAgent(brand_config)
    result = agent.analyze(test_frame)
    
    assert 'score' in result
    assert 'metrics' in result
    assert 'color_match' in result['metrics']
    assert isinstance(result['score'], float)
    assert 0 <= result['score'] <= 1

def test_logo_detection(brand_config, test_frame):
    agent = BrandAgent(brand_config)
    result = agent.analyze(test_frame)
    
    assert 'logo_detection' in result['metrics']
    assert 'present' in result['metrics']['logo_detection']
    assert 'confidence' in result['metrics']['logo_detection']

def test_visual_style_analysis(brand_config, test_frame):
    agent = BrandAgent(brand_config)
    result = agent.analyze(test_frame)
    
    assert 'visual_style_match' in result['metrics']
    assert isinstance(result['metrics']['visual_style_match'], float)
    assert 0 <= result['metrics']['visual_style_match'] <= 1

def test_violations_reporting(brand_config, test_frame):
    agent = BrandAgent(brand_config)
    result = agent.analyze(test_frame)
    
    assert 'violations' in result
    assert isinstance(result['violations'], list)