from abc import ABC, abstractmethod
from typing import Any

class BaseConverter(ABC):
    """Abstract base class for all format converters."""

    @abstractmethod
    def convert(self, data: Any) -> Any:
        """
        Converts data from one format to another.

        Args:
            data: The input data in the source format.

        Returns:
            The converted data in the target format.
        """
        pass