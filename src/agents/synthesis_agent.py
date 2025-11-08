"""
Synthesis Agent for combining analyses and generating final recommendations.
"""
from typing import Any, Dict, List
import numpy as np
from .base_agent import BaseAgent

class SynthesisAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.final_score = 0.0
        self.synthesis_results = {}
        
    def analyze(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize results from all agents and generate final analysis.
        
        Args:
            agent_results: Dictionary containing results from all agents
            
        Returns:
            Dictionary containing synthesized analysis and recommendations
        """
        # Calculate overall score
        scores = self._extract_scores(agent_results)
        self.final_score = self._calculate_final_score(scores)
        
        # Generate synthesis
        synthesis = {
            'overall_score': self.final_score,
            'component_scores': scores,
            'critical_issues': self._identify_critical_issues(agent_results),
            'recommendations': self._generate_recommendations(agent_results),
            'improvement_priority': self._prioritize_improvements(agent_results),
            'deployment_decision': self._make_deployment_decision()
        }
        
        self.synthesis_results = synthesis
        return synthesis
    
    def get_score(self) -> float:
        """
        Get the final synthesized score.
        
        Returns:
            Float score between 0 and 1
        """
        return self.final_score
    
    def _extract_scores(self, agent_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract scores from each agent's results."""
        return {
            'visual_quality': agent_results.get('visual_quality', {}).get('score', 0.0),
            'brand_compliance': agent_results.get('brand_compliance', {}).get('score', 0.0),
            'safety': agent_results.get('safety', {}).get('score', 0.0),
            'message_clarity': agent_results.get('message_clarity', {}).get('score', 0.0)
        }
    
    def _calculate_final_score(self, scores: Dict[str, float]) -> float:
        """Calculate final weighted score."""
        weights = {
            'visual_quality': 0.25,
            'brand_compliance': 0.30,
            'safety': 0.25,
            'message_clarity': 0.20
        }
        
        weighted_score = sum(
            scores[key] * weights[key]
            for key in weights
        )
        
        return min(max(weighted_score, 0.0), 1.0)
    
    def _identify_critical_issues(self, agent_results: Dict[str, Any]) -> List[str]:
        """Identify critical issues that need immediate attention."""
        critical_issues = []
        
        # Safety issues
        safety_results = agent_results.get('safety', {})
        if safety_results.get('score', 1.0) < 0.8:
            critical_issues.extend(safety_results.get('flags', []))
            
        # Brand compliance issues
        brand_results = agent_results.get('brand_compliance', {})
        if brand_results.get('score', 1.0) < 0.7:
            critical_issues.extend(brand_results.get('violations', []))
            
        # Message clarity issues
        message_results = agent_results.get('message_clarity', {})
        if message_results.get('score', 1.0) < 0.6:
            critical_issues.extend(message_results.get('suggestions', []))
            
        return critical_issues
    
    def _generate_recommendations(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        # Visual quality recommendations
        visual_results = agent_results.get('visual_quality', {})
        if visual_results.get('score', 1.0) < 0.8:
            metrics = visual_results.get('metrics', {})
            for metric, value in metrics.items():
                if value < 0.7:
                    recommendations.append({
                        'category': 'visual_quality',
                        'component': metric,
                        'priority': 'high' if value < 0.5 else 'medium',
                        'suggestion': f"Improve {metric.replace('_', ' ')} quality"
                    })
        
        # Brand compliance recommendations
        brand_results = agent_results.get('brand_compliance', {})
        if brand_results.get('score', 1.0) < 0.8:
            for violation in brand_results.get('violations', []):
                recommendations.append({
                    'category': 'brand_compliance',
                    'component': 'brand_guidelines',
                    'priority': 'high',
                    'suggestion': f"Address brand violation: {violation}"
                })
        
        # Message clarity recommendations
        message_results = agent_results.get('message_clarity', {})
        if message_results.get('score', 1.0) < 0.8:
            for suggestion in message_results.get('suggestions', []):
                recommendations.append({
                    'category': 'message_clarity',
                    'component': 'messaging',
                    'priority': 'medium',
                    'suggestion': suggestion
                })
        
        return recommendations
    
    def _prioritize_improvements(self, agent_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize areas for improvement."""
        scores = self._extract_scores(agent_results)
        priorities = []
        
        for category, score in scores.items():
            if score < 0.8:
                priority_level = self._determine_priority_level(score)
                priorities.append({
                    'category': category,
                    'current_score': score,
                    'priority_level': priority_level,
                    'target_score': min(score + 0.2, 1.0),
                    'impact': self._estimate_improvement_impact(category, score)
                })
        
        # Sort by priority level and potential impact
        priorities.sort(key=lambda x: (
            -self._priority_to_number(x['priority_level']),
            -x['impact']
        ))
        
        return priorities
    
    def _determine_priority_level(self, score: float) -> str:
        """Determine priority level based on score."""
        if score < 0.6:
            return 'critical'
        elif score < 0.7:
            return 'high'
        elif score < 0.8:
            return 'medium'
        else:
            return 'low'
    
    def _priority_to_number(self, priority: str) -> int:
        """Convert priority level to numeric value for sorting."""
        priority_map = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(priority, 0)
    
    def _estimate_improvement_impact(self, category: str, current_score: float) -> float:
        """Estimate the potential impact of improving a category."""
        # Impact is higher for lower scores and critical categories
        base_impact = 1.0 - current_score
        
        # Category weights
        category_weights = {
            'safety': 1.5,  # Safety issues are most critical
            'brand_compliance': 1.3,
            'message_clarity': 1.2,
            'visual_quality': 1.0
        }
        
        return base_impact * category_weights.get(category, 1.0)
    
    def _make_deployment_decision(self) -> Dict[str, Any]:
        """Make a decision about whether the ad is ready for deployment."""
        scores = self.synthesis_results['component_scores']
        critical_issues = self.synthesis_results['critical_issues']
        
        # Define thresholds
        thresholds = {
            'safety': 0.95,  # Safety must be nearly perfect
            'brand_compliance': 0.85,
            'message_clarity': 0.80,
            'visual_quality': 0.75
        }
        
        # Check if any scores are below thresholds
        below_threshold = [
            category for category, threshold in thresholds.items()
            if scores.get(category, 0.0) < threshold
        ]
        
        # Make decision
        if critical_issues or below_threshold:
            decision = {
                'ready': False,
                'blocking_issues': critical_issues,
                'below_threshold': below_threshold,
                'recommendation': 'Revision needed before deployment'
            }
        else:
            decision = {
                'ready': True,
                'confidence': min(self.final_score, 1.0),
                'recommendation': 'Approved for deployment'
            }
            
        return decision