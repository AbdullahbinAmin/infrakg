from pathlib import Path
from typing import List, Tuple

import yaml

from infrakg.models import Edge, Node
from infrakg.parsers import register_parser
from infrakg.parsers.base import ParserPlugin


class GithubActionsParser(ParserPlugin):
    @property
    def name(self) -> str:
        return "github_actions"

    def parse(self, directory: Path) -> Tuple[List[Node], List[Edge]]:
        nodes = []
        edges = []

        workflows_dir = directory / ".github" / "workflows"
        if not workflows_dir.exists():
            return nodes, edges

        for yaml_file in workflows_dir.rglob("*.y*ml"):
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    doc = yaml.safe_load(f)
            except Exception as e:
                print(f"Failed to parse {yaml_file}: {e}")
                continue

            if not doc or not isinstance(doc, dict):
                continue

            workflow_name = doc.get("name", yaml_file.stem)
            wf_node_id = f"gha.workflow.{workflow_name}"

            nodes.append(
                Node(
                    id=wf_node_id,
                    type="github_workflow",
                    name=workflow_name,
                    source=self.name,
                    file_path=str(yaml_file),
                    attributes={"on": doc.get("on")},
                )
            )

            jobs = doc.get("jobs", {})
            for job_id, job_attrs in jobs.items():
                job_node_id = f"gha.job.{workflow_name}.{job_id}"
                nodes.append(
                    Node(
                        id=job_node_id,
                        type="github_job",
                        name=job_id,
                        source=self.name,
                        file_path=str(yaml_file),
                        attributes=job_attrs or {},
                    )
                )

                # Every job implicitly depends on the workflow itself (belongs to)
                edges.append(
                    Edge(source_id=job_node_id, target_id=wf_node_id, type="belongs_to")
                )

                if job_attrs and isinstance(job_attrs, dict):
                    needs = job_attrs.get("needs", [])
                    if isinstance(needs, str):
                        needs = [needs]

                    for dep in needs:
                        dep_node_id = f"gha.job.{workflow_name}.{dep}"
                        edges.append(
                            Edge(
                                source_id=job_node_id,
                                target_id=dep_node_id,
                                type="needs",
                            )
                        )

        return nodes, edges


register_parser(GithubActionsParser())
