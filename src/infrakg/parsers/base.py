from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

from infrakg.models import Edge, Node


class ParserPlugin(ABC):
    """
    Abstract base class for all infrastructure parser plugins.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the parser (e.g., 'terraform', 'kubernetes')."""
        pass

    @abstractmethod
    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        """
        Parse the given directory for supported infrastructure files.
        Returns a tuple of (nodes, edges).
        """
        pass
