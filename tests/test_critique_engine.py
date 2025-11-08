"""
Tests for the CritiqueEngine implementation.
"""
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
from app.core.critique_engine import CritiqueEngine

@pytest.fixture
def mock_config():
    return {
        'sampling_rate': 1,
        'max_workers': 2,
        'temporal_window': 5,
        'min_scene_duration': 0.5,
        'brand_agent': {},
        'quality_agent': {},
        'clarity_agent': {},
        'safety_agent': {},
        'synthesis_agent': {}
    }

@pytest.fixture
def critique_engine(mock_config):
    with patch('app.core.critique_engine.BrandAgent'), \
         patch('app.core.critique_engine.QualityAgent'), \
         patch('app.core.critique_engine.ClarityAgent'), \
         patch('app.core.critique_engine.SafetyAgent'), \
         patch('app.core.critique_engine.SynthesisAgent'):
        return CritiqueEngine(mock_config)

@pytest.fixture
def sample_video(tmp_path):
    """Creates a sample video file for testing."""
    video_path = str(tmp_path / "test_video.mp4")
    
    # Create a simple video with 10 frames
    frames = []
    for i in range(10):
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(frame, str(i), (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        frames.append(frame)
    
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (100, 100))
    for frame in frames:
        out.write(frame)
    out.release()
    
    return video_path

def test_critique_engine_initialization(critique_engine, mock_config):
    assert critique_engine.sampling_rate == mock_config['sampling_rate']
    assert critique_engine.max_workers == mock_config['max_workers']
    assert len(critique_engine.agents) == 5

def test_analyze_frame(critique_engine):
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Mock all agents' analyze methods
    for agent in critique_engine.agents.values():
        agent.analyze = Mock(return_value={'score': 0.8, 'metrics': {}})
    
    result = critique_engine.analyze_frame(frame)
    
    assert isinstance(result, dict)
    assert all(agent.analyze.called for name, agent in critique_engine.agents.items() 
              if name != 'synthesis')

def test_analyze_video(critique_engine, sample_video):
    # Mock all agents' analyze methods
    for agent in critique_engine.agents.values():
        agent.analyze = Mock(return_value={'score': 0.8, 'metrics': {}})
    
    result = critique_engine.analyze_video(sample_video)
    
    assert isinstance(result, dict)
    assert 'frame_results' in result
    assert 'temporal_analysis' in result
    assert 'video_metadata' in result

def test_get_sample_frames(critique_engine, sample_video):
    cap = cv2.VideoCapture(sample_video)
    frames = critique_engine._get_sample_frames(cap, interval=2)
    
    assert isinstance(frames, list)
    assert all(isinstance(f, tuple) and len(f) == 2 for f in frames)
    assert all(isinstance(f[1], np.ndarray) for f in frames)
    
    cap.release()

def test_parallel_frame_analysis(critique_engine):
    # Create test frames
    frames = [(i, np.zeros((100, 100, 3), dtype=np.uint8)) for i in range(5)]
    
    # Mock analyze_frame method
    critique_engine.analyze_frame = Mock(return_value={'score': 0.8})
    
    results = critique_engine._parallel_frame_analysis(frames)
    
    assert isinstance(results, dict)
    assert len(results) == len(frames)
    assert critique_engine.analyze_frame.call_count == len(frames)

def test_analyze_temporal_patterns(critique_engine):
    frame_results = {
        0: {'score': 0.8, 'metrics': {'quality': 0.8}},
        30: {'score': 0.7, 'metrics': {'quality': 0.7}},
        60: {'score': 0.9, 'metrics': {'quality': 0.9}}
    }
    
    fps = 30.0
    result = critique_engine._analyze_temporal_patterns(frame_results, fps)
    
    assert isinstance(result, dict)
    assert 'scene_changes' in result
    assert 'content_flow' in result
    assert 'pacing' in result
    assert 'consistency' in result

def test_scene_change_detection(critique_engine):
    frame_results = {
        0: {'quality': {'score': 0.8}},
        30: {'quality': {'score': 0.3}},  # Big change
        60: {'quality': {'score': 0.4}}   # Small change
    }
    
    scene_changes = critique_engine._detect_scene_changes(frame_results)
    
    assert isinstance(scene_changes, list)
    assert len(scene_changes) > 0
    assert all('frame' in change for change in scene_changes)
    assert all('transition_type' in change for change in scene_changes)

def test_error_handling_invalid_video(critique_engine, tmp_path):
    invalid_video = str(tmp_path / "invalid.mp4")
    with open(invalid_video, 'w') as f:
        f.write("Not a video file")
    
    with pytest.raises(ValueError):
        critique_engine.analyze_video(invalid_video)

def test_consistency_analysis(critique_engine):
    frame_results = {
        0: {'brand': {'score': 0.8}, 'quality': {'score': 0.7}},
        30: {'brand': {'score': 0.7}, 'quality': {'score': 0.8}},
        60: {'brand': {'score': 0.9}, 'quality': {'score': 0.7}}
    }
    
    consistency = critique_engine._analyze_consistency(frame_results)
    
    assert isinstance(consistency, dict)
    assert 'brand_consistency' in consistency
    assert 'quality_consistency' in consistency
    assert 'safety_consistency' in consistency