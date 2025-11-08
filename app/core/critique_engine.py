"""
Core critique engine for orchestrating the analysis of video ads.
"""
from typing import Any, Dict
import numpy as np
from app.agents.brand_agent import BrandAgent
from app.agents.quality_agent import QualityAgent
from app.agents.clarity_agent import ClarityAgent
from app.agents.safety_agent import SafetyAgent
from app.agents.synthesis_agent import SynthesisAgent

class CritiqueEngine:
    """
    Orchestrates the multi-agent critique process.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the critique engine and all its agents.

        Args:
            config (Dict[str, Any]): The master configuration object.
        """
        self.config = config
        self.agents = {
            'brand': BrandAgent(config.get('brand_agent', {})),
            'quality': QualityAgent(config.get('quality_agent', {})),
            'clarity': ClarityAgent(config.get('clarity_agent', {})),
            'safety': SafetyAgent(config.get('safety_agent', {})),
            'synthesis': SynthesisAgent(config.get('synthesis_agent', {})),
        }

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
        final_scorecard = synthesis_agent.analyze(agent_results)
        
        return final_scorecard