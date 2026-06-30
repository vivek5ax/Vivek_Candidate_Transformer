from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class ParserMetadata(BaseModel):
    """
    Metadata capturing the execution and provenance context of a parsing operation.
    """
    source_type: str = Field(..., description="Type of source: csv, resume_pdf, ats_json, etc.")
    file_name: Optional[str] = Field(None, description="Path or identifier of input source")
    parse_status: str = Field(default="SUCCESS", description="SUCCESS | PARTIAL | ERROR")
    warnings: List[str] = Field(default_factory=list, description="Warnings generated during parsing")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_source_id: Optional[str] = Field(None, description="Unique source ingestion ID")
