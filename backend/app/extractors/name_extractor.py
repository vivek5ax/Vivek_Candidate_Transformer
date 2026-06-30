import re
from typing import Optional, Tuple


def extract_name(text: str) -> Optional[str]:
    """
    Extract candidate full name from top lines of unformatted prose or resume text.
    Uses deterministic heuristics (e.g., first non-empty line with 2-4 capitalized words).
    """
    if not text:
        return None
    lines = [l.strip() for l in text.split("\n") if l.strip() and not l.strip().startswith("Embedded Link:")]
    # Strip any [BOLD:size] tags before extracting name
    lines = [re.sub(r'^\[BOLD:[\d.]+\]\s*', '', l) for l in lines]
    if not lines:
        return None

    # Check top 15 non-empty lines for a name-like candidate (to handle complex PDF layouts)
    for line in lines[:15]:
        # Strip out email or phone if on the same line
        clean_line = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', line)
        clean_line = re.sub(r'\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', '', clean_line).strip()
        # Remove common icon characters
        clean_line = re.sub(r'[^\w\s\'-]', '', clean_line).strip()

        words = clean_line.split()
        if 2 <= len(words) <= 4:
            # Check if words look like names (letters only, mostly capitalized or clean)
            if all(re.match(r'^[A-Za-z\'-]+$', w) for w in words):
                # Ignore lines that look like common headers
                lower_line = clean_line.lower()
                headers = {"resume", "curriculum", "vitae", "summary", "education", "experience", "profile", "skills", "linkedin", "github", "portfolio"}
                if not any(h in lower_line for h in headers):
                    return clean_line

    # Fallback: Find the first line that looks somewhat like text (not just an icon)
    for line in lines[:10]:
        clean_line = re.sub(r'[^\w\s\'-]', '', line).strip()
        if len(clean_line) > 3 and not any(h in clean_line.lower() for h in ("resume", "linkedin", "github", "gmail")):
            return clean_line

    return lines[0] if len(lines) > 0 else None


def split_full_name(full_name: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Split a full name string into first_name and last_name.
    """
    if not full_name:
        return None, None

    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], None
    elif len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return None, None
