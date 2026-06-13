from abc import ABC, abstractmethod

from infrakg.graph import InfraGraph


class GraphExporter(ABC):
    """
    Abstract base class for all graph exporters.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the exporter (e.g., 'json', 'graphml')."""
        pass

    @abstractmethod
    def export(self, graph: InfraGraph, output_path: str) -> None:
        """
        Export the graph to the specified output path.
        """
        pass
