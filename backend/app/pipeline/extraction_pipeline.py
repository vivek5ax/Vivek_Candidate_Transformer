import os
import re
import json
import logging
from typing import List, Optional, Dict, Any

from app.models.extracted_candidate import ExtractedCandidate
from app.parsers.parser_factory import parse_source

logger = logging.getLogger(__name__)


def _normalize_phone(phone: str) -> str:
    return re.sub(r'\D', '', phone)


def _normalize_str(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip().lower()


def match_candidate_record(resume_cand: ExtractedCandidate, csv_candidates: List[ExtractedCandidate]) -> Optional[ExtractedCandidate]:
    """
    Match extracted resume profile against a list of candidates parsed from a recruiter CSV export.
    Matches based on primary keys: Email overlap -> Phone overlap -> Exact Name match.
    """
    if not csv_candidates:
        return None

    if isinstance(resume_cand, list):
        resume_cand = resume_cand[0] if resume_cand else ExtractedCandidate()
    if not resume_cand:
        return None

    resume_emails = {e.lower().strip() for e in resume_cand.emails if e}
    resume_phones = {_normalize_phone(p) for p in resume_cand.phones if p}
    resume_name = _normalize_str(resume_cand.full_name)

    # 1. Email overlap
    if resume_emails:
        for c in csv_candidates:
            c_emails = {e.lower().strip() for e in c.emails if e}
            if resume_emails & c_emails:
                return c

    # 2. Phone overlap (min 7 digits to prevent false positive short matches)
    if resume_phones:
        for c in csv_candidates:
            c_phones = {_normalize_phone(p) for p in c.phones if p}
            for rp in resume_phones:
                if len(rp) >= 7 and any(rp in cp or cp in rp for cp in c_phones if len(cp) >= 7):
                    return c

    # 3. Exact full name match
    if resume_name:
        for c in csv_candidates:
            c_name = _normalize_str(c.full_name)
            if resume_name == c_name and len(resume_name) > 3:
                return c

    # 4. Fuzzy name match
    if resume_name:
        parts = resume_name.split()
        if len(parts) >= 2:
            first_name = parts[0]
            for c in csv_candidates:
                c_name = _normalize_str(c.full_name)
                c_parts = c_name.split()
                if len(c_parts) >= 2:
                    if first_name == c_parts[0] and parts[-1][0] == c_parts[-1][0]:
                        return c

    return None


def combine_extracted_candidates(
    resume_cand: ExtractedCandidate, 
    csv_cand: Optional[ExtractedCandidate],
    resume_filename: str = "resume.pdf",
    csv_filename: str = "candidates.csv"
) -> Dict[str, Any]:
    """
    Merge the file extracted resume object with the matching CSV candidate record.
    Outputs the final JSON structure using the FieldValue schema where every field 
    is an object containing {"value": Any, "provenance": List[Dict]}.
    """
    if isinstance(resume_cand, list):
        resume_cand = resume_cand[0] if resume_cand else ExtractedCandidate()
    if isinstance(csv_cand, list):
        csv_cand = csv_cand[0] if csv_cand else None

    out = {}

    def _wrap(val, prov):
        return {"value": val, "provenance": prov}

    # Helper for exact match fallback
    def _merge_scalar(field_name: str, resume_val: Any, csv_val: Any, r_method: str = "regex"):
        prov = []
        final_val = resume_val or (csv_val if csv_cand else None)
        if final_val == resume_val and resume_val:
            prov.append({"source": resume_filename, "value": [resume_val] if isinstance(resume_val, list) else resume_val, "method": r_method})
        elif final_val:
            prov.append({"source": csv_filename, "value": [csv_val] if isinstance(csv_val, list) else csv_val, "method": "exact_match"})
        out[field_name] = _wrap(final_val, prov)

    _merge_scalar("candidate_id", resume_cand.candidate_id, csv_cand.candidate_id if csv_cand else None)
    _merge_scalar("full_name", resume_cand.full_name, csv_cand.full_name if csv_cand else None, "font_size_heuristics")
    _merge_scalar("first_name", resume_cand.first_name, csv_cand.first_name if csv_cand else None)
    _merge_scalar("last_name", resume_cand.last_name, csv_cand.last_name if csv_cand else None)
    _merge_scalar("location", resume_cand.location, csv_cand.location if csv_cand else None, "nlp_extraction")
    _merge_scalar("headline", resume_cand.headline, csv_cand.headline if csv_cand else None, "heuristics")
    _merge_scalar("years_experience", resume_cand.years_experience, csv_cand.years_experience if csv_cand else None, "date_math")
    _merge_scalar("current_company", resume_cand.current_company, csv_cand.current_company if csv_cand else None, "nlp_extraction")
    _merge_scalar("title", resume_cand.title, csv_cand.title if csv_cand else None, "nlp_extraction")
    _merge_scalar("links", resume_cand.links, csv_cand.links if csv_cand else None, "regex")
    _merge_scalar("experience", resume_cand.experience, csv_cand.experience if csv_cand else None, "layout_parser")
    _merge_scalar("education", resume_cand.education, csv_cand.education if csv_cand else None, "layout_parser")
    _merge_scalar("additional_details", resume_cand.additional_details, csv_cand.additional_details if csv_cand else None, "layout_parser")

    # EMAILS
    em_prov = []
    combined_emails = []
    for email in resume_cand.emails:
        if email not in combined_emails:
            combined_emails.append(email)
            em_prov.append({"source": resume_filename, "value": [email], "method": "regex"})
    for email in (csv_cand.emails if csv_cand else []):
        if email not in combined_emails:
            combined_emails.append(email)
            em_prov.append({"source": csv_filename, "value": [email], "method": "exact_match"})
    out["emails"] = _wrap(combined_emails, em_prov)

    # PHONES
    ph_prov = []
    combined_phones = []
    def _format_e164(p: str):
        digits = ''.join(c for c in p if c.isdigit())
        if len(digits) == 10: return f"+1{digits}"
        return f"+{digits}" if digits else p
        
    for phone in resume_cand.phones:
        e164 = _format_e164(phone)
        if e164 not in combined_phones:
            combined_phones.append(e164)
            ph_prov.append({"source": resume_filename, "value": [e164], "method": "regex"})
    for phone in (csv_cand.phones if csv_cand else []):
        e164 = _format_e164(phone)
        if e164 not in combined_phones:
            combined_phones.append(e164)
            ph_prov.append({"source": csv_filename, "value": [e164], "method": "exact_match"})
    out["phones"] = _wrap(combined_phones, ph_prov)

    # SKILLS
    sk_prov = []
    combined_primary = list(dict.fromkeys(resume_cand.primary_skills + (csv_cand.primary_skills if csv_cand else [])))
    if resume_cand.primary_skills:
        sk_prov.append({"source": resume_filename, "value": resume_cand.primary_skills, "method": "nlp_extraction"})
    if csv_cand and csv_cand.primary_skills:
        csv_unique = [s for s in csv_cand.primary_skills if s not in resume_cand.primary_skills]
        if csv_unique:
            sk_prov.append({"source": csv_filename, "value": csv_unique, "method": "csv_mapping"})
    out["primary_skills"] = _wrap(combined_primary, sk_prov)

    primary_set = set(combined_primary)
    combined_secondary = [s for s in resume_cand.secondary_skills if s not in primary_set]
    sec_prov = []
    if combined_secondary:
        sec_prov.append({"source": resume_filename, "value": combined_secondary, "method": "nlp_extraction"})
    out["secondary_skills"] = _wrap(combined_secondary, sec_prov)
    
    grouped_skills = []
    if resume_cand.primary_skills:
        grouped_skills.append({"confidence": 1.0, "source": resume_filename, "values": resume_cand.primary_skills})
    if resume_cand.secondary_skills:
        grouped_skills.append({"confidence": 0.8, "source": resume_filename, "values": resume_cand.secondary_skills})
    if csv_cand and csv_cand.primary_skills:
        csv_unique = [s for s in csv_cand.primary_skills if s not in resume_cand.primary_skills]
        if csv_unique:
            grouped_skills.append({"confidence": 1.0, "source": csv_filename, "values": csv_unique})
    out["skills"] = _wrap(grouped_skills, []) # SKILLS array itself is a composite, provenance inside

    # Top level metadata & sources
    out["sources"] = [resume_filename] + ([csv_filename] if csv_cand else [])
    out["metadata"] = resume_cand.metadata.model_dump(mode="json") if hasattr(resume_cand.metadata, "model_dump") else resume_cand.metadata

    return out

def run_multi_source_extraction(
    resume_file_path: str, 
    csv_file_path: str, 
    output_dir: Optional[str] = None,
    resume_filename: str = "resume.pdf",
    csv_filename: str = "candidates.csv"
) -> Dict[str, Any]:
    """
    Dynamically identifies uploaded/provided file formats, runs source parsers on both resume file (.txt/.pdf/.docx)
    and recruiter CSV file, performs candidate record matching, merges multi-source objects, and outputs ultimate result JSON.
    """
    # Parse resume dynamically based on extension (.pdf, .docx, .txt)
    resume_cand = parse_source(resume_file_path, "resume")
    if isinstance(resume_cand, list):
        resume_cand = resume_cand[0] if resume_cand else ExtractedCandidate()

    # Parse recruiter CSV
    csv_candidates = []
    if os.path.exists(csv_file_path):
        csv_candidates = parse_source(csv_file_path, "csv")
        if not isinstance(csv_candidates, list):
            csv_candidates = [csv_candidates]

    # Match candidate against CSV
    matched_csv_cand = match_candidate_record(resume_cand, csv_candidates)

    # Combine profile
    combined_profile = combine_extracted_candidates(
        resume_cand, 
        matched_csv_cand,
        resume_filename=resume_filename,
        csv_filename=csv_filename
    )

    ultimate_output = combined_profile

    # Save to output_dir or default D:/candidate-transformer/sample_outputs/output.json
    if not output_dir:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        output_dir = os.path.join(root_dir, "sample_outputs")
    os.makedirs(output_dir, exist_ok=True)

    out_json_path = os.path.join(output_dir, "output.json")
    try:
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(ultimate_output, f, indent=2, ensure_ascii=False)
        logger.info(f"Ultimate combined extraction output saved to {out_json_path}")
    except Exception as e:
        logger.error(f"Failed to save ultimate output.json: {e}")

    return ultimate_output


def process_sample_inputs(sample_inputs_dir: str, target_format: Optional[str] = None) -> Dict[str, Any]:
    """
    Scans sample_inputs folder for RESUME.txt, RESUME.pdf, or RESUME.docx along with recruiter_export.csv.
    Executes multi-source extraction pipeline and generates output.json.
    """
    csv_path = os.path.join(sample_inputs_dir, "recruiter_export.csv")

    resume_path = None
    # If target format given (e.g. '.pdf' or 'RESUME.pdf'), look specifically for that
    if target_format:
        ext = target_format if target_format.startswith(".") else os.path.splitext(target_format)[1]
        cand_path = os.path.join(sample_inputs_dir, f"RESUME{ext.lower()}")
        if os.path.exists(cand_path):
            resume_path = cand_path

    # Otherwise discover RESUME.* or candidate_resume.*
    if not resume_path:
        for filename in sorted(os.listdir(sample_inputs_dir)):
            if filename == "recruiter_export.csv":
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext in (".txt", ".pdf", ".docx", ".doc") and ("resume" in filename.lower() or filename.startswith("RESUME")):
                resume_path = os.path.join(sample_inputs_dir, filename)
                break

    if not resume_path or not os.path.exists(resume_path):
        raise FileNotFoundError(f"No suitable resume file found in {sample_inputs_dir}")

    return run_multi_source_extraction(resume_path, csv_path)
