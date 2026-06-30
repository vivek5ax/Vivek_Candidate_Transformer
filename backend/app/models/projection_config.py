from pydantic import BaseModel, Field
from typing import List, Optional


class ProjectedField(BaseModel):
    display_name: str
    from_path: str = Field(alias="from")
    normalize: Optional[str] = None
    classify_skills: bool = False
    sub_fields: Optional[List['ProjectedField']] = None

ProjectedField.model_rebuild()


class ProjectedSection(BaseModel):
    section_name: str
    from_array: Optional[str] = None
    fields: List[ProjectedField]


class ProjectionConfig(BaseModel):
    provenance_filters: List[str] = Field(default_factory=lambda: ["source", "method", "value", "raw_value"])
    sections: List[ProjectedSection]
