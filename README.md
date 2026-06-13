# InfraKG (Infrastructure Knowledge Graph)

A unified dependency graph and analysis tool for DevOps infrastructure sources.

## Features

- Parse infrastructure files (Terraform, Kubernetes, Docker Compose, GitHub Actions, Ansible).
- Build a directed graph representing dependencies.
- Identify the impact of infrastructure changes.
- Export graph to JSON, GraphML, and Neo4j formats.
- Detect orphaned resources and circular dependencies.

## Installation

```bash
pip install infrakg
```

## Quick Start

```bash
# Scan a directory to build the knowledge graph
infrakg scan /path/to/infra

# Output the graph summary
infrakg graph /path/to/infra

# Check impact of modifying a specific resource
infrakg impact /path/to/infra --resource "aws_db_instance.main"

# Export the graph
infrakg export /path/to/infra --format graphml --output graph.graphml
```
