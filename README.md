# InfraKG (Infrastructure Knowledge Graph)

![PyPI](https://img.shields.io/pypi/v/infrakg)
![Python Versions](https://img.shields.io/pypi/pyversions/infrakg)
![License](https://img.shields.io/github/license/AbdullahbinAmin/infrakg)
![CI](https://github.com/AbdullahbinAmin/infrakg/actions/workflows/ci.yml/badge.svg)

**InfraKG** is a powerful Python library and CLI tool that parses your infrastructure-as-code (IaC) and DevOps configurations to build a unified dependency graph. It helps you understand complex infrastructure relationships, detect circular dependencies, find orphaned resources, and analyze the downstream impact of your changes.

## Features

- **Multi-Source Parsing:** Unifies resources from Terraform (`.tf`), Kubernetes (`.yaml`), Docker Compose (`docker-compose.yml`), GitHub Actions workflows, and Ansible playbooks.
- **Dependency Graph:** Automatically builds a NetworkX-powered Directed Acyclic Graph (DAG) representing dependencies (both explicit and implicit).
- **Impact Analysis:** Instantly discover which downstream resources will be affected if a specific node is modified or deleted.
- **Graph Exports:** Export your infrastructure graph to standard formats like JSON, GraphML (for Gephi visualization), and Neo4j Cypher scripts.
- **Python API:** Programmatically load and analyze your infrastructure within your own custom scripts or automation pipelines.

## Installation

Install the library directly from PyPI using pip:

```bash
pip install infrakg
```

## CLI Usage

InfraKG provides a clean, intuitive CLI interface built with Typer.

### 1. Scan your infrastructure
Scan a directory to discover all resources and their relationships.
```bash
infrakg scan /path/to/your/infra
```

### 2. View Graph Statistics
Calculate and display structural metrics about your infrastructure, including total nodes, edges, orphaned resources, and detected circular dependency cycles.
```bash
infrakg graph /path/to/your/infra
```

### 3. Impact Analysis
Determine what happens when a critical piece of infrastructure changes.
```bash
infrakg impact /path/to/your/infra --resource "aws_vpc.main"
```
*Output example:*
```text
Impact Analysis for aws_vpc.main:
  - aws_subnet.public
  - aws_instance.web
```

### 4. Export to Visualizers
Export your infrastructure state to share with your team or visualize using graphing tools.
```bash
# Export to JSON
infrakg export /path/to/infra --format json --output my_infra.json

# Export to GraphML (Great for Gephi/yEd)
infrakg export /path/to/infra --format graphml --output my_infra.graphml

# Export to Neo4j (Generates Cypher scripts)
infrakg export /path/to/infra --format neo4j --output neo4j_load.cypher
```

## Python API Usage

You can seamlessly integrate InfraKG into your own Python scripts to build custom CI/CD checks or compliance rules.

```python
from pathlib import Path
from infrakg.cli import build_graph_from_dir

# 1. Build the graph from your infrastructure folder
infra_dir = Path("./my-infrastructure")
graph = build_graph_from_dir(infra_dir)

# 2. Find Orphaned Resources (resources that nothing depends on)
orphans = graph.find_orphans()
print(f"Found {len(orphans)} orphaned resources to clean up!")

# 3. Detect Circular Dependencies
cycles = graph.find_circular_dependencies()
if cycles:
    print("WARNING: Circular dependencies detected!")

# 4. Check Impact Programmatically
impacted_nodes = graph.get_impact("docker.service.database")
print(f"Modifying the database will impact: {impacted_nodes}")
```

## Supported Integrations

InfraKG relies on a scalable Plugin architecture. Current supported parsers:

- ✅ **Terraform**: Parses HCL2 to find explicit `depends_on` and implicit string interpolations.
- ✅ **Kubernetes**: Understands references between Deployments, Pods, ConfigMaps, Secrets, PVCs, and Ingress to Services.
- ✅ **Docker Compose**: Maps Services, Networks, and Volumes.
- ✅ **GitHub Actions**: Connects Workflows and Jobs based on `needs`.
- ✅ **Ansible**: Links Playbooks to their respective Roles.

## License

This project is licensed under the MIT License.
