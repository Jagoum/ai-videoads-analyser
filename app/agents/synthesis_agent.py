"""
Synthesis Agent for combining the results of all critique agents.
"""
from typing import Any, Dict, List
from .base_agent import BaseAgent

class SynthesisAgent(BaseAgent):
    """
    Aggregates results from other agents into a final scorecard.
    """
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.score = 0.0
        self.results = {}

    def analyze(self, agent_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes the results from all critique agents.

        Args:
            agent_results (Dict[str, Dict[str, Any]]): A dictionary of results
                from the other agents.

        Returns:
            Dict[str, Any]: The final, synthesized scorecard.
        """
        self.results = agent_results
        self.score = self._calculate_overall_score()
        
        return self.get_scorecard()

    def get_score(self) -> float:
        """
        Returns the final, overall score for the ad.
        """
        return self.score

    def get_scorecard(self) -> Dict[str, Any]:
        """
        Constructs the final scorecard.
        """
        return {
            'overall_score': self.score,
            'category_scores': {
                'brand_alignment': self.results.get('brand', {}).get('score', 0),
                'visual_quality': self.results.get('quality', {}).get('score', 0),
                'message_clarity': self.results.get('clarity', {}).get('score', 0),
                'safety_and_ethics': self.results.get('safety', {}).get('score', 0),
            },
            'details': self.results
        }

    def _calculate_overall_score(self) -> float:
        """
        Calculates the weighted average of all agent scores.
        """
        weights = self.config.get('synthesis_weights', {
            'brand': 0.4,
            'quality': 0.3,
            'clarity': 0.2,
            'safety': 0.1
        })
        
        total_score = 0
        for agent_name, result in self.results.items():
            total_score += result.get('score', 0) * weights.get(agent_name, 0)
            
        return float(total_score)