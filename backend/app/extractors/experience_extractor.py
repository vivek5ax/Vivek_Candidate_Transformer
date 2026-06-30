import re
from typing import Any, Dict, List, Optional, Tuple
from app.utils.date_utils import parse_to_yyyy_mm
from app.utils.ai_validator import ai_validator


def extract_experience(text: str) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Parses canonical EXPERIENCE block text into structured job entries.
    Uses Date anchoring and spaCy ORG validation for perfect extraction.
    Returns: (experience_list, most_recent_title, most_recent_company)
    """
    if not text:
        return [], None, None

    entries: List[Dict[str, Any]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    date_regex = re.compile(r'((?:[A-Z][a-z]{2,8}\s+)?\d{4})\s*(?:[\-\u2013\u2014]+|to)\s*(Present|Current|(?:[A-Z][a-z]{2,8}\s+)?\d{4})', re.IGNORECASE)
    single_date_regex = re.compile(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{4}\b', re.IGNORECASE)
    bold_regex = re.compile(r'^\[BOLD:[\d.]+\]\s*(.*)$')

    most_recent_title = None
    most_recent_company = None
    
    # 1. Identify all Date anchors
    date_anchors = []
    for i, raw_line in enumerate(lines):
        line = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', raw_line).strip()
        dm = date_regex.search(line)
        sm = single_date_regex.search(line)
        if dm or (sm and len(line) < 130):
            date_anchors.append({
                "index": i,
                "start": dm.group(1).strip() if (dm and dm.group(1)) else None,
                "end": dm.group(2).strip().title() if (dm and dm.group(2)) else (sm.group(0).strip().title() if sm else "")
            })
            
    # If no dates found, very rare, return empty for now
    if not date_anchors:
        return [], None, None
        
    # 2. Extract entries around Date anchors
    for a_idx, anchor in enumerate(date_anchors):
        idx = anchor["index"]
        
        # Look backwards up to 5 lines to find bold headers (including the date line itself)
        bold_lines = []
        for j in range(idx, max(-1, idx - 5), -1):
            # stop if we hit the previous anchor's boundaries
            if a_idx > 0 and j <= date_anchors[a_idx-1]["index"]:
                break
            
            match = bold_regex.search(lines[j])
            if match:
                bl = match.group(1).strip()
                if j == idx:
                    dm_match = date_regex.search(bl)
                    sm_match = single_date_regex.search(bl)
                    if dm_match:
                        bl = bl.replace(dm_match.group(0), "").strip()
                    elif sm_match:
                        bl = bl.replace(sm_match.group(0), "").strip()
                    bl = re.sub(r'[\-\u2013\u2014|]+\s*$', '', bl).strip()
                if len(bl) > 2:
                    print(f"DEBUG BOLD LINE: {bl!r}")
                    bold_lines.insert(0, bl)
                
        # If no bold lines, look for normal short lines
        if not bold_lines:
            for j in range(idx, max(-1, idx - 3), -1):
                if a_idx > 0 and j <= date_anchors[a_idx-1]["index"]:
                    break
                clean = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', lines[j]).strip()
                if j == idx:
                    dm_match = date_regex.search(clean)
                    sm_match = single_date_regex.search(clean)
                    if dm_match:
                        clean = clean.replace(dm_match.group(0), "").strip()
                    elif sm_match:
                        clean = clean.replace(sm_match.group(0), "").strip()
                    clean = re.sub(r'[\-\u2013\u2014|]+\s*$', '', clean).strip()
                    
                if len(clean) > 2 and len(clean) < 80 and not any(clean.startswith(b) for b in ("-", "*", "•")):
                    bold_lines.insert(0, clean)
                    
        # Collect links embedded in bold lines
        entry_links = []
        clean_bold_lines = []
        for line in bold_lines:
            found_links = re.findall(r'\[LINK:(https?://[^\]\s]+)\]', line)
            entry_links.extend([l for l in found_links if l not in entry_links])
            clean_bold_lines.append(re.sub(r'\s*\[LINK:https?://[^\]\s]+\]', '', line).strip())
            
        # Use spaCy to classify Company vs Title
        company, title = ai_validator.extract_org_and_title(clean_bold_lines)
        
        def split_title_company(text: str):
            parts = re.split(r'\s+[\-\u2013\u2014|]\s+|\s{3,}', text, maxsplit=1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
            return None, None

        # Deterministic Split Fallback (if they are on the same line)
        if company and not title:
            t, c = split_title_company(company)
            if t and c: title, company = t, c
        elif title and not company:
            t, c = split_title_company(title)
            if t and c: title, company = t, c
            
        # If both not found natively via spaCy, fallback to naive layout assumption
        if not title and not company and clean_bold_lines:
            t, c = split_title_company(clean_bold_lines[0])
            if t and c:
                title, company = t, c
            else:
                title = clean_bold_lines[0]
                if len(clean_bold_lines) > 1:
                    company = clean_bold_lines[1]
                
        if not most_recent_title:
            most_recent_title = title
            most_recent_company = company
            
        # Collect responsibilities: from Date until the next anchor's lookback boundary
        resp_start = idx + 1
        resp_end = len(lines)
        if a_idx + 1 < len(date_anchors):
            # Next anchor lookback boundary
            next_idx = date_anchors[a_idx+1]["index"]
            
            # Count how many bold lines precede the next anchor to define the boundary
            next_bold_count = 0
            for j in range(next_idx - 1, max(idx, next_idx - 5), -1):
                if bold_regex.search(lines[j]):
                    next_bold_count += 1
                else:
                    break
            resp_end = next_idx - (next_bold_count if next_bold_count > 0 else 1)
            
        responsibilities = []
        for j in range(resp_start, resp_end):
            # Also extract links from responsibilities
            found_links = re.findall(r'\[LINK:(https?://[^\]\s]+)\]', lines[j])
            entry_links.extend([l for l in found_links if l not in entry_links])
            
            clean_l = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', lines[j]).strip()
            clean_l = re.sub(r'\s*\[LINK:https?://[^\]\s]+\]', '', clean_l).strip()
            # clean bullet points
            clean_l = re.sub(r'^[-*•\d.\s]+', '', clean_l).strip()
            if clean_l and len(clean_l) > 10:
                responsibilities.append(clean_l)
                
        # Consolidate responsibilities (merge broken lines if necessary)
        merged_resp = []
        for r in responsibilities:
            if merged_resp and len(r) > 10 and r[0].islower():
                merged_resp[-1] = merged_resp[-1] + " " + r
            else:
                merged_resp.append(r)
                
        entries.append({
            "title": title,
            "company": company,
            "start_date": anchor["start"],
            "end_date": anchor["end"],
            "responsibilities": merged_resp,
            "links": entry_links
        })

    # Format fields to match target schema
    for entry in entries:
        entry["start"] = parse_to_yyyy_mm(entry.pop("start_date", None))
        entry["end"] = parse_to_yyyy_mm(entry.pop("end_date", None))
        resp_list = entry.pop("responsibilities", [])
        entry["summary"] = "\n".join(resp_list) if resp_list else None

    return entries, most_recent_title, most_recent_company
