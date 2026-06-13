from typing import List, Tuple
from pathlib import Path
import importlib
import pkgutil

from infrakg.models import Node, Edge
from infrakg.parsers.base import ParserPlugin

# Will be populated with parser instances
_PARSERS: List[ParserPlugin] = []

def register_parser(parser: ParserPlugin):
    _PARSERS.append(parser)

def load_parsers():
    """Dynamically load all parsers in this package."""
    if _PARSERS:
        return
        
    import infrakg.parsers
    for _, module_name, _ in pkgutil.iter_modules(infrakg.parsers.__path__):
        if module_name != "base":
            importlib.import_module(f"infrakg.parsers.{module_name}")

def parse_all(directory: Path) -> Tuple[List[Node], List[Edge]]:
    """
    Run all registered parsers against the directory.
    """
    load_parsers()
    all_nodes = []
    all_edges = []
    for parser in _PARSERS:
        nodes, edges = parser.parse(directory)
        all_nodes.extend(nodes)
        all_edges.extend(edges)
    return all_nodes, all_edges
