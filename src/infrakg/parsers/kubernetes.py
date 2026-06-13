from pathlib import Path
from typing import List, Tuple

import yaml

from infrakg.models import Edge, Node
from infrakg.parsers import register_parser
from infrakg.parsers.base import ParserPlugin


class KubernetesParser(ParserPlugin):
    @property
    def name(self) -> str:
        return "kubernetes"

    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        nodes = []
        edges = []

        for yaml_file in directory.rglob("*.yaml"):
            if ".github" in str(yaml_file):  # Skip github actions
                continue

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    # K8s files can have multiple documents
                    docs = list(yaml.safe_load_all(f))
            except Exception as e:
                print(f"Failed to parse {yaml_file}: {e}")
                continue

            for doc in docs:
                if not doc or not isinstance(doc, dict):
                    continue

                kind = doc.get("kind")
                metadata = doc.get("metadata", {})
                name = metadata.get("name")

                if not kind or not name:
                    continue

                node_id = f"k8s.{kind}.{name}"
                node = Node(
                    id=node_id,
                    type=kind,
                    name=name,
                    source=self.name,
                    file_path=str(yaml_file),
                    attributes=doc,
                )
                nodes.append(node)

                # Extract implicit dependencies based on common K8s patterns

                # Deployments, StatefulSets depend on ConfigMaps, Secrets, PVCs
                spec = doc.get("spec", {})
                template = spec.get("template", {})
                pod_spec = template.get(
                    "spec", spec
                )  # Use template spec if present, else root spec (e.g. for Pods)

                if "volumes" in pod_spec:
                    for vol in pod_spec["volumes"]:
                        if "configMap" in vol:
                            cm_name = vol["configMap"].get("name")
                            if cm_name:
                                edges.append(
                                    Edge(
                                        source_id=node_id,
                                        target_id=f"k8s.ConfigMap.{cm_name}",
                                    )
                                )
                        elif "secret" in vol:
                            secret_name = vol["secret"].get("secretName")
                            if secret_name:
                                edges.append(
                                    Edge(
                                        source_id=node_id,
                                        target_id=f"k8s.Secret.{secret_name}",
                                    )
                                )
                        elif "persistentVolumeClaim" in vol:
                            pvc_name = vol["persistentVolumeClaim"].get("claimName")
                            if pvc_name:
                                edges.append(
                                    Edge(
                                        source_id=node_id,
                                        target_id=f"k8s.PersistentVolumeClaim.{pvc_name}",
                                    )
                                )

                # Ingress depends on Services
                if kind == "Ingress":
                    rules = spec.get("rules", [])
                    for rule in rules:
                        http = rule.get("http", {})
                        paths = http.get("paths", [])
                        for path in paths:
                            backend = path.get("backend", {})
                            service = backend.get("service", {})
                            svc_name = service.get("name")
                            if svc_name:
                                edges.append(
                                    Edge(
                                        source_id=node_id,
                                        target_id=f"k8s.Service.{svc_name}",
                                    )
                                )

                # Service depends on pods matching selector, but that's a bit dynamic.
                # We won't model selector-based edges right now unless explicit.

        return nodes, edges


register_parser(KubernetesParser())
