
"""
RecruitFlow AI - Structured Review Generation

Processes one or more resumes through the existing
document parser and matching engine.

Every review remains a draft requiring human approval.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .document_parser import (
    DocumentExtractionError,
    SUPPORTED_FORMATS,
    extract_from_path,
)
from .matching_engine import screen_candidate
from .schemas import JobDescription


@dataclass
class BatchResult:
    job_id: str
    source_folder: str
    reviews: list[dict[str, Any]] = field(
        default_factory=list
    )
    errors: list[dict[str, str]] = field(
        default_factory=list
    )

    @property
    def successful(self) -> int:
        return len(self.reviews)

    @property
    def failed(self) -> int:
        return len(self.errors)

    @property
    def total(self) -> int:
        return self.successful + self.failed

    def summary(self) -> dict[str, Any]:
        status_counts = {
            "Meets requirements": 0,
            "Missing requirements": 0,
            "Needs clarification": 0,
        }

        for item in self.reviews:
            status = item["review"]["review_status"]
            status_counts[status] = (
                status_counts.get(status, 0) + 1
            )

        return {
            "job_id": self.job_id,
            "total_files": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "review_status_counts": status_counts,
            "human_approval_required": True,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary(),
            "source_folder": self.source_folder,
            "reviews": self.reviews,
            "errors": self.errors,
        }


def candidate_id_from_path(path: Path) -> str:
    """
    Convert synthetic resume filenames to candidate IDs.

    candidate_01.txt -> C01
    other_resume.pdf -> OTHER_RESUME
    """
    stem = path.stem.strip()

    if not stem:
        raise ValueError("Resume filename is invalid.")

    if stem.lower().startswith("candidate_"):
        suffix = stem[len("candidate_"):]

        if suffix.isdigit():
            return "C" + suffix

    return stem.upper()


def generate_review(
    path: str | Path,
    job: JobDescription,
) -> dict[str, Any]:
    """
    Extract and screen a single resume.

    Returns document metadata and a structured draft review.
    """
    path = Path(path)

    extraction = extract_from_path(path)

    candidate_id = candidate_id_from_path(path)

    review = screen_candidate(
        job=job,
        candidate_id=candidate_id,
        resume_text=extraction.text,
    )

    return {
        "source_file": path.name,
        "document": {
            "file_type": extraction.file_type,
            "character_count": extraction.character_count,
            "page_count": extraction.page_count,
            "warnings": list(extraction.warnings),
        },
        "review": review.to_dict(),
    }


def process_batch(
    folder: str | Path,
    job: JobDescription,
) -> BatchResult:
    """
    Process supported files in one folder.

    Errors are recorded individually.
    A single bad resume does not stop the batch.

    Duplicate candidate IDs are not silently overwritten.
    """
    folder = Path(folder)

    if not folder.is_dir():
        raise ValueError(
            f"Resume folder does not exist: {folder}"
        )

    result = BatchResult(
        job_id=job.job_id,
        source_folder=str(folder),
    )

    files = sorted(
        (
            path for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_FORMATS
        ),
        key=lambda path: path.name.casefold(),
    )

    if not files:
        raise ValueError(
            "No supported TXT, PDF, or DOCX files found."
        )

    seen_ids = set()

    for path in files:
        try:
            candidate_id = candidate_id_from_path(path)

            if candidate_id in seen_ids:
                raise ValueError(
                    f"Duplicate candidate ID: {candidate_id}"
                )

            item = generate_review(path, job)
            seen_ids.add(candidate_id)
            result.reviews.append(item)

        except (
            DocumentExtractionError,
            ValueError,
            OSError,
        ) as exc:
            result.errors.append({
                "source_file": path.name,
                "error": str(exc),
            })

    return result
