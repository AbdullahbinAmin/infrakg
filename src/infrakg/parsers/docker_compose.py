from pathlib import Path
from typing import List, Tuple

import yaml

from infrakg.models import Edge, Node
from infrakg.parsers import register_parser
from infrakg.parsers.base import ParserPlugin


class DockerComposeParser(ParserPlugin):
    @property
    def name(self) -> str:
        return "docker_compose"

    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        nodes = []
        edges = []

        # Find docker-compose.yml or docker-compose.yaml
        for yaml_file in directory.rglob("docker-compose*.y*ml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            except Exception as e:
                print(f"Failed to parse {yaml_file}: {e}")
                continue

            if not doc or not isinstance(doc, dict):
                continue

            services = doc.get("services", {})
            for svc_name, svc_attrs in services.items():
                node_id = f"docker.service.{svc_name}"
                node = Node(
                    id=node_id,
                    type="docker_service",
                    name=svc_name,
                    source=self.name,
                    file_path=str(yaml_file),
                    attributes=svc_attrs or {},
                )
                nodes.append(node)

                if svc_attrs and isinstance(svc_attrs, dict):
                    # explicit depends_on
                    depends_on = svc_attrs.get("depends_on", [])
                    if isinstance(depends_on, list):
                        for dep in depends_on:
                            edges.append(
                                Edge(
                                    source_id=node_id, target_id=f"docker.service.{dep}"
                                )
                            )
                    elif isinstance(depends_on, dict):
                        for dep in depends_on.keys():
                            edges.append(
                                Edge(
                                    source_id=node_id, target_id=f"docker.service.{dep}"
                                )
                            )

                    # implicit dependencies: networks
                    networks = svc_attrs.get("networks", [])
                    if isinstance(networks, list):
                        for net in networks:
                            edges.append(
                                Edge(
                                    source_id=node_id, target_id=f"docker.network.{net}"
                                )
                            )
                    elif isinstance(networks, dict):
                        for net in networks.keys():
                            edges.append(
                                Edge(
                                    source_id=node_id, target_id=f"docker.network.{net}"
                                )
                            )

                    # implicit dependencies: volumes
                    volumes = svc_attrs.get("volumes", [])
                    if isinstance(volumes, list):
                        for vol in volumes:
                            if isinstance(vol, str) and ":" in vol:
                                source_vol = vol.split(":")[0]
                                # Only link to named volumes, skip bind mounts (starts with . or /)
                                if not source_vol.startswith((".", "/", "~")):
                                    edges.append(
                                        Edge(
                                            source_id=node_id,
                                            target_id=f"docker.volume.{source_vol}",
                                        )
                                    )

            networks = doc.get("networks", {})
            for net_name, net_attrs in networks.items():
                nodes.append(
                    Node(
                        id=f"docker.network.{net_name}",
                        type="docker_network",
                        name=net_name,
                        source=self.name,
                        file_path=str(yaml_file),
                        attributes=net_attrs or {},
                    )
                )

            volumes = doc.get("volumes", {})
            for vol_name, vol_attrs in volumes.items():
                nodes.append(
                    Node(
                        id=f"docker.volume.{vol_name}",
                        type="docker_volume",
                        name=vol_name,
                        source=self.name,
                        file_path=str(yaml_file),
                        attributes=vol_attrs or {},
                    )
                )

        return nodes, edges


register_parser(DockerComposeParser())
