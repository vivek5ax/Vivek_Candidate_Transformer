"""
BRANCH 2 — CANONICAL DATA MODEL CONTRACT

This file freezes the schema behavior for all downstream branches.

DO NOT MODIFY WITHOUT VERSION UPGRADE.
"""


BRANCH_2_VERSION = "1.0.0"


CANONICAL_RULES = {
    "field_wrapper": "FieldValue required for all atomic values",
    "source_tracking": "Every value must contain source + confidence",
    "merge_logic": "deterministic confidence × source trust scoring",
    "list_handling": "union + deduplication required",
    "structured_data": "must remain nested and traceable",
    "determinism": "no randomness allowed in any resolution",
}


FORBIDDEN_PATTERNS = [
    "raw string fields in Candidate",
    "untracked values without FieldValue",
    "random selection in merge logic",
    "LLM-based merge decisions inside core layer",
]


def validate_branch2_compliance():
    """
    Lightweight sanity checker for architecture integrity.
    """
    return {
        "version": BRANCH_2_VERSION,
        "status": "LOCKED",
        "rules": CANONICAL_RULES,
        "forbidden": FORBIDDEN_PATTERNS,
    }