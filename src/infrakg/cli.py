import typer
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table

from infrakg.graph import InfraGraph
from infrakg.parsers import parse_all
from infrakg.exporters import get_exporter

app = typer.Typer(help="InfraKG - Infrastructure Knowledge Graph CLI")
console = Console()

def build_graph_from_dir(directory: Path) -> InfraGraph:
    nodes, edges = parse_all(directory)
    graph = InfraGraph()
    for node in nodes:
        graph.add_node(node)
    for edge in edges:
        graph.add_edge(edge)
    return graph

@app.command()
def scan(directory: Path = typer.Argument(..., help="Directory containing infrastructure files")):
    """Scan directory and print found resources and dependencies."""
    console.print(f"Scanning [bold green]{directory}[/bold green]...")
    nodes, edges = parse_all(directory)
    console.print(f"Found [bold blue]{len(nodes)}[/bold blue] resources and [bold blue]{len(edges)}[/bold blue] dependencies.")

@app.command()
def graph(directory: Path = typer.Argument(..., help="Directory containing infrastructure files")):
    """Build the graph and show a summary."""
    graph = build_graph_from_dir(directory)
    summary = graph.summary()
    
    table = Table(title="Graph Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    for k, v in summary.items():
        table.add_row(k.replace("_", " ").title(), str(v))
        
    console.print(table)

@app.command()
def impact(
    directory: Path = typer.Argument(..., help="Directory containing infrastructure files"),
    resource: str = typer.Option(..., "--resource", "-r", help="Resource ID to analyze impact for")
):
    """Analyze the impact of changing a specific resource."""
    graph = build_graph_from_dir(directory)
    impacted = graph.get_impact(resource)
    
    if not impacted:
        console.print(f"No impact found or resource [bold red]{resource}[/bold red] does not exist/has no dependencies.")
        return
        
    console.print(f"Impact Analysis for [bold yellow]{resource}[/bold yellow]:")
    for item in impacted:
        console.print(f"  - {item}")

@app.command()
def export(
    directory: Path = typer.Argument(..., help="Directory containing infrastructure files"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, graphml, neo4j)"),
    output: str = typer.Option("graph_output", "--output", "-o", help="Output file path")
):
    """Export the knowledge graph to a specific format."""
    graph = build_graph_from_dir(directory)
    
    if not output.endswith(f".{format}") and format != "neo4j":
        output = f"{output}.{format}"
    elif format == "neo4j" and not output.endswith(".cypher"):
        output = f"{output}.cypher"
        
    try:
        exporter = get_exporter(format)
        exporter.export(graph, output)
        console.print(f"Successfully exported graph to [bold green]{output}[/bold green] using [bold blue]{format}[/bold blue] format.")
    except Exception as e:
        console.print(f"[bold red]Export failed:[/bold red] {e}")

if __name__ == "__main__":
    app()
