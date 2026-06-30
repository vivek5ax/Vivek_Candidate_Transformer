from typing import List, Optional, TypeVar

from .field import FieldValue

T = TypeVar("T")

def get_best_fieldvalue(values: List[FieldValue[T]]) -> Optional[FieldValue[T]]:
    """
    Returns the FieldValue with highest confidence.
    If tie → first encountered is returned.
    """

    if not values:
        return None

    return max(values, key=lambda v: v.confidence)

def merge_fieldvalues(values: List[FieldValue[T]]) -> Optional[FieldValue[T]]:
    """
    Merge multiple FieldValues into a single canonical FieldValue.
    Strategy:
    - choose highest confidence
    - preserve its source and timestamp
    """

    return get_best_fieldvalue(values)

def deduplicate_fieldvalues(values: List[FieldValue[T]]) -> List[FieldValue[T]]:
    """
    Removes duplicates based on `value`.
    Keeps highest confidence instance per unique value.
    """

    seen = {}

    for v in values:
        key = v.value

        if key not in seen:
            seen[key] = v
        else:
            if v.confidence > seen[key].confidence:
                seen[key] = v

    return list(seen.values())

def filter_valid_fieldvalues(values: List[FieldValue[T]]) -> List[FieldValue[T]]:
    """
    Removes invalid FieldValues:
    - None values
    - empty strings
    """

    return [
        v for v in values
        if v.value is not None and str(v.value).strip() != ""
    ]

def normalize_fieldvalues(values: List[FieldValue[T]]) -> List[FieldValue[T]]:
    """
    Full preprocessing pipeline:
    1. filter invalid
    2. deduplicate
    """

    values = filter_valid_fieldvalues(values)
    values = deduplicate_fieldvalues(values)
    return values
