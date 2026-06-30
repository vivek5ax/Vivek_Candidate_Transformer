import csv
import io
import os
import logging
from typing import Any, Union, List, Dict, Optional

from app.models.extracted_candidate import ExtractedCandidate
from app.models.parser_metadata import ParserMetadata
from app.parsers.base_parser import BaseParser
from app.extractors.name_extractor import split_full_name
from app.extractors.skill_extractor import extract_skills

logger = logging.getLogger(__name__)


class CSVParser(BaseParser):
    """
    Structured source parser for Recruiter CSV exports.
    Handles tabular rows containing columns such as name, email, phone, current_company, title, skills.
    """

    def __init__(self):
        super().__init__(source_type="csv")

    def parse(self, source: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]], **kwargs) -> Union[ExtractedCandidate, List[ExtractedCandidate]]:
        """
        Parse CSV data into ExtractedCandidate object(s).
        Input can be:
        - file path (str ending in .csv)
        - raw CSV string or bytes
        - single dictionary representing a row
        - list of dictionaries representing rows
        """
        file_name = kwargs.get("file_name", None)
        if isinstance(source, str) and os.path.exists(source):
            file_name = file_name or source
            try:
                with open(source, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            except Exception as e:
                logger.error(f"Failed to read CSV file {source}: {e}")
                return self._create_error_candidate(f"File read failure: {e}", file_name=file_name)
            return [self._parse_row(row, row_index=idx, file_name=file_name) for idx, row in enumerate(rows)]

        elif isinstance(source, (str, bytes)):
            try:
                if isinstance(source, bytes):
                    source = source.decode("utf-8", errors="ignore")
                reader = csv.DictReader(io.StringIO(source))
                rows = list(reader)
            except Exception as e:
                logger.error(f"Failed to parse CSV text string: {e}")
                return self._create_error_candidate(f"CSV string parsing error: {e}", file_name=file_name)
            return [self._parse_row(row, row_index=idx, file_name=file_name) for idx, row in enumerate(rows)]

        elif isinstance(source, list):
            return [self._parse_row(row, row_index=idx, file_name=file_name) for idx, row in enumerate(source)]

        elif isinstance(source, dict):
            return self._parse_row(source, row_index=0, file_name=file_name)

        else:
            return self._create_error_candidate(f"Unsupported input type for CSVParser: {type(source)}", file_name=file_name)

    def _parse_row(self, row: Dict[str, Any], row_index: int = 0, file_name: Optional[str] = None) -> ExtractedCandidate:
        warnings = []
        if not row:
            warnings.append(f"Row {row_index} is completely empty.")

        # Normalize column keys
        norm_row = {}
        for k, v in row.items():
            if k is not None:
                clean_key = str(k).strip().lower().replace(" ", "_").replace("-", "_")
                norm_row[clean_key] = v

        def get_val(*keys) -> Optional[str]:
            for k in keys:
                val = norm_row.get(k)
                if val is not None and str(val).strip() != "":
                    return str(val).strip()
            return None

        # Extract name
        full_name = get_val("name", "full_name", "candidate_name", "employee_name")
        first_name = get_val("first_name", "given_name")
        last_name = get_val("last_name", "family_name", "surname")

        if full_name and not first_name:
            fn, ln = split_full_name(full_name)
            first_name = fn
            last_name = ln
        elif first_name and not full_name:
            full_name = f"{first_name} {last_name or ''}".strip()

        # Extract contact info
        raw_email = get_val("email", "emails", "email_address", "primary_email")
        emails = [raw_email] if raw_email else []

        raw_phone = get_val("phone", "phones", "phone_number", "mobile", "contact_number")
        phones = [raw_phone] if raw_phone else []

        # Extract professional fields
        current_company = get_val("current_company", "company", "employer", "organization")
        title = get_val("title", "job_title", "role", "designation", "current_title")
        headline = get_val("headline", "summary", "bio")

        # Extract skills
        raw_skills = get_val("skills", "skill_set", "technologies")
        skills = extract_skills(raw_skills) if raw_skills else []

        # Extract candidate ID if present
        candidate_id = get_val("id", "candidate_id", "applicant_id")

        # Extract missing fields
        raw_years = get_val("years_experience", "experience_years", "yoe")
        years_experience = None
        if raw_years:
            try:
                years_experience = float(raw_years)
            except ValueError:
                pass

        location_val = get_val("location", "address")
        city_val = get_val("city")
        region_val = get_val("region", "state", "province")
        country_val = get_val("country")
        
        location = None
        if location_val or city_val or region_val or country_val:
            location = {}
            if location_val: location["raw"] = location_val
            if city_val: location["city"] = city_val
            if region_val: location["region"] = region_val
            if country_val: location["country"] = country_val

        linkedin = get_val("linkedin")
        github = get_val("github")
        portfolio = get_val("portfolio")
        links = {}
        if linkedin: links["linkedin"] = linkedin
        if github: links["github"] = github
        if portfolio: links["portfolio"] = portfolio
        if not links: links = None

        if not full_name and not emails and not phones:
            warnings.append(f"Row {row_index} lacks sufficient candidate identity (name/email/phone).")

        metadata = ParserMetadata(
            source_type="csv",
            file_name=file_name or f"row_{row_index}",
            parse_status="PARTIAL" if warnings else "SUCCESS",
            warnings=warnings,
            raw_source_id=f"csv_row_{row_index}"
        )

        return ExtractedCandidate(
            candidate_id=candidate_id,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            emails=emails,
            phones=phones,
            location=location,
            links=links,
            years_experience=years_experience,
            primary_skills=skills,
            current_company=current_company,
            title=title,
            headline=headline,
            metadata=metadata
        )

    def _create_error_candidate(self, err_msg: str, file_name: Optional[str] = None) -> ExtractedCandidate:
        metadata = ParserMetadata(
            source_type="csv",
            file_name=file_name,
            parse_status="ERROR",
            warnings=[err_msg]
        )
        return ExtractedCandidate(metadata=metadata)
