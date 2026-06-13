import json

import networkx as nx

from infrakg.exporters import register_exporter
from infrakg.exporters.base import GraphExporter
from infrakg.graph import InfraGraph


class JsonExporter(GraphExporter):
    @property
    def name(self) -> str:
        return "json"

    def export(self, graph: InfraGraph, output_path: str) -> None:
        data = nx.node_link_data(graph.graph)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


register_exporter(JsonExporter())
