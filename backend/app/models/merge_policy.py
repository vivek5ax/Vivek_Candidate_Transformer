from typing import List, Optional, TypeVar

from .field import FieldValue

T = TypeVar("T")


# =========================================================
# 🧠 SOURCE TRUST MODEL
# =========================================================

SOURCE_TRUST_SCORE = {
    "resume": 0.95,
    "linkedin": 0.90,
    "github": 0.85,
    "csv": 0.70,
    "manual": 0.60,
    "api": 0.75
}


# =========================================================
# ⚙️ MERGE SCORING FUNCTION
# =========================================================

def compute_merge_score(confidence: float, source: str) -> float:
    """
    Final deterministic score used for conflict resolution.

    Formula:
        score = confidence × source_trust
    """

    trust = SOURCE_TRUST_SCORE.get(source, 0.5)
    return confidence * trust


# =========================================================
# 🧠 CONFLICT RESOLUTION ENGINE
# =========================================================

def resolve_conflict(values: List[FieldValue[T]]) -> Optional[FieldValue[T]]:
    """
    Deterministic winner selection rule.

    Steps:
    1. Compute merge score = confidence × source_trust
    2. Pick highest score
    3. Tie-breaker → higher confidence
    """

    if not values:
        return None

    def score(v: FieldValue[T]) -> float:
        return compute_merge_score(v.confidence, v.source)

    return max(
        values,
        key=lambda v: (score(v), v.confidence)
    )


# =========================================================
# 📜 FIELD MERGE STRATEGY CONTRACT (DESIGN RULES)
# =========================================================
"""
FIELD MERGE STRATEGY

1. SCALAR FIELDS (title, company, full_name parts)
   → resolve_conflict()

2. LIST FIELDS (skills, emails, phones)
   → union + deduplicate (handled in utils layer)

3. STRUCTURED FIELDS (education)
   → group by semantic key + resolve_conflict per group

4. IDENTITY FIELDS (name)
   → highest merge score wins

--------------------------------------------------------

DETERMINISM RULE:
- score = confidence × source_trust
- tie-breaker = confidence
- NO randomness allowed
"""


# =========================================================
# 📊 DECISION MATRIX (SYSTEM BEHAVIOR CONTRACT)
# =========================================================
"""
SCALAR       → resolve_conflict
LIST         → union + deduplicate
STRUCTURED   → grouped merge strategy
IDENTITY     → highest score selection
"""


# =========================================================
# ⚠️ SYSTEM GUARANTEE RULES
# =========================================================
"""
MERGE SYSTEM GUARANTEE:

- Deterministic output for same input
- No randomness in selection
- No LLM dependency in merge core
- Fully explainable decisions
- Source + confidence always preserved
"""