import re
from typing import Dict, Optional

# Basic mapping for known countries. Real implementation might use pycountry.
COUNTRY_MAPPING = {
    "usa": "US",
    "united states": "US",
    "india": "IN",
    "uk": "GB",
    "united kingdom": "GB",
    "canada": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
}

def parse_location(loc_str: Optional[str]) -> Optional[Dict[str, Optional[str]]]:
    """
    Parses a raw location string like 'Hyderabad, India' into { city, region, country }.
    """
    if not loc_str:
        return None

    clean_loc = loc_str.strip()
    # Remove emojis or common bullet points
    clean_loc = re.sub(r'^[📍\s•]+', '', clean_loc)

    parts = [p.strip() for p in clean_loc.split(',')]
    
    city = None
    region = None
    country = None

    if len(parts) == 1:
        # Check if it's just a country or city
        val = parts[0]
        if val.lower() in COUNTRY_MAPPING or len(val) == 2:
            country = COUNTRY_MAPPING.get(val.lower(), val.upper())
        else:
            city = val
    elif len(parts) == 2:
        # e.g., "Hyderabad, India" or "San Francisco, CA"
        city = parts[0]
        val2 = parts[1]
        if val2.lower() in COUNTRY_MAPPING:
            country = COUNTRY_MAPPING[val2.lower()]
        elif len(val2) == 2 and val2.upper() == val2:
            # Assume 2-letter code is country or US state
            if val2 in ["CA", "NY", "TX", "WA", "FL", "IL"]: # basic heuristic
                region = val2
                country = "US"
            else:
                country = val2
        else:
            region = val2
    elif len(parts) >= 3:
        # e.g., "San Francisco, CA, USA"
        city = parts[0]
        region = parts[1]
        val3 = parts[-1]
        country = COUNTRY_MAPPING.get(val3.lower(), val3)

    return {
        "city": city,
        "region": region,
        "country": country
    }
