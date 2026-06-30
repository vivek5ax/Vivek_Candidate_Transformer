import re
from typing import Dict, List, Set

# Comprehensive section header taxonomy mapping canonical section names to vast surface form variations
SECTION_HEADER_TAXONOMY: Dict[str, Set[str]] = {
    "SUMMARY": {
        "summary", "professional summary", "executive summary", "career summary",
        "objective", "career objective", "professional objective", "about me",
        "profile", "professional profile", "personal profile", "overview"
    },
    "TECHNICAL_SKILLS": {
        "skills", "technical skills", "skills & technologies",
        "core competencies", "competencies", "it skills", "software skills",
        "programming skills", "technical proficiency", "tools & technologies",
        "key skills", "technical expertise", "skills matrix"
    },
    "EXPERIENCE": {
        "experience", "professional experience", "work experience", "employment history",
        "work history", "career history", "professional background", "industry experience",
        "internships", "internship experience", "externships", "co-op experience",
        "work background", "relevant experience", "employment"
    },
    "PROJECTS": {
        "projects", "key projects", "academic projects", "personal projects",
        "technical projects", "software projects", "capstone projects", "major projects"
    },
    "EDUCATION": {
        "education", "academic background", "educational qualifications",
        "academic qualifications", "academics", "university education", "scholastic record"
    },
    "CERTIFICATIONS": {
        "certifications", "licenses & certifications", "professional certifications",
        "courses & certifications", "training & certifications", "certified courses"
    },
    "ACHIEVEMENTS": {
        "achievements", "awards", "honors & awards", "awards & achievements",
        "accolades", "accomplishments", "key accomplishments", "scholarships & awards"
    },
    "OPEN_SOURCE": {
        "open source contributions", "open source", "hackathons", "hackathon experience",
        "coding profiles", "competitive programming", "profiles", "online profiles"
    },
    "PUBLICATIONS": {
        "publications", "research papers", "patents", "presentations"
    },
    "LANGUAGES": {
        "languages", "known languages", "spoken languages", "linguistic skills"
    },
    "INTERESTS": {
        "interests", "hobbies", "extra-curricular activities", "extracurriculars", "activities"
    }
}

# Inverted lookup: lowercased header string -> canonical section key
HEADER_TO_CANONICAL: Dict[str, str] = {}
for canonical_key, variations in SECTION_HEADER_TAXONOMY.items():
    for var in variations:
        HEADER_TO_CANONICAL[var.lower().strip()] = canonical_key


def segment_resume_sections(text: str) -> Dict[str, str]:
    """
    Slices raw resume document prose into canonical section blocks based on strict header recognition.
    Returns a dictionary mapping section keys (e.g. 'HEADER', 'SUMMARY', 'TECHNICAL_SKILLS', 'EXPERIENCE')
    to their raw text content.
    """
    if not text:
        return {"HEADER": ""}

    sections: Dict[str, List[str]] = {"HEADER": []}
    current_section = "HEADER"

    lines = text.splitlines()
    for line in lines:
        raw_line = line.strip()
        if not raw_line:
            sections.setdefault(current_section, []).append("")
            continue

        # Skip decorative divider lines (e.g. ======= or -------)
        if re.fullmatch(r'^[=\-_*#~]{3,}$', raw_line):
            continue

        # Strip the new [BOLD:size] formatting
        raw_line_no_bold = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', raw_line)
        
        # Clean potential header candidate
        # Remove decorative borders, markdown hashes, or colons at end
        clean_cand = re.sub(r'^[=\-_*#~\s]+|[=\-_*#~:\s]+$', '', raw_line_no_bold).lower().strip()

        # Check heuristics: header lines should be relatively short (< 45 chars)
        # and should not start with bullet points, contain key-value colons followed by content, or comma-separated lists
        has_inline_kv = ":" in raw_line_no_bold and not raw_line_no_bold.strip().endswith(":")
        has_commas = "," in raw_line_no_bold and len(raw_line_no_bold.split(",")) >= 2
        is_bullet_or_kv = any(raw_line_no_bold.startswith(b) for b in ("-", "*", "•", "1.", "2.")) or has_inline_kv or has_commas

        detected_section = None
        if len(clean_cand) < 45 and not is_bullet_or_kv:
            # Exact match check
            if clean_cand in HEADER_TO_CANONICAL:
                cand_sec = HEADER_TO_CANONICAL[clean_cand]
                if not (current_section == "TECHNICAL_SKILLS" and cand_sec == "LANGUAGES"):
                    detected_section = cand_sec
            else:
                # Token or phrase check for composite headers like "PROJECTS & HACKATHONS" or "PROFESSIONAL WORK EXPERIENCE"
                tokens = set(re.split(r'[\s&/|,+\-]+', clean_cand))
                for core_word, canonical_key in [
                    ("skills", "TECHNICAL_SKILLS"),
                    ("experience", "EXPERIENCE"), ("internships", "EXPERIENCE"),
                    ("projects", "PROJECTS"), ("hackathons", "OPEN_SOURCE"), ("hackathon", "OPEN_SOURCE"),
                    ("education", "EDUCATION"), ("certifications", "CERTIFICATIONS"),
                    ("achievements", "ACHIEVEMENTS"), ("awards", "ACHIEVEMENTS")
                ]:
                    if core_word in tokens and len(tokens) <= 5:
                        if not (current_section == "TECHNICAL_SKILLS" and canonical_key == "LANGUAGES"):
                            detected_section = canonical_key
                            break

        if detected_section:
            current_section = detected_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(line)

    # Join lines back into block text
    return {sec: "\n".join(lines).strip() for sec, lines in sections.items() if any(l.strip() for l in lines)}
