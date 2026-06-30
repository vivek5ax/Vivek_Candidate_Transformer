import re
from typing import List, Tuple
from app.skill_taxonomy import ALIAS_TO_CANONICAL, ALL_SKILL_TERMS
from app.extractors.section_segmenter import segment_resume_sections

# Sort terms by length descending to match multi-word phrases (e.g. "ruby on rails", "spring boot") first
SORTED_SKILL_TERMS = sorted(ALL_SKILL_TERMS, key=len, reverse=True)


def extract_skills(text: str) -> List[str]:
    """
    Extract canonicalized skill names from text or structured delimited strings using comprehensive taxonomy.
    """
    if not text:
        return []

    found_skills = []
    seen_canonical = set()

    text_lower = text.lower()

    # 1. If structured delimited list (<= 300 chars), split on delimiters
    if len(text) <= 300 and any(delim in text for delim in (",", ";", "|")):
        tokens = re.split(r'[,|;]+', text)
        for t in tokens:
            cleaned = t.strip()
            if 1 < len(cleaned) <= 40 and not any(c in cleaned for c in ("@", ":", "http")):
                lower_key = cleaned.lower()
                # Check taxonomy mapping first
                if lower_key in ALIAS_TO_CANONICAL:
                    canonical = ALIAS_TO_CANONICAL[lower_key]
                    if canonical not in seen_canonical:
                        seen_canonical.add(canonical)
                        found_skills.append(canonical)
                else:
                    # If unknown custom phrase, keep formatted
                    if lower_key not in seen_canonical:
                        seen_canonical.add(lower_key)
                        found_skills.append(cleaned.title() if len(cleaned) > 3 else cleaned.upper())

    # 2. Scan full text against taxonomy vocabulary
    for term in SORTED_SKILL_TERMS:
        # Match whole word/token boundaries where applicable
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, text_lower):
            canonical = ALIAS_TO_CANONICAL[term]
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                found_skills.append(canonical)

    return found_skills


def extract_skills_section_aware(text: str) -> Tuple[List[str], List[str]]:
    """
    Slices unstructured resume prose into canonical sections using segment_resume_sections.
    Primary skills come exclusively from TECHNICAL_SKILLS blocks.
    Secondary skills come from EXPERIENCE, PROJECTS, SUMMARY, and other sections.
    """
    if not text:
        return [], []

    sections = segment_resume_sections(text)

    primary_text = sections.get("TECHNICAL_SKILLS", "")
    p_skills = extract_skills(primary_text)

    # Secondary skills come from anywhere outside the dedicated skills section
    secondary_blocks = [
        content for sec, content in sections.items()
        if sec != "TECHNICAL_SKILLS"
    ]
    s_skills_raw = extract_skills("\n".join(secondary_blocks))

    p_set = set(p_skills)
    s_skills = [s for s in s_skills_raw if s not in p_set]

    return p_skills, s_skills

