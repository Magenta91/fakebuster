from abc import ABC, abstractmethod
from typing import Any
import logging


class BaseProcessor(ABC):
    """
    Base class for all text/data processors.

    To add a new processing step:
    1. Create a new file in services/processors/
    2. Subclass BaseProcessor
    3. Implement process()
    4. Chain it in the pipeline
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Transform input data and return processed output."""
        ...

    def safe_process(self, data: Any) -> Any:
        try:
            return self.process(data)
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} failed — {e}")
            return data  # pass-through on failure to not break the chain
