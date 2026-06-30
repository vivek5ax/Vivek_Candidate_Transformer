import os
import json
import logging
from typing import Any, Union, List
from app.parsers.base_parser import BaseParser
from app.parsers.csv_parser import CSVParser
from app.parsers.resume_parser import ResumeParser
from app.models.extracted_candidate import ExtractedCandidate
from app.config.settings import settings

logger = logging.getLogger(__name__)


def save_dev_extraction_output(data: Union[ExtractedCandidate, List[ExtractedCandidate]], filename_prefix: str = "extracted_output"):
    """
    Strictly in non-production/development environments, save JSON representation
    of extracted candidate objects to D:/candidate-transformer/sample_outputs for inspection.
    """
    if settings.ENVIRONMENT.lower() == "production":
        return

    try:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        sample_outputs_dir = os.path.join(root_dir, "sample_outputs")
        os.makedirs(sample_outputs_dir, exist_ok=True)

        out_path = os.path.join(sample_outputs_dir, f"{filename_prefix}.json")

        if isinstance(data, list):
            dump_data = [item.model_dump(mode="json") for item in data]
        else:
            dump_data = data.model_dump(mode="json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dump_data, f, indent=2, ensure_ascii=False)
        logger.info(f"[DEV ONLY] Saved extracted objects to {out_path}")
    except Exception as e:
        logger.warning(f"Failed to save dev extraction output: {e}")


def get_parser(source_type: str) -> BaseParser:
    """
    Factory method returning the appropriate parser instance based on source_type.
    Supported types: 'csv', 'resume', 'pdf', 'docx'.
    """
    st = source_type.lower().strip()
    if st in ("csv", "recruiter_csv"):
        return CSVParser()
    elif st in ("resume", "pdf", "docx", "doc", "txt"):
        return ResumeParser()
    else:
        raise ValueError(f"Unsupported source_type: {source_type}")


def parse_source(source: Any, source_type: str, **kwargs) -> Union[ExtractedCandidate, List[ExtractedCandidate]]:
    """
    Convenience method to instantiate parser and extract data in one step.
    Automatically saves extraction output to sample_outputs in dev environment.
    """
    parser = get_parser(source_type)
    res = parser.parse(source, **kwargs)

    # In dev mode, save result to sample_outputs for visual inspection
    file_name = kwargs.get("file_name")
    if file_name:
        clean_name = os.path.splitext(os.path.basename(file_name))[0]
        prefix = f"extracted_{clean_name}"
    else:
        prefix = f"extracted_{source_type}"

    save_dev_extraction_output(res, filename_prefix=prefix)
    return res

