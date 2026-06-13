import json

from infrakg.exporters import register_exporter
from infrakg.exporters.base import GraphExporter
from infrakg.graph import InfraGraph


class Neo4jExporter(GraphExporter):
    @property
    def name(self) -> str:
        return "neo4j"

    def export(self, graph: InfraGraph, output_path: str) -> None:
        """
        Exports Cypher queries to load the graph into Neo4j.
        """
        queries = []
        queries.append("// Create constraints")
        queries.append(
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Resource) REQUIRE n.id IS UNIQUE;"
        )
        queries.append("")

        queries.append("// Create Nodes")
        for node_id, data in graph.graph.nodes(data=True):
            props = {
                "id": data.get("id", node_id),
                "type": data.get("type", "unknown"),
                "name": data.get("name", "unknown"),
                "source": data.get("source", "unknown"),
            }
            props_str = ", ".join(f"{k}: {json.dumps(v)}" for k, v in props.items())
            queries.append(
                f"MERGE (n:Resource {{id: {json.dumps(node_id)}}}) SET n += {{{props_str}}};"
            )

        queries.append("")
        queries.append("// Create Edges")
        for u, v, data in graph.graph.edges(data=True):
            rel_type = data.get("type", "depends_on").upper()
            # replace invalid characters in rel_type if any
            rel_type = rel_type.replace("-", "_").replace(".", "_")
            queries.append(f"MATCH (source:Resource {{id: {json.dumps(u)}}})")
            queries.append(f"MATCH (target:Resource {{id: {json.dumps(v)}}})")
            queries.append(f"MERGE (source)-[:{rel_type}]->(target);")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(queries))


register_exporter(Neo4jExporter())
