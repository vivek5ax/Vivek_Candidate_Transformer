def validate_confidence(value: float) -> bool:
    return 0.0 <= value <= 1.0

def validate_email(email: str) -> bool:
    return "@" in email and "." in email

from typing import Any
from .candidate import Candidate


def validate_candidate_sanity(candidate: Candidate) -> bool:
    """
    Ensures candidate is structurally valid.

    Rules:
    - must have full_name OR at least one email OR phone
    - confidence must be valid (Pydantic already enforces per-field)
    """

    has_identity = (
        candidate.full_name is not None
        or len(candidate.emails) > 0
        or len(candidate.phones) > 0
    )

    return has_identity

