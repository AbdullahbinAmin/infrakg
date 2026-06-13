import networkx as nx
from typing import List, Set, Dict, Any, Optional
from infrakg.models import Node, Edge

class InfraGraph:
    """
    Core graph engine managing the infrastructure dependency graph using NetworkX.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node):
        """Add a resource node to the graph."""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.model_dump())

    def add_edge(self, edge: Edge):
        """Add a dependency edge to the graph. Source depends on Target."""
        # Ensure nodes exist
        if edge.source_id not in self.graph:
            self.graph.add_node(edge.source_id, id=edge.source_id, name="Unknown", type="unknown", source="unknown", attributes={})
        if edge.target_id not in self.graph:
            self.graph.add_node(edge.target_id, id=edge.target_id, name="Unknown", type="unknown", source="unknown", attributes={})
            
        self.graph.add_edge(edge.source_id, edge.target_id, **edge.model_dump())

    def get_node(self, node_id: str) -> Optional[Node]:
        """Retrieve a node by its ID."""
        return self.nodes.get(node_id)

    def find_orphans(self) -> List[str]:
        """
        Find isolated nodes (no incoming or outgoing edges).
        """
        orphans = []
        for node in self.graph.nodes():
            if self.graph.degree(node) == 0:
                orphans.append(node)
        return orphans

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Detect cycles in the dependency graph.
        Returns a list of cycles, where each cycle is a list of node IDs.
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def get_impact(self, node_id: str) -> Set[str]:
        """
        Find all resources that depend (directly or indirectly) on the given node.
        Since edges are defined as A -> depends on -> B,
        if B changes, we need to find everything that can reach B.
        In a directed graph where edges are dependencies (source -> target),
        the impact of 'target' is the set of all ancestors of 'target'.
        """
        if node_id not in self.graph:
            return set()
            
        # Ancestors are nodes that have a path to the given node
        impacted_nodes = nx.ancestors(self.graph, node_id)
        return impacted_nodes

    def summary(self) -> Dict[str, Any]:
        """
        Provide a summary of the graph metrics.
        """
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "orphans_count": len(self.find_orphans()),
            "cycles_count": len(self.find_circular_dependencies())
        }
