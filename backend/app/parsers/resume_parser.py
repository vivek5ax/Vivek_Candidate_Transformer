import os
import re
import logging
from typing import Any, Union, List, Optional

from app.models.extracted_candidate import ExtractedCandidate
from app.models.parser_metadata import ParserMetadata
from app.parsers.base_parser import BaseParser
from app.extractors.text_extractor import extract_text_from_file
from app.extractors.email_extractor import extract_emails
from app.extractors.phone_extractor import extract_phones
from app.extractors.skill_extractor import extract_skills, extract_skills_section_aware
from app.extractors.name_extractor import extract_name, split_full_name
from app.extractors.section_segmenter import segment_resume_sections
from app.extractors.experience_extractor import extract_experience
from app.extractors.education_extractor import extract_education
from app.extractors.project_extractor import extract_projects
from app.utils.location_utils import parse_location
from app.utils.link_utils import categorize_links

logger = logging.getLogger(__name__)


class ResumeParser(BaseParser):
    """
    Unstructured source parser for candidate resumes (PDF, DOCX, TXT).
    Extracts text and applies deterministic extraction utilities to extract identity, contact, skills, and work history.
    """

    def __init__(self):
        super().__init__(source_type="resume")

    def parse(self, source: Union[str, bytes], **kwargs) -> ExtractedCandidate:
        """
        Parse raw resume content (file path or bytes stream) into an ExtractedCandidate.
        """
        file_name = kwargs.get("file_name", None)
        warnings = []

        # Extract text
        if isinstance(source, str) and os.path.exists(source):
            file_name = file_name or source
            raw_text = extract_text_from_file(source)
        elif isinstance(source, bytes):
            # If bytes, check optional file_name parameter to infer extension
            ext = os.path.splitext(file_name)[1].lower() if file_name else ".pdf"
            dummy_path = f"dummy{ext}"
            raw_text = extract_text_from_file(dummy_path, file_content=source)
        elif isinstance(source, str):
            # Treat raw string directly as resume text
            raw_text = source
        else:
            return self._create_error_candidate(f"Unsupported input type for ResumeParser: {type(source)}", file_name=file_name)

        if not raw_text or not raw_text.strip():
            warnings.append("No text could be extracted from resume file/stream.")
            metadata = ParserMetadata(
                source_type="resume",
                file_name=file_name,
                parse_status="ERROR" if not raw_text else "PARTIAL",
                warnings=warnings
            )
            return ExtractedCandidate(metadata=metadata)

        # Segment resume into canonical sections
        sections = segment_resume_sections(raw_text)

        # Identity & Contact
        full_name = extract_name(raw_text)
        first_name, last_name = split_full_name(full_name) if full_name else (None, None)

        emails = extract_emails(raw_text)
        phones = extract_phones(raw_text)

        # Header metadata extraction (headline, location, links)
        headline = None
        raw_location = None
        raw_links = []
        
        # Extract ALL embedded geometric links from the entire document
        embedded_links = re.findall(r'\[LINK:([^\]\s]+)\]', raw_text)
        for el in embedded_links:
            if el not in raw_links and el.startswith("http"):
                raw_links.append(el.strip())
                
        for line in raw_text.splitlines()[:15]:
            clean_l = re.sub(r'^\[BOLD:[\d.]+\]\s*', '', line).strip()
            if "linkedin.com" in clean_l or "github.com" in clean_l or "http" in clean_l:
                found_links = re.findall(r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9-]+\.[a-zA-Z0-9-./]+)', clean_l)
                for fl in found_links:
                    clean_fl = re.sub(r'^[🔗\s]+', '', fl).strip()
                    if clean_fl not in raw_links and not clean_fl.endswith("."):
                        raw_links.append(clean_fl)
            elif "📍" in clean_l or ("USA" in clean_l and "," in clean_l) or ("," in clean_l and sum(c.isalpha() for c in clean_l) > 5 and len(clean_l) < 30):
                if not raw_location and not any(k in clean_l.lower() for k in ("email", "phone", "http")):
                    raw_location = re.sub(r'^[📍\s]+', '', clean_l).strip()
            elif "|" in clean_l and not any(k in clean_l.lower() for k in ("email:", "phone:", "linkedin", "github", "http", ".com")):
                if len(clean_l) < 70 and not headline and clean_l != full_name:
                    headline = clean_l
        
        links = categorize_links(raw_links)
        location = parse_location(raw_location)

        # Skills extraction
        p_skills, s_skills = extract_skills_section_aware(raw_text)
        
        # Build unified skills array matching target schema
        skills = []
        for pk in p_skills:
            skills.append({"name": pk, "confidence": 1.0, "sources": ["primary"]})
        for sk in s_skills:
            if sk not in p_skills:
                skills.append({"name": sk, "confidence": 0.8, "sources": ["secondary"]})

        # Structured Experience & Education
        exp_text = sections.get("EXPERIENCE", "")
        experience, recent_title, recent_company = extract_experience(exp_text)

        edu_text = sections.get("EDUCATION", "")
        education = extract_education(edu_text)

        # Additional Details (Projects, Open Source, Certifications, Achievements, etc.)
        additional_details = {}
        for sec_name, content in sections.items():
            if sec_name not in ("HEADER", "SUMMARY", "TECHNICAL_SKILLS", "EXPERIENCE", "EDUCATION") and content.strip():
                if sec_name == "PROJECTS":
                    proj_entries = extract_projects(content)
                    additional_details[sec_name] = proj_entries if proj_entries else [l.strip() for l in content.splitlines() if l.strip()]
                else:
                    additional_details[sec_name] = [l.strip() for l in content.splitlines() if l.strip()]

        # Years of experience calculation
        years_experience = None
        summary_text = sections.get("SUMMARY", "") or raw_text[:1000]
        y_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*years? (?:of )?experience', summary_text, re.IGNORECASE)
        if y_match:
            try:
                years_experience = float(y_match.group(1))
            except ValueError:
                pass

        # Title and current company resolution
        title, company = self._heuristic_title_company(raw_text, recent_title, recent_company)

        if not full_name and not emails and not phones:
            warnings.append("Resume extraction found no clear name, email, or phone.")

        metadata = ParserMetadata(
            source_type="resume",
            file_name=file_name or "resume_doc",
            parse_status="PARTIAL" if warnings else "SUCCESS",
            warnings=warnings,
            raw_source_id=os.path.basename(file_name) if file_name else "resume_doc"
        )

        return ExtractedCandidate(
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            emails=emails,
            phones=phones,
            primary_skills=p_skills,
            secondary_skills=s_skills,
            skills=skills,
            title=title,
            current_company=company,
            education=education,
            experience=experience,
            years_experience=years_experience,
            headline=headline,
            location=location,
            links=links,
            additional_details=additional_details if additional_details else None,
            metadata=metadata
        )

    def _heuristic_title_company(self, text: str, recent_title: Optional[str] = None, recent_company: Optional[str] = None):
        """
        Resolves Title and Company, favoring structured experience parser results over naive heuristics.
        """
        if recent_title or recent_company:
            return recent_title, recent_company

        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:20]:
            match = re.search(r'^([A-Z][A-Za-z0-9\s/&]+)\s+(?:at|@|\||-)\s+([A-Z][A-Za-z0-9\s.,&]+)$', line)
            if match and not any(k in line.lower() for k in ("developer |", "engineer |", "email:", "phone:")):
                t, c = match.group(1).strip(), match.group(2).strip()
                if 2 < len(t) < 50 and 2 < len(c) < 50:
                    return t, c
        return None, None

    def _create_error_candidate(self, err_msg: str, file_name: Optional[str] = None) -> ExtractedCandidate:
        metadata = ParserMetadata(
            source_type="resume",
            file_name=file_name,
            parse_status="ERROR",
            warnings=[err_msg]
        )
        return ExtractedCandidate(metadata=metadata)
