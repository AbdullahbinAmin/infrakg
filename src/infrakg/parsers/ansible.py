import yaml
from pathlib import Path
from typing import List, Tuple

from infrakg.models import Node, Edge
from infrakg.parsers.base import ParserPlugin
from infrakg.parsers import register_parser

class AnsibleParser(ParserPlugin):
    @property
    def name(self) -> str:
        return "ansible"

    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        nodes = []
        edges = []

        # Find potential playbooks
        for yaml_file in directory.rglob("*.y*ml"):
            # skip kubernetes, github actions, docker-compose
            name_str = str(yaml_file)
            if ".github" in name_str or "docker-compose" in name_str or "kubernetes" in name_str:
                continue
                
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            except Exception as e:
                # might not be a valid yaml
                continue

            if not isinstance(doc, list):
                # Ansible playbooks are usually a list of plays
                continue
                
            is_playbook = False
            for idx, play in enumerate(doc):
                if not isinstance(play, dict):
                    continue
                    
                # Basic heuristic for a play
                if "hosts" in play and ("tasks" in play or "roles" in play):
                    is_playbook = True
                    play_name = play.get("name", f"play_{idx}")
                    play_node_id = f"ansible.playbook.{yaml_file.stem}.{play_name}"
                    
                    nodes.append(Node(
                        id=play_node_id,
                        type="ansible_play",
                        name=play_name,
                        source=self.name,
                        file_path=str(yaml_file),
                        attributes={"hosts": play.get("hosts")}
                    ))

                    # parse roles
                    roles = play.get("roles", [])
                    for role in roles:
                        role_name = role if isinstance(role, str) else role.get("role")
                        if role_name:
                            role_node_id = f"ansible.role.{role_name}"
                            nodes.append(Node(
                                id=role_node_id,
                                type="ansible_role",
                                name=role_name,
                                source=self.name,
                                file_path=str(yaml_file),
                                attributes={}
                            ))
                            edges.append(Edge(source_id=play_node_id, target_id=role_node_id, type="uses_role"))

        return nodes, edges

register_parser(AnsibleParser())
