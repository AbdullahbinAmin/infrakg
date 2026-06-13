from typing import List
import importlib
import pkgutil

from infrakg.exporters.base import GraphExporter

_EXPORTERS: List[GraphExporter] = []

def register_exporter(exporter: GraphExporter):
    _EXPORTERS.append(exporter)

def load_exporters():
    if _EXPORTERS:
        return
        
    import infrakg.exporters
    for _, module_name, _ in pkgutil.iter_modules(infrakg.exporters.__path__):
        if module_name != "base":
            importlib.import_module(f"infrakg.exporters.{module_name}")

def get_exporter(name: str) -> GraphExporter:
    load_exporters()
    for exporter in _EXPORTERS:
        if exporter.name == name:
            return exporter
    raise ValueError(f"Exporter '{name}' not found. Available exporters: {[e.name for e in _EXPORTERS]}")
