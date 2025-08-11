# Workflow domain model
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

class Workflow(BaseModel):
    """
    JSON-LD compatible Workflow metamodel.

    Represents the structure of a Workflow type for the metadata registry.
    This is a metamodel (a blueprint), not a concrete workflow instance.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for this workflow metamodel.")
    name: str = Field(..., description="Human-readable name for the workflow type.")
    description: Optional[str] = Field(None, description="Optional description of the workflow type.")
    component_ids: List[UUID] = Field(default_factory=list, description="List of component metamodel UUIDs that make up this workflow.")
    
    @property
    def __jsonld__(self):
        return {
            "@context": "https://schema.org",
            "@type": "Workflow",
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "component_ids": [str(cid) for cid in self.component_ids],
        }
