"""
Base Agent class for the BrandAI critique system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    Abstract base class for all critique agents.
    """
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initializes the agent with a configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary for the agent.
        """
        self.config = config or {}

    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Analyzes the input data and returns a critique.

        Args:
            data (Any): The input data to be analyzed (e.g., a video frame).

        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.
        """
        pass

    @abstractmethod
    def get_score(self) -> float:
        """
        Returns the overall score of the analysis.

        Returns:
            float: A score between 0 and 1.
        """
        pass