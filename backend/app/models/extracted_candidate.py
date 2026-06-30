from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from .parser_metadata import ParserMetadata


class ExtractedCandidate(BaseModel):
    """
    Raw extracted candidate information from a single source.
    No normalization, deduplication, or conflict resolution has occurred at this stage.
    Uses standard Python primitive types (str, List[str], Dict), NOT FieldValue[T].
    """
    candidate_id: Optional[str] = None
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list, description="E.164 formatted phones")
    location: Optional[Dict[str, Optional[str]]] = Field(default=None, description="{ city, region, country }")
    links: Optional[Dict[str, Any]] = Field(default=None, description="{ linkedin, github, portfolio, other[] }")
    headline: Optional[str] = None
    years_experience: Optional[float] = None

    primary_skills: List[str] = Field(default_factory=list, description="Legacy field")
    secondary_skills: List[str] = Field(default_factory=list, description="Legacy field")
    skills: List[Dict[str, Any]] = Field(default_factory=list, description="[{ confidence, source, values[] }]")

    current_company: Optional[str] = None
    title: Optional[str] = None
    experience: List[Dict[str, Any]] = Field(default_factory=list, description="[{ company, title, start, end, summary }]")
    education: List[Dict[str, Any]] = Field(default_factory=list, description="[{ institution, degree, field, end_year }]")
    additional_details: Optional[Dict[str, Any]] = Field(default=None, description="Structured content from extra sections")

    provenance: List[Dict[str, str]] = Field(default_factory=list, description="[{ field, source, method }]")
    sources: List[str] = Field(default_factory=list, description="List of source file names used to compile this profile")
    overall_confidence: Optional[float] = None

    metadata: Optional[ParserMetadata] = None
