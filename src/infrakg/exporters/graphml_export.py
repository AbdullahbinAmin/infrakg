import networkx as nx

from infrakg.exporters import register_exporter
from infrakg.exporters.base import GraphExporter
from infrakg.graph import InfraGraph


class GraphmlExporter(GraphExporter):
    @property
    def name(self) -> str:
        return "graphml"

    def export(self, graph: InfraGraph, output_path: str) -> None:
        # Convert dict attributes to strings for graphml compatibility
        g_copy = nx.DiGraph()
        for node, data in graph.graph.nodes(data=True):
            clean_data = {
                k: str(v) if isinstance(v, (dict, list)) else v for k, v in data.items()
            }
            g_copy.add_node(node, **clean_data)

        for u, v, data in graph.graph.edges(data=True):
            clean_data = {
                k: str(v) if isinstance(v, (dict, list)) else v for k, v in data.items()
            }
            g_copy.add_edge(u, v, **clean_data)

        nx.write_graphml(g_copy, output_path)


register_exporter(GraphmlExporter())
