from typing import Optional
from pydantic import BaseModel, Field
from .field import FieldValue


class EducationItem(BaseModel):
    """
    Represents a single education entry in candidate profile.
    Fully traceable and source-aware.
    """

    degree: FieldValue[str]
    institution: FieldValue[str]

    start_year: Optional[FieldValue[int]] = None
    end_year: Optional[FieldValue[int]] = None

    model_config = {
        "extra": "forbid"
    }