from infrakg.graph import InfraGraph


def test_add_node(sample_graph: InfraGraph):
    assert sample_graph.get_node("aws_vpc.main") is not None
    assert "aws_vpc.main" in sample_graph.graph


def test_find_orphans(sample_graph: InfraGraph):
    orphans = sample_graph.find_orphans()
    assert "orphan_resource" in orphans
    assert "aws_vpc.main" not in orphans  # it has an edge from subnet
    assert "aws_subnet.public" not in orphans
    assert "aws_instance.web" not in orphans


def test_circular_dependencies(sample_graph: InfraGraph):
    cycles = sample_graph.find_circular_dependencies()
    # cycles should contain the [cycle_a, cycle_b] loop
    found = False
    for c in cycles:
        if set(c) == {"cycle_a", "cycle_b"}:
            found = True
            break
    assert found


def test_get_impact(sample_graph: InfraGraph):
    # If we change aws_vpc.main, it impacts aws_subnet.public and aws_instance.web
    impacted = sample_graph.get_impact("aws_vpc.main")
    assert "aws_subnet.public" in impacted
    assert "aws_instance.web" in impacted
    assert "orphan_resource" not in impacted
