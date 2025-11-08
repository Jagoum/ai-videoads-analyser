"""
Base Agent class for the video analysis system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the base agent.
        
        Args:
            config: Configuration dictionary for the agent
        """
        self.config = config or {}
        
    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Analyze the input data and return results.
        
        Args:
            data: Input data to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        pass
    
    @abstractmethod
    def get_score(self) -> float:
        """
        Get the normalized score (0-1) for this agent's analysis.
        
        Returns:
            Float score between 0 and 1
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate the agent's configuration.
        
        Returns:
            Boolean indicating if configuration is valid
        """
        return True