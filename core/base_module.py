from abc import ABC, abstractmethod
import numpy as np

class BaseModule(ABC):
    """
    Abstract Base Class for all AI Modules.
    Ensures a consistent interface across the plugin-based system.
    """

    def __init__(self, name: str, config: dict = None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)

    @abstractmethod
    def process(self, frame: np.ndarray) -> dict:
        """
        Process the input frame and return results as a dictionary.
        """
        pass

    @abstractmethod
    def draw(self, frame: np.ndarray, results: dict) -> np.ndarray:
        """
        Draw visual overlays on the frame based on process results.
        """
        pass
