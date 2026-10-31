
"""
RecruitFlow AI - Manual Skill-Matching Test
"""

import argparse
import json
import sys
from pathlib import Path

from src.document_parser import (
    extract_from_path,
    DocumentExtractionError,
)
from src.schemas import JobDescription
from src.matching_engine import screen_candidate


def main():
    parser = argparse.ArgumentParser(
        description="Screen a synthetic candidate resume"
    )

    parser.add_argument(
        "resume",
        help="Path to candidate TXT/PDF/DOCX resume"
    )

    args = parser.parse_args()

    job = JobDescription(
        job_id="JOB001",
        title="Junior AI/ML Engineer",
        required_skills=[
            "Python",
            "Machine Learning",
            "Scikit-learn",
            "Pandas",
            "SQL",
        ],
        preferred_skills=[
            "TensorFlow",
            "PyTorch",
            "FastAPI",
            "Docker",
            "Git",
        ],
        min_experience_years=1.0,
    )

    try:
        result = extract_from_path(args.resume)

        candidate_id = Path(
            args.resume
        ).stem.upper().replace("CANDIDATE_", "C")

        review = screen_candidate(
            job=job,
            candidate_id=candidate_id,
            resume_text=result.text,
        )

    except (DocumentExtractionError, ValueError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(
        json.dumps(
            review.to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
