import re
from pathlib import Path
from typing import Any, List, Tuple

import hcl2

from infrakg.models import Edge, Node
from infrakg.parsers import register_parser
from infrakg.parsers.base import ParserPlugin


class TerraformParser(ParserPlugin):
    @property
    def name(self) -> str:
        return "terraform"

    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        nodes = []
        edges = []

        # Matches typical terraform references like: aws_vpc.main.id or aws_subnet.public
        # Also handles data sources: data.aws_vpc.selected.id
        ref_pattern = re.compile(
            r"\b([a-zA-Z_][a-zA-Z0-9_-]*)\.([a-zA-Z_][a-zA-Z0-9_-]*)(?:\.[a-zA-Z0-9_-]+)?\b"
        )

        for tf_file in directory.rglob("*.tf"):
            try:
                with open(tf_file, "r", encoding="utf-8") as f:
                    parsed = hcl2.load(f)
            except Exception as e:
                print(f"Failed to parse {tf_file}: {e}")
                continue

            # Parse resources
            if "resource" in parsed:
                for res_dict in parsed["resource"]:
                    for res_type, res_blocks in res_dict.items():
                        for res_name, res_attrs in res_blocks.items():
                            clean_type = res_type.strip("\"'")
                            clean_name = res_name.strip("\"'")
                            node_id = f"{clean_type}.{clean_name}"
                            node = Node(
                                id=node_id,
                                type=clean_type,
                                name=clean_name,
                                source=self.name,
                                file_path=str(tf_file),
                                attributes=res_attrs,
                            )
                            nodes.append(node)

                            # Extract edges by looking for dependencies in attributes
                            self._extract_edges(node_id, res_attrs, ref_pattern, edges)

                            # Handle explicit depends_on
                            if "depends_on" in res_attrs:
                                for dep in res_attrs["depends_on"]:
                                    # dep is usually a list of references or a single reference string
                                    # Example: ["aws_vpc.main"] or [aws_vpc.main]
                                    # hcl2 might parse it directly as a string or list
                                    dep_str = str(dep)
                                    clean_dep = dep_str.strip("[]'\"")
                                    if clean_dep:
                                        edges.append(
                                            Edge(source_id=node_id, target_id=clean_dep)
                                        )

            # Parse data sources similarly if needed
            if "data" in parsed:
                for data_dict in parsed["data"]:
                    for data_type, data_blocks in data_dict.items():
                        for data_name, data_attrs in data_blocks.items():
                            node_id = f"data.{data_type}.{data_name}"
                            node = Node(
                                id=node_id,
                                type=f"data.{data_type}",
                                name=data_name,
                                source=self.name,
                                file_path=str(tf_file),
                                attributes=data_attrs,
                            )
                            nodes.append(node)
                            self._extract_edges(node_id, data_attrs, ref_pattern, edges)

        return nodes, edges

    def _extract_edges(
        self, node_id: str, attrs: Any, pattern: re.Pattern, edges: List[Edge]
    ):
        """Recursively search for string references indicating dependencies."""
        if isinstance(attrs, dict):
            for k, v in attrs.items():
                if k == "depends_on":
                    continue  # handled separately
                self._extract_edges(node_id, v, pattern, edges)
        elif isinstance(attrs, list):
            for item in attrs:
                self._extract_edges(node_id, item, pattern, edges)
        elif isinstance(attrs, str):
            # Look for terraform interpolation syntax
            matches = pattern.findall(attrs)
            for match in matches:
                # match is a tuple (type, name), e.g., ("aws_vpc", "main")
                if match[0] in ["var", "local", "module", "data"]:
                    # for data sources, it should be data.type.name
                    # we can map it but let's keep it simple
                    continue

                target_id = f"{match[0]}.{match[1]}"
                # basic filtering for common false positives
                if target_id != node_id and len(target_id) > 3:
                    edges.append(Edge(source_id=node_id, target_id=target_id))


register_parser(TerraformParser())
