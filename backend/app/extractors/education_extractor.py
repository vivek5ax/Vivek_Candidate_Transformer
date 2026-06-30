import re
from typing import Any, Dict, List, Optional
from app.utils.date_utils import parse_to_yyyy_mm
from app.utils.ai_validator import ai_validator


def extract_education(text: str) -> List[Dict[str, Any]]:
    """
    Parses canonical EDUCATION block text into structured academic degree entries
    using ai_validator to intelligently map fields.
    """
    if not text:
        return []

    entries: List[Dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    lines = [re.sub(r'^\[BOLD:[\d.]+\]\s*', '', l) for l in lines]

    date_regex = re.compile(r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|\d{4})\s*(?:[\-\u2013\u2014]+|to)\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}|\d{4}|Present|Current)', re.IGNORECASE)
    cgpa_regex = re.compile(r'(?:CGPA|GPA|Grade|Percentage|Score)[:\s]+([\d.]+(?:\s*/\s*[\d.]+|%)?)', re.IGNORECASE)

    current_entry: Optional[Dict[str, Any]] = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if line is CGPA
        cgpa_match = cgpa_regex.search(line)
        if cgpa_match:
            if current_entry:
                current_entry["cgpa"] = cgpa_match.group(1).strip()
            i += 1
            continue

        # Look ahead for up to 3 lines to form an entry chunk
        chunk = lines[i:i+3]
        if not chunk:
            break

        # A new entry usually starts with a school name or degree.
        # We will parse 1, 2, or 3 lines as a single block based on metadata
        # Find which line is the date
        date_line_idx = -1
        date_match = None
        for idx, cl in enumerate(chunk):
            dm = date_regex.search(cl)
            if dm or ai_validator.is_valid_date(cl):
                date_line_idx = idx
                date_match = dm
                break
                
        if date_line_idx != -1:
            # We found a date in the next 3 lines!
            # The remaining lines in the chunk before/around the date are org/degree
            end_date = date_match.group(2).strip() if date_match else chunk[date_line_idx]
            
            non_date_lines = [cl for idx, cl in enumerate(chunk) if idx != date_line_idx and not cgpa_regex.search(cl)]
            
            inst = None
            deg = None
            
            if len(non_date_lines) == 1:
                # Combined line or just one line available
                parts = re.split(r',|\s+at\s+|\s+-\s+|\s+–\s+', non_date_lines[0], maxsplit=1)
                if len(parts) == 2:
                    deg, inst = parts[0].strip(), parts[1].strip()
                else:
                    deg = non_date_lines[0]
            elif len(non_date_lines) >= 2:
                # Use AI validator to see which is ORG
                l1, l2 = non_date_lines[0], non_date_lines[1]
                if ai_validator.is_valid_organization(l1):
                    inst = l1
                    deg = l2
                elif ai_validator.is_valid_organization(l2):
                    inst = l2
                    deg = l1
                else:
                    # Fallback heuristics
                    if any(k in l1.lower() for k in ("university", "college", "institute", "school")):
                        inst = l1
                        deg = l2
                    else:
                        deg = l1
                        inst = l2
                        
            if current_entry:
                entries.append(current_entry)
                
            current_entry = {
                "degree": deg,
                "institution": inst,
                "end_date": end_date,
                "cgpa": None
            }
            # Advance i past the chunk we just consumed
            # If we used 3 lines, advance by 3, etc.
            # We consumed up to the max index we used.
            consumed_lines = len(non_date_lines) + 1 # +1 for date
            i += consumed_lines
            continue
            
        else:
            # No date found in the chunk. It might just be a single line entry.
            if current_entry:
                entries.append(current_entry)
            
            parts = re.split(r',|\s+at\s+|\s+-\s+|\s+–\s+', line, maxsplit=1)
            deg = parts[0].strip()
            inst = parts[1].strip() if len(parts) == 2 else None
            current_entry = {
                "degree": deg,
                "institution": inst,
                "end_date": None,
                "cgpa": None
            }
            i += 1

    if current_entry:
        entries.append(current_entry)

    formatted_entries = []
    for entry in entries:
        deg = entry.get("degree") or ""
        field = None
        
        # Split degree and field
        deg_split = re.split(r'\s+in\s+|\s+-\s+|\s+–\s+', deg, maxsplit=1, flags=re.IGNORECASE)
        if len(deg_split) == 2:
            deg = deg_split[0].strip()
            field = deg_split[1].strip()

        # Parse end_year from end_date
        end_date_raw = entry.get("end_date")
        end_year = None
        if end_date_raw:
            ym = parse_to_yyyy_mm(end_date_raw)
            if ym:
                end_year = ym[:4] # Extract YYYY

        formatted_entries.append({
            "institution": entry.get("institution"),
            "degree": deg,
            "field": field,
            "end_year": end_year
        })

    return formatted_entries
