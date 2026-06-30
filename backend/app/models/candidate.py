from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from .field import FieldValue
from .education import EducationItem
from .source import SourceInfo


class Candidate(BaseModel):
    """
    Canonical unified candidate representation.

    This is:
    - multi-source merged
    - confidence-aware
    - fully traceable
    """

    # 👤 Identity
    full_name: FieldValue[str]
    first_name: Optional[FieldValue[str]] = None
    last_name: Optional[FieldValue[str]] = None

    # 📞 Contact
    emails: List[FieldValue[str]] = Field(default_factory=list)
    phones: List[FieldValue[str]] = Field(default_factory=list)

    # 🏢 Professional
    current_company: Optional[FieldValue[str]] = None
    title: Optional[FieldValue[str]] = None

    # 🧠 Skills
    skills: List[FieldValue[str]] = Field(default_factory=list)

    # 🎓 Education
    education: List[EducationItem] = Field(default_factory=list)

    # 📦 Metadata layer
    sources: List[SourceInfo] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "extra": "forbid"
    }