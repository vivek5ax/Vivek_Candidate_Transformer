from typing import List, Dict, Any

def categorize_links(raw_links: List[str]) -> Dict[str, Any]:
    """
    Categorizes a list of raw URLs into { linkedin, github, portfolio, other }.
    """
    result: Dict[str, Any] = {
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "other": []
    }
    
    if not raw_links:
        return result

    for link in raw_links:
        clean_link = link.strip()
        lower_link = clean_link.lower()
        
        if "linkedin.com" in lower_link and not result["linkedin"]:
            result["linkedin"] = clean_link
        elif "github.com" in lower_link and not result["github"]:
            result["github"] = clean_link
        elif any(domain in lower_link for domain in ("portfolio", "personal", "me.com", ".dev")) and not result["portfolio"]:
            result["portfolio"] = clean_link
        else:
            other_links = result.get("other")
            if isinstance(other_links, list) and clean_link not in other_links:
                other_links.append(clean_link)
    return result
