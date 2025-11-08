"""
Core Video Analyzer class that orchestrates the multi-agent analysis system.
"""
import os
import json
from typing import Any, Dict, List
import cv2
import numpy as np
from .agents.visual_quality_agent import VisualQualityAgent
from .agents.brand_compliance_agent import BrandComplianceAgent
from .agents.safety_agent import SafetyAgent
from .agents.message_agent import MessageAgent
from .agents.synthesis_agent import SynthesisAgent

class VideoAnalyzer:
    def __init__(self, brand_config_path: str = None):
        """
        Initialize the Video Analyzer system.
        
        Args:
            brand_config_path: Path to brand configuration JSON file
        """
        self.brand_config = self._load_brand_config(brand_config_path)
        self._initialize_agents()
        
    def analyze_video(self, video_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Analyze a video file using the multi-agent system.
        
        Args:
            video_path: Path to the video file
            output_path: Optional path to save the analysis results
            
        Returns:
            Dictionary containing complete analysis results
        """
        # Load video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        try:
            # Extract frames and perform analysis
            frames = self._extract_frames(cap)
            results = self._analyze_frames(frames)
            
            # Save results if output path provided
            if output_path:
                self._save_results(results, output_path)
                
            return results
            
        finally:
            cap.release()
    
    def analyze_batch(self, input_dir: str, output_dir: str) -> List[Dict[str, Any]]:
        """
        Analyze multiple videos in a directory.
        
        Args:
            input_dir: Directory containing video files
            output_dir: Directory to save analysis results
            
        Returns:
            List of analysis results for each video
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for filename in os.listdir(input_dir):
            if filename.endswith(('.mp4', '.avi', '.mov')):
                video_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_analysis.json")
                
                try:
                    result = self.analyze_video(video_path, output_path)
                    results.append({
                        'video_name': filename,
                        'analysis': result
                    })
                except Exception as e:
                    print(f"Error analyzing {filename}: {str(e)}")
        
        return results
    
    def _load_brand_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load brand configuration from JSON file."""
        if not config_path:
            return {}
            
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load brand config: {str(e)}")
            return {}
    
    def _initialize_agents(self):
        """Initialize all analysis agents."""
        self.visual_agent = VisualQualityAgent(self.brand_config)
        self.brand_agent = BrandComplianceAgent(self.brand_config)
        self.safety_agent = SafetyAgent(self.brand_config)
        self.message_agent = MessageAgent(self.brand_config)
        self.synthesis_agent = SynthesisAgent(self.brand_config)
    
    def _extract_frames(self, cap: cv2.VideoCapture, max_frames: int = 30) -> List[np.ndarray]:
        """
        Extract frames from video for analysis.
        
        Args:
            cap: OpenCV VideoCapture object
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of video frames as numpy arrays
        """
        frames = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = max(1, total_frames // max_frames)
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                frames.append(frame)
                
            frame_count += 1
            
            if len(frames) >= max_frames:
                break
        
        return frames
    
    def _analyze_frames(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """
        Perform multi-agent analysis on video frames.
        
        Args:
            frames: List of video frames
            
        Returns:
            Dictionary containing analysis results from all agents
        """
        if not frames:
            raise ValueError("No frames available for analysis")
            
        # Analyze each frame with all agents
        frame_results = []
        for frame in frames:
            frame_analysis = {
                'visual_quality': self.visual_agent.analyze(frame),
                'brand_compliance': self.brand_agent.analyze(frame),
                'safety': self.safety_agent.analyze(frame),
                'message_clarity': self.message_agent.analyze(frame)
            }
            frame_results.append(frame_analysis)
        
        # Aggregate results across frames
        aggregated_results = self._aggregate_frame_results(frame_results)
        
        # Generate final synthesis
        final_results = self.synthesis_agent.analyze(aggregated_results)
        
        return {
            'frame_analysis': frame_results,
            'aggregated_results': aggregated_results,
            'final_analysis': final_results
        }
    
    def _aggregate_frame_results(self, frame_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate analysis results across all frames.
        
        Args:
            frame_results: List of per-frame analysis results
            
        Returns:
            Dictionary containing aggregated results
        """
        def aggregate_scores(key: str) -> float:
            scores = [frame[key]['score'] for frame in frame_results]
            return float(np.mean(scores))
        
        def aggregate_lists(key: str, subkey: str) -> List[str]:
            all_items = []
            for frame in frame_results:
                items = frame[key].get(subkey, [])
                if items and isinstance(items, list):
                    all_items.extend(items)
            return list(set(all_items))  # Remove duplicates
        
        return {
            'visual_quality': {
                'score': aggregate_scores('visual_quality'),
                'metrics': self._aggregate_metrics([f['visual_quality'].get('metrics', {}) for f in frame_results])
            },
            'brand_compliance': {
                'score': aggregate_scores('brand_compliance'),
                'violations': aggregate_lists('brand_compliance', 'violations')
            },
            'safety': {
                'score': aggregate_scores('safety'),
                'flags': aggregate_lists('safety', 'flags')
            },
            'message_clarity': {
                'score': aggregate_scores('message_clarity'),
                'suggestions': aggregate_lists('message_clarity', 'suggestions')
            }
        }
    
    def _aggregate_metrics(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate numeric metrics across frames."""
        if not metrics_list:
            return {}
            
        aggregated = {}
        for key in metrics_list[0].keys():
            values = [m.get(key, 0.0) for m in metrics_list]
            aggregated[key] = float(np.mean(values))
            
        return aggregated
    
    def _save_results(self, results: Dict[str, Any], output_path: str):
        """Save analysis results to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
    def get_deployment_recommendation(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get deployment recommendation based on analysis results.
        
        Args:
            results: Analysis results from analyze_video
            
        Returns:
            Dictionary containing deployment recommendation
        """
        return results['final_analysis'].get('deployment_decision', {})
    
    def get_improvement_suggestions(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get prioritized improvement suggestions.
        
        Args:
            results: Analysis results from analyze_video
            
        Returns:
            List of improvement suggestions with priorities
        """
        return results['final_analysis'].get('recommendations', [])