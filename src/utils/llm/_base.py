from abc import ABC, abstractmethod


class LLM(ABC):
    """
    Abstract base class for Large Language Model (LLM) interfaces.
    """

    @abstractmethod
    def _setup(self, **kwargs):
        """
        Set up the LLM client and configuration.
        """
        pass

    @abstractmethod
    def generate(self, **kwargs):
        """
        Generate content using the LLM.
        """
        pass

    @abstractmethod
    def _parse_output(self, **kwargs):
        """
        Parse the output from the LLM response.
        """
        pass
