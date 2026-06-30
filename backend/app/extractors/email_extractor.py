import re
from typing import List


EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
)


def extract_emails(text: str) -> List[str]:
    """
    Extract raw email strings from unstructured or structured text using regex.
    Performs basic deduplication while preserving order.
    Note: Full validation and email normalization happen in Branch 4.
    """
    if not text:
        return []

    matches = EMAIL_REGEX.findall(text)
    seen = set()
    emails = []
    for m in matches:
        m_clean = m.strip().lower()
        if m_clean not in seen:
            seen.add(m_clean)
            emails.append(m.strip())
    return emails
