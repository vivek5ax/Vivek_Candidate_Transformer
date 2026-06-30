from datetime import datetime

from app.models.field import FieldValue
from app.models.merge_policy import resolve_conflict
from app.models.utils import normalize_fieldvalues, deduplicate_fieldvalues


# =========================================================
# 🧨 EDGE CASE 1: EMPTY INPUTS
# =========================================================
def test_empty_inputs():
    empty_conflict = resolve_conflict([])
    assert empty_conflict is None


# =========================================================
# 🧨 EDGE CASE 2: NULL / EMPTY VALUES
# =========================================================
def test_null_empty_values():
    bad_skills = [
        FieldValue[str](value="", source="resume", confidence=0.9),
        FieldValue[str](value=None, source="linkedin", confidence=0.8),  # logically bad input
        FieldValue[str](value="Python", source="resume", confidence=0.95),
    ]

    clean_skills = normalize_fieldvalues(bad_skills)
    assert len(clean_skills) == 1
    assert clean_skills[0].value == "Python"


# =========================================================
# 🧨 EDGE CASE 3: DUPLICATES EXPLOSION
# =========================================================
def test_duplicates_explosion():
    duplicate_skills = [
        FieldValue[str](value="Python", source="resume", confidence=0.9),
        FieldValue[str](value="Python", source="linkedin", confidence=0.85),
        FieldValue[str](value="Python", source="github", confidence=0.8),
    ]

    deduped = deduplicate_fieldvalues(duplicate_skills)
    assert len(deduped) == 1
    assert deduped[0].confidence == 0.9


# =========================================================
# 🧨 EDGE CASE 4: CONFIDENCE BOUNDARY
# =========================================================
def test_confidence_boundary():
    boundary_values = [
        FieldValue[str](value="Java", source="resume", confidence=1.0),
        FieldValue[str](value="Java", source="linkedin", confidence=0.0),
    ]

    winner = resolve_conflict(boundary_values)
    assert winner is not None
    assert winner.confidence == 1.0


# =========================================================
# 🧨 EDGE CASE 5: CONFLICT CHAOS (REAL WORLD SIMULATION)
# =========================================================
def test_conflict_chaos():
    chaos = [
        FieldValue[str](value="Backend Dev", source="linkedin", confidence=0.88),
        FieldValue[str](value="Software Engineer", source="resume", confidence=0.89),
        FieldValue[str](value="Backend Engineer", source="github", confidence=0.87),
    ]

    final = resolve_conflict(chaos)
    assert final is not None
    assert final.value == "Software Engineer"


# =========================================================
# 🧾 OUTPUT CHECK
# =========================================================
if __name__ == "__main__":
    print("\n===== EDGE CASE TESTS =====\n")
    test_empty_inputs()
    test_null_empty_values()
    test_duplicates_explosion()
    test_confidence_boundary()
    test_conflict_chaos()
    print("All edge case tests passed successfully!")