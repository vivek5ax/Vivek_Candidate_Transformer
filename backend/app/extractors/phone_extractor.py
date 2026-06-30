import re
import phonenumbers
from typing import List


PHONE_REGEX = re.compile(
    r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
)


def extract_phones(text: str) -> List[str]:
    """
    Extract phone numbers from text and strictly format to E.164.
    """
    if not text:
        return []

    matches = PHONE_REGEX.findall(text)
    seen = set()
    phones = []
    
    for m in matches:
        cleaned = m.strip()
        digits_only = re.sub(r'\D', '', cleaned)
        
        if 7 <= len(digits_only) <= 15:
            # Try to parse with phonenumbers
            try:
                # Default to US/IN if no country code provided, just for heuristics
                # But phonenumbers needs a region if there's no + sign.
                # We can try parsing with 'US' first.
                pn = phonenumbers.parse(cleaned, "US")
                if phonenumbers.is_possible_number(pn):
                    e164_str = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
                    if e164_str not in seen:
                        seen.add(e164_str)
                        phones.append(e164_str)
            except phonenumbers.NumberParseException:
                pass

    return phones
