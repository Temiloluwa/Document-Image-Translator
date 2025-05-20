from abc import ABC, abstractmethod
from typing import Any, Dict


class LLM(ABC):
    @abstractmethod
    def _setup(self, **kwargs: Dict[str, Any]) -> None:
        """Set up the LLM with any necessary configurations."""
        pass

    @abstractmethod
    def generate(self, **kwargs: Dict[str, Any]) -> str:
        """Generate text based on the given prompt."""
        pass

    @abstractmethod
    def _parse_output(self, **kwargs: Dict[str, Any]) -> Any:
        """Parse LLM response"""
        pass
