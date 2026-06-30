from pydantic import BaseModel, Field
from datetime import datetime, timezone


class SourceInfo(BaseModel):
    """
    Represents a raw data source ingested into the system.
    This is DIFFERENT from FieldValue.source.

    Example sources:
    - resume.pdf
    - linkedin_api
    - github_profile
    - csv_upload
    """

    source_id: str = Field(..., description="Unique identifier for the source")
    source_type: str = Field(..., description="resume | linkedin | github | csv | api")
    ingestion_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "forbid"
    }