from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class Node(BaseModel):
    """
    Represents an infrastructure resource in the knowledge graph.
    """

    id: str = Field(
        ..., description="Unique identifier for the resource (e.g., 'aws_instance.web')"
    )
    type: str = Field(
        ..., description="Type of the resource (e.g., 'aws_instance', 'Deployment')"
    )
    name: str = Field(..., description="Name of the resource")
    source: str = Field(
        ..., description="Source system (e.g., 'terraform', 'kubernetes')"
    )
    file_path: Optional[str] = Field(
        None, description="Path to the file defining this resource"
    )
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional attributes or metadata"
    )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        return self.id == other.id


class Edge(BaseModel):
    """
    Represents a dependency between two resources.
    source -> depends on -> target
    """

    source_id: str = Field(
        ..., description="ID of the resource that depends on another"
    )
    target_id: str = Field(..., description="ID of the resource being depended upon")
    type: str = Field("depends_on", description="Type of relationship")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the relationship"
    )

    def __hash__(self) -> int:
        return hash((self.source_id, self.target_id, self.type))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        return (self.source_id, self.target_id, self.type) == (
            other.source_id,
            other.target_id,
            other.type,
        )
