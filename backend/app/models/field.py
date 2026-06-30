from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

T = TypeVar("T")


class FieldValue(BaseModel, Generic[T]):
    """
    Canonical wrapper for ALL atomic values in the system.

    Every value carries:
    - value: actual extracted data
    - source: origin system (resume, linkedin, csv, etc.)
    - confidence: extraction/merge confidence score (0–1)
    - updated_at: timestamp for traceability
    """

    value: Optional[T] = None
    source: str = Field(..., description="Origin system of the value")
    confidence: float = Field(..., ge=0.0, le=1.0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "forbid",
        "frozen": True
    }

    def __repr__(self) -> str:
        return (
            f"FieldValue(value={self.value}, "
            f"source={self.source}, "
            f"confidence={self.confidence})"
        )