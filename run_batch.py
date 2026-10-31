
"""
RecruitFlow AI - Batch Processing CLI

Usage:
    python run_batch.py
    python run_batch.py --folder data/resumes --output outputs
"""

import argparse
import sys

from src.schemas import JobDescription
from src.review_generator import process_batch
from src.reporting import export_all


def create_demo_job() -> JobDescription:
    """
    Fixed demo job matching the Day 1 project requirements.
    """
    return JobDescription(
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RecruitFlow AI batch resume screening"
    )

    parser.add_argument(
        "--folder",
        default="data/resumes",
        help="Folder containing resumes",
    )

    parser.add_argument(
        "--output",
        default="outputs",
        help="Directory for generated reports",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("RECRUITFLOW AI - BATCH PROCESSING")
    print("=" * 60)

    job = create_demo_job()

    try:
        batch = process_batch(
            folder=args.folder,
            job=job,
        )

        paths = export_all(
            batch=batch,
            output_dir=args.output,
        )

    except (ValueError, OSError) as exc:
        print(f"[ERROR] {exc}")
        return 1

    summary = batch.summary()

    print(f"\nJob: {job.title}")
    print(f"Job ID: {job.job_id}")
    print(f"Total files: {summary['total_files']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")

    print("\nReview statuses:")

    for status, count in (
        summary["review_status_counts"].items()
    ):
        print(f"  {status}: {count}")

    if batch.errors:
        print("\nProcessing errors:")

        for error in batch.errors:
            print(
                f"  {error['source_file']}: "
                f"{error['error']}"
            )

    print("\nGenerated reports:")

    for format_name, path in paths.items():
        print(f"  {format_name.upper()}: {path}")

    print("\nAll candidate approvals remain Pending.")
    print("=" * 60)

    # Partial failures are reported but do not stop
    # other candidates from being processed.
    return 2 if batch.failed else 0


if __name__ == "__main__":
    sys.exit(main())
