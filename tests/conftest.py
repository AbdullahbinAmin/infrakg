import pytest
from infrakg.graph import InfraGraph
from infrakg.models import Node, Edge

@pytest.fixture
def sample_graph():
    graph = InfraGraph()
    
    # Create some nodes
    n1 = Node(id="aws_vpc.main", type="aws_vpc", name="main", source="terraform")
    n2 = Node(id="aws_subnet.public", type="aws_subnet", name="public", source="terraform")
    n3 = Node(id="aws_instance.web", type="aws_instance", name="web", source="terraform")
    n4 = Node(id="orphan_resource", type="orphan", name="orphan", source="terraform")
    
    # Create a cycle
    n5 = Node(id="cycle_a", type="test", name="a", source="test")
    n6 = Node(id="cycle_b", type="test", name="b", source="test")
    
    for n in [n1, n2, n3, n4, n5, n6]:
        graph.add_node(n)
        
    # subnet depends on vpc
    graph.add_edge(Edge(source_id=n2.id, target_id=n1.id))
    # instance depends on subnet
    graph.add_edge(Edge(source_id=n3.id, target_id=n2.id))
    
    # add cycle
    graph.add_edge(Edge(source_id=n5.id, target_id=n6.id))
    graph.add_edge(Edge(source_id=n6.id, target_id=n5.id))
    
    return graph
