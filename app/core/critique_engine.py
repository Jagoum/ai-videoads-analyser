"""
Core critique engine for orchestrating the comprehensive analysis of video ads.
Handles full video processing with temporal analysis and multi-agent coordination.
"""
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.agents.brand_agent import BrandAgent
from app.agents.quality_agent import QualityAgent
from app.agents.clarity_agent import ClarityAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.synthesis_agent import SynthesisAgent

class CritiqueEngine:
    """
    Orchestrates the multi-agent critique process for comprehensive video analysis.
    Handles frame sampling, parallel processing, and temporal analysis.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the critique engine and all its agents.

        Args:
            config (Dict[str, Any]): The master configuration object.
        """
        self.config = config
        self.sampling_rate = config.get('sampling_rate', 1)  # Frames per second to analyze
        self.max_workers = config.get('max_workers', 4)  # Maximum parallel workers
        
        # Initialize all analysis agents
        self.agents = {
            'brand': BrandAgent(config.get('brand_agent', {})),
            'quality': QualityAgent(config.get('quality_agent', {})),
            'clarity': ClarityAgent(config.get('clarity_agent', {})),
            'safety': SafetyAgent(config.get('safety_agent', {})),
            'synthesis': SynthesisAgent(config.get('synthesis_agent', {})),
        }
        
        # Initialize temporal analysis settings
        self.temporal_window = config.get('temporal_window', 5)  # seconds
        self.min_scene_duration = config.get('min_scene_duration', 0.5)  # seconds

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """
        Performs comprehensive analysis of a full video.
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            Dict[str, Any]: Comprehensive analysis results including temporal patterns
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        # Calculate frame sampling
        sample_interval = int(fps / self.sampling_rate)
        frames_to_analyze = self._get_sample_frames(cap, sample_interval)
        
        # Analyze frames in parallel
        frame_results = self._parallel_frame_analysis(frames_to_analyze)
        
        # Perform temporal analysis
        temporal_analysis = self._analyze_temporal_patterns(frame_results, fps)
        
        # Generate final report
        synthesis_agent = self.agents['synthesis']
        final_scorecard = synthesis_agent.analyze({
            'frame_results': frame_results,
            'temporal_analysis': temporal_analysis,
            'video_metadata': {
                'duration': duration,
                'fps': fps,
                'frame_count': frame_count
            }
        })
        
        cap.release()
        return final_scorecard
        
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analyzes a single video frame using all critique agents.

        Args:
            frame (np.ndarray): The video frame to analyze.

        Returns:
            Dict[str, Any]: The final, synthesized scorecard for the frame.
        """
        agent_results = {}
        for agent_name, agent in self.agents.items():
            if agent_name != 'synthesis':
                agent_results[agent_name] = agent.analyze(frame)
        
        # Synthesize the results
        synthesis_agent = self.agents['synthesis']
        final_scorecard = synthesis_agent.analyze({'frame_results': agent_results})
        
        return final_scorecard
        
    def _get_sample_frames(self, cap: cv2.VideoCapture, 
                          interval: int) -> List[Tuple[int, np.ndarray]]:
        """
        Extracts frames at specified intervals for analysis.
        """
        frames = []
        frame_idx = 0
        
        while True:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
                
            frames.append((frame_idx, frame))
            frame_idx += interval
            
        return frames
        
    def _parallel_frame_analysis(self, 
                               frames: List[Tuple[int, np.ndarray]]) -> Dict[int, Dict[str, Any]]:
        """
        Analyzes multiple frames in parallel using ThreadPoolExecutor.
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_frame = {
                executor.submit(self.analyze_frame, frame): idx 
                for idx, frame in frames
            }
            
            for future in as_completed(future_to_frame):
                frame_idx = future_to_frame[future]
                try:
                    results[frame_idx] = future.result()
                except Exception as e:
                    print(f"Error analyzing frame {frame_idx}: {str(e)}")
                    results[frame_idx] = {'error': str(e)}
                    
        return results
        
    def _analyze_temporal_patterns(self, 
                                 frame_results: Dict[int, Dict[str, Any]], 
                                 fps: float) -> Dict[str, Any]:
        """
        Analyzes temporal patterns and transitions in the video.
        """
        temporal_analysis = {
            'scene_changes': self._detect_scene_changes(frame_results),
            'content_flow': self._analyze_content_flow(frame_results),
            'pacing': self._analyze_pacing(frame_results, fps),
            'consistency': self._analyze_consistency(frame_results)
        }
        
        return temporal_analysis
        
    def _detect_scene_changes(self, 
                            frame_results: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detects major scene changes in the video.
        """
        scene_changes = []
        prev_frame_idx = None
        prev_results = None
        
        for frame_idx, results in sorted(frame_results.items()):
            if prev_results is not None:
                if self._is_scene_change(prev_results, results):
                    scene_changes.append({
                        'frame': frame_idx,
                        'transition_type': self._classify_transition(prev_results, results)
                    })
            prev_frame_idx = frame_idx
            prev_results = results
            
        return scene_changes
        
    def _is_scene_change(self, prev_results: Dict[str, Any], 
                        curr_results: Dict[str, Any]) -> bool:
        """
        Determines if there is a significant scene change between frames.
        """
        # Implement scene change detection logic based on multiple metrics
        quality_diff = abs(
            prev_results.get('quality', {}).get('score', 0) - 
            curr_results.get('quality', {}).get('score', 0)
        )
        
        return quality_diff > 0.3  # Threshold for scene change
        
    def _analyze_content_flow(self, 
                            frame_results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the flow and progression of content throughout the video.
        """
        return {
            'flow_score': self._calculate_flow_score(frame_results),
            'transitions': self._analyze_transitions(frame_results),
            'narrative_coherence': self._analyze_narrative_coherence(frame_results)
        }
        
    def _analyze_pacing(self, frame_results: Dict[int, Dict[str, Any]], 
                       fps: float) -> Dict[str, Any]:
        """
        Analyzes the pacing and rhythm of the video.
        """
        return {
            'pacing_score': self._calculate_pacing_score(frame_results, fps),
            'scene_duration_variance': self._calculate_scene_duration_variance(frame_results, fps),
            'rhythm_analysis': self._analyze_rhythm(frame_results, fps)
        }
        
    def _analyze_consistency(self, 
                           frame_results: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes the consistency of various metrics throughout the video.
        """
        return {
            'brand_consistency': self._analyze_metric_consistency(frame_results, 'brand'),
            'quality_consistency': self._analyze_metric_consistency(frame_results, 'quality'),
            'safety_consistency': self._analyze_metric_consistency(frame_results, 'safety')
        }