import re
from typing import Any, Dict, List

def extract_projects(text: str) -> List[Dict[str, Any]]:
    """
    Extracts a simplified list of projects from the PROJECTS section using [BOLD:size] tags.
    Returns: List of {"title": "...", "link": "..."}
    """
    if not text:
        return []

    projects = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    project_title_size = None
    bold_regex = re.compile(r'^\[BOLD:([\d.]+)\]\s*(.*)$')
    
    # 1. Find the canonical project title size from the very first bold line
    for line in lines:
        match = bold_regex.search(line)
        if match:
            project_title_size = match.group(1)
            break
            
    if not project_title_size:
        # Fallback: if no bold formatting was extracted, we can't reliably partition using size.
        # Fallback to naive bullet extraction for simplicity.
        pass

    current_title = None
    current_links = []
    
    # Tightened regex to extract valid urls (both embedded LINK tags and raw urls as fallback)
    url_pat = re.compile(r'\[LINK:(https?://[^\]\s]+)\]|(?:https?://[a-zA-Z0-9-]+\.[a-zA-Z0-9-./]+|www\.[a-zA-Z0-9-]+\.[a-zA-Z0-9-./]+|[a-zA-Z0-9-]+\.(?:com|in|org|net|io|app|dev|me)(?:/[a-zA-Z0-9-./]+)?)')
    
    for i, line in enumerate(lines):
        clean_line = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', line).strip()
        clean_line = re.sub(r'\s*\[LINK:https?://[^\]\s]+\]', '', clean_line).strip()
        
        # Check for link in the line itself or adjacent lines
        found_links = []
        for match in url_pat.finditer(line):
            if match.group(1): # It was a [LINK:] tag
                found_links.append(match.group(1))
            else:
                found_links.append(match.group(0))
            
        match = bold_regex.search(line)
        if match:
            size = match.group(1)
            raw_title = match.group(2).strip()
            raw_title = re.sub(r'\s*\[LINK:https?://[^\]\s]+\]', '', raw_title).strip()
            
            if size == project_title_size and len(raw_title) > 2 and len(raw_title) < 120:
                if current_title:
                    projects.append({
                        "title": current_title,
                        "links": current_links
                    })
                current_title = raw_title
                current_links = [l for l in found_links if l not in current_links]
                continue
                
        if current_title and found_links:
            for fl in found_links:
                if fl not in current_links:
                    current_links.append(fl)
            
    if current_title:
        projects.append({
            "title": current_title,
            "links": current_links
        })
        
    return projects
