import os
import shutil
import tempfile
import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.pipeline.extraction_pipeline import run_multi_source_extraction
from app.parsers.parser_factory import parse_source
from app.config.settings import settings
from app.models.projection_config import ProjectionConfig
from app.projection.projection_engine import apply_projection
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Resolve sample_outputs directory (dev-only output store)
_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
SAMPLE_OUTPUTS_DIR = os.path.join(_ROOT_DIR, "sample_outputs")

ALLOWED_RESUME_EXTS = {".pdf", ".docx", ".doc", ".txt"}
ALLOWED_CSV_EXTS = {".csv"}


def _save_upload_to_tmp(upload: UploadFile, allowed_exts: set, label: str) -> str:
    """
    Write an UploadFile's bytes to a temporary file while preserving the original extension.
    Returns the temp file path.
    """
    original_name = upload.filename or ""
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported {label} file format '{ext}'. "
                f"Allowed formats: {', '.join(sorted(allowed_exts))}"
            )
        )

    tmp_dir = tempfile.mkdtemp(prefix="candidate_transformer_")
    tmp_path = os.path.join(tmp_dir, f"upload{ext}")
    try:
        content = upload.file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)
    except Exception as e:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded {label}: {e}")

    return tmp_path


@router.post(
    "/multi-source",
    summary="Extract candidate profile from resume + recruiter CSV",
    description=(
        "Upload a resume file (PDF, DOCX, or TXT) and optionally a recruiter CSV export. "
        "The extraction pipeline parses both sources, matches the candidate record from the CSV, "
        "and returns a combined candidate profile. "
        "The result is also persisted to sample_outputs/output.json for inspection (dev only)."
    ),
    tags=["Extraction"],
    response_class=JSONResponse,
)
async def extract_multi_source(
    resume_file: UploadFile = File(..., description="Candidate resume file (.pdf, .docx, .txt)"),
    csv_file: Optional[UploadFile] = File(None, description="Recruiter CSV export file (.csv) — optional"),
):
    resume_tmp_path = None
    csv_tmp_path = None
    tmp_dirs = []

    try:
        # Save resume upload to temp file
        resume_tmp_path = _save_upload_to_tmp(resume_file, ALLOWED_RESUME_EXTS, "resume")
        tmp_dirs.append(os.path.dirname(resume_tmp_path))

        # Save CSV upload to temp file (if provided)
        if csv_file and csv_file.filename:
            csv_tmp_path = _save_upload_to_tmp(csv_file, ALLOWED_CSV_EXTS, "CSV")
            tmp_dirs.append(os.path.dirname(csv_tmp_path))

        # Run multi-source extraction pipeline
        if csv_tmp_path:
            result = run_multi_source_extraction(
                resume_tmp_path,
                csv_tmp_path,
                output_dir=SAMPLE_OUTPUTS_DIR if settings.ENVIRONMENT.lower() != "production" else None,
                resume_filename=resume_file.filename or "resume.pdf",
                csv_filename=csv_file.filename if (csv_file and getattr(csv_file, "filename", None)) else "candidates.csv"
            )
        else:
            # No CSV: only resume extraction
            resume_cand = parse_source(resume_tmp_path, "resume")
            if isinstance(resume_cand, list):
                resume_cand = resume_cand[0] if resume_cand else None
                
            if resume_cand and hasattr(resume_cand, "sources"):
                resume_cand.sources = [resume_file.filename or "resume.pdf"]
                
            result = resume_cand.model_dump(mode="json") if hasattr(resume_cand, "model_dump") else (resume_cand or {})
            
            # Save to sample_outputs (dev only)
            if settings.ENVIRONMENT.lower() != "production":
                import json
                os.makedirs(SAMPLE_OUTPUTS_DIR, exist_ok=True)
                out_path = os.path.join(SAMPLE_OUTPUTS_DIR, "output.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during multi-source extraction")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
    finally:
        # Always clean up temp files
        for d in tmp_dirs:
            shutil.rmtree(d, ignore_errors=True)


@router.post(
    "/resume",
    summary="Extract candidate profile from a single resume file",
    description=(
        "Upload a single resume file (PDF, DOCX, or TXT). "
        "Runs the resume extraction pipeline and returns a structured ExtractedCandidate object. "
        "Result is also persisted to sample_outputs/output.json (dev only)."
    ),
    tags=["Extraction"],
    response_class=JSONResponse,
)
async def extract_resume_only(
    resume_file: UploadFile = File(..., description="Candidate resume file (.pdf, .docx, .txt)"),
):
    resume_tmp_path = None
    tmp_dir = None

    try:
        resume_tmp_path = _save_upload_to_tmp(resume_file, ALLOWED_RESUME_EXTS, "resume")
        tmp_dir = os.path.dirname(resume_tmp_path)

        resume_cand = parse_source(resume_tmp_path, "resume")
        if isinstance(resume_cand, list):
            resume_cand = resume_cand[0] if resume_cand else None

        if not resume_cand:
            raise HTTPException(status_code=422, detail="Could not extract any candidate data from the uploaded resume.")

        result = resume_cand.model_dump(mode="json")

        # Save to sample_outputs/output.json (dev only)
        if settings.ENVIRONMENT.lower() != "production":
            import json
            os.makedirs(SAMPLE_OUTPUTS_DIR, exist_ok=True)
            out_path = os.path.join(SAMPLE_OUTPUTS_DIR, "output.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"resume_extraction": result, "csv_extraction": None, "combined_profile": result}, f, indent=2, ensure_ascii=False)

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during resume extraction")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {e}")
    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


class ProjectionRequest(BaseModel):
    data: dict
    config: ProjectionConfig


@router.post("/project")
def project_extracted_data(req: ProjectionRequest):
    """
    Takes a canonical JSON output and a projection configuration (blueprint).
    Returns a customized JSON tree tailored for the frontend UI.
    """
    try:
        projected = apply_projection(req.data, req.config)
        return JSONResponse(content=projected)
    except Exception as e:
        logger.exception("Error during projection")
        raise HTTPException(status_code=400, detail=str(e))
