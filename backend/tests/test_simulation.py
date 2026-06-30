from datetime import datetime, timezone

from app.models.field import FieldValue
from app.models.source import SourceInfo
from app.models.candidate import Candidate
from app.models.merge_policy import resolve_conflict
from app.models.utils import normalize_fieldvalues, deduplicate_fieldvalues


def run_simulation():
    # =========================================================
    # 🧠 MOCK SOURCES
    # =========================================================
    resume_source = SourceInfo(
        source_id="resume_001",
        source_type="resume",
        ingestion_time=datetime.now(timezone.utc)
    )

    linkedin_source = SourceInfo(
        source_id="linkedin_001",
        source_type="linkedin",
        ingestion_time=datetime.now(timezone.utc)
    )

    # =========================================================
    # 👤 CONFLICTING IDENTITY FIELDS
    # =========================================================
    name_from_resume = FieldValue[str](
        value="Vivek M",
        source="resume",
        confidence=0.92
    )

    name_from_linkedin = FieldValue[str](
        value="Vivek Mohan",
        source="linkedin",
        confidence=0.89
    )

    title_resume = FieldValue[str](
        value="Software Engineer",
        source="resume",
        confidence=0.90
    )

    title_linkedin = FieldValue[str](
        value="Backend Developer",
        source="linkedin",
        confidence=0.88
    )

    # =========================================================
    # 🧠 SKILLS (WITH DUPLICATES ACROSS SOURCES)
    # =========================================================
    skills = [
        FieldValue[str](value="Python", source="resume", confidence=0.95),
        FieldValue[str](value="FastAPI", source="resume", confidence=0.90),
        FieldValue[str](value="Python", source="linkedin", confidence=0.85),
        FieldValue[str](value="Docker", source="linkedin", confidence=0.80),
    ]

    # =========================================================
    # 📞 EMAILS (DUPLICATE + MULTI SOURCE)
    # =========================================================
    emails = [
        FieldValue[str](value="vivek@gmail.com", source="resume", confidence=0.95),
        FieldValue[str](value="vivek.mohan@linkedin.com", source="linkedin", confidence=0.90),
    ]

    # =========================================================
    # ⚙️ NORMALIZATION + DEDUP
    # =========================================================
    clean_skills = normalize_fieldvalues(skills)
    clean_emails = deduplicate_fieldvalues(emails)

    # =========================================================
    # 🧠 CONFLICT RESOLUTION (CORE MERGE LOGIC)
    # =========================================================
    final_name = resolve_conflict([name_from_resume, name_from_linkedin])
    final_title = resolve_conflict([title_resume, title_linkedin])
    assert final_name is not None

    # =========================================================
    # 🏗️ FINAL CANONICAL CANDIDATE OBJECT
    # =========================================================
    candidate = Candidate(
        full_name=final_name,
        title=final_title,
        emails=clean_emails,
        skills=clean_skills,
        education=[],
        sources=[resume_source, linkedin_source],
        last_updated=datetime.now(timezone.utc)
    )

    assert candidate.full_name.value == "Vivek M"
    assert candidate.title is not None
    assert candidate.title.value == "Software Engineer"
    assert len(candidate.skills) == 3
    assert len(candidate.emails) == 2
    return candidate


def test_simulation_workflow():
    run_simulation()


# =========================================================
# 🧾 OUTPUT SIMULATION
# =========================================================
if __name__ == "__main__":
    candidate = run_simulation()
    print("\n===== FINAL CANONICAL CANDIDATE =====\n")
    print("NAME:", candidate.full_name.value)
    print("TITLE:", candidate.title.value if candidate.title else "N/A")

    print("\nEMAILS:")
    for e in candidate.emails:
        print(f"- {e.value} | {e.source} | {e.confidence}")

    print("\nSKILLS:")
    for s in candidate.skills:
        print(f"- {s.value} | {s.source} | {s.confidence}")

    print("\nSOURCES:")
    for s in candidate.sources:
        print(f"- {s.source_id} | {s.source_type}")

    print("\nLAST UPDATED:", candidate.last_updated)