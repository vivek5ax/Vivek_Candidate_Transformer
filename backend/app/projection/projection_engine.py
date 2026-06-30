import jmespath  # type: ignore
from typing import Any, Dict, List
from app.models.projection_config import ProjectionConfig, ProjectedSection, ProjectedField

def apply_projection(data: Dict[str, Any], config: ProjectionConfig) -> Dict[str, Any]:
    """
    Applies the UI-driven ProjectionConfig to the canonical ExtractedCandidate dict.
    Returns a newly shaped dictionary mapped to the config's sections and display_names.
    """
    result: Dict[str, Any] = {"sections": []}
    
    for section in config.sections:
        sec_out: Dict[str, Any] = {
            "section_name": section.section_name,
            "data": None
        }
        
        if section.from_array:
            # Map an array of objects
            array_data = jmespath.search(section.from_array, data)
            if not array_data or not isinstance(array_data, list):
                sec_out["data"] = []
            else:
                mapped_array = []
                for item in array_data:
                    if section.section_name == "Certifications" and isinstance(item, str):
                        if "(Certificate)" in item or "[LINK:" in item:
                            continue
                    mapped_item = _map_fields(item, section.fields, config.provenance_filters)
                    mapped_array.append(mapped_item)
                sec_out["data"] = mapped_array
        else:
            # Map a flat object
            sec_out["data"] = _map_fields(data, section.fields, config.provenance_filters)
            
        result["sections"].append(sec_out)
        
    return result

def _map_fields(source_data: Any, fields: List[ProjectedField], prov_filters: List[str]) -> Dict[str, Any]:
    mapped: Dict[str, Any] = {}
    for field in fields:
        val = jmespath.search(field.from_path, source_data)
        
        # In our architecture, val is usually {"value": X, "provenance": [ ... ]}
        # But if jmespath searches a nested path (e.g. `emails.value[0]`), it returns just the raw primitive!
        # If it returns the full object with provenance, we filter it.
        if isinstance(val, dict) and "value" in val and "provenance" in val:
            # Filter provenance based on config
            filtered_prov = []
            for p in val.get("provenance", []):
                new_p = {}
                for k, v in p.items():
                    if k in prov_filters:
                        new_p[k] = v
                
                # Add simulated confidence if requested but not natively present
                if "confidence" in prov_filters and "confidence" not in new_p:
                    source_str = str(p.get("source", ""))
                    new_p["confidence"] = 1.0 if source_str.lower().endswith(".csv") else 0.85
                    
                if new_p:
                    filtered_prov.append(new_p)
            
            val_to_use = val["value"]
            
            # Normalize if requested
            if field.normalize:
                val_to_use = _normalize(val_to_use, field.normalize)
                
            # Classify skills if requested (basic mapping to canonical names)
            if field.classify_skills and isinstance(val_to_use, list):
                classified = {"Known Skills": [], "Other": []}
                from app.skill_taxonomy.tech_skills import TECH_SKILL_TAXONOMY
                # Create a reverse lookup dict
                reverse_lookup = {}
                for canonical, aliases in TECH_SKILL_TAXONOMY.items():
                    for alias in aliases:
                        reverse_lookup[alias.lower()] = canonical
                        
                for skill in val_to_use:
                    skill_str = str(skill).lower().strip()
                    if skill_str in reverse_lookup:
                        canonical = reverse_lookup[skill_str]
                        if canonical not in classified["Known Skills"]:
                            classified["Known Skills"].append(canonical)
                    else:
                        classified["Other"].append(skill)
                val_to_use = classified
                
            # Handle recursive sub_fields
            if field.sub_fields:
                val_to_use = {} # Clear parent value so it acts only as a container for selected sub_fields
                
            mapped[field.display_name] = {
                "value": val_to_use,
                "provenance": filtered_prov
            }
            
            # Sub-fields logic: If sub_fields exist, we process them relative to the current source_data 
            # and attach them to the mapped result.
            if field.sub_fields:
                sub_mapped = _map_fields(source_data, field.sub_fields, prov_filters)
                # Merge sub_mapped into the current object's representation
                for k, v in sub_mapped.items():
                    mapped[field.display_name][k] = v
        else:
            # It's a raw primitive because the jmespath bypassed the wrapper
            val_to_use = val
            if field.normalize:
                val_to_use = _normalize(val_to_use, field.normalize)
                
            mapped[field.display_name] = {
                "value": val_to_use,
                "provenance": []
            }
            if field.sub_fields:
                sub_mapped = _map_fields(source_data, field.sub_fields, prov_filters)
                for k, v in sub_mapped.items():
                    mapped[field.display_name][k] = v
            
    return mapped


def _normalize(value: Any, rule: str) -> Any:
    # Example placeholder for normalizations
    if not value: return value
    rule = rule.lower()
    
    if rule == "title_case" and isinstance(value, str):
        return value.title()
    if rule == "uppercase" and isinstance(value, str):
        return value.upper()
    
    return value
