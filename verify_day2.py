
"""
RecruitFlow AI - Day 2 Integration Verification

Verifies:
1. Required project files
2. Synthetic resume count
3. Batch processing results
4. JSON, CSV and Markdown reports
5. Candidate IDs and approval status
6. Candidate C07 conflicting experience
7. Error handling with an invalid PDF

Run:
    python verify_day2.py
"""

import csv
import json
import tempfile
from pathlib import Path

from run_batch import create_demo_job
from src.review_generator import process_batch
from src.reporting import export_all


ROOT = Path(__file__).resolve().parent
RESUME_DIR = ROOT / "data" / "resumes"
OUTPUT_DIR = ROOT / "outputs"


def check(condition, message):
    if not condition:
        raise AssertionError(message)

    print(f"[PASS] {message}")


def main():
    print("=" * 65)
    print("RECRUITFLOW AI - DAY 2 INTEGRATION VERIFICATION")
    print("=" * 65)

    required_files = [
        "run_batch.py",
        "src/schemas.py",
        "src/validators.py",
        "src/document_parser.py",
        "src/matching_engine.py",
        "src/review_generator.py",
        "src/reporting.py",
        "tests/test_schemas.py",
        "tests/test_document_parser.py",
        "tests/test_matching_engine.py",
        "tests/test_batch_processing.py",
        "data/job_description.txt",
    ]

    for filename in required_files:
        check(
            (ROOT / filename).is_file(),
            f"Required file exists: {filename}",
        )

    check(
        RESUME_DIR.is_dir(),
        "Resume directory exists",
    )

    resumes = sorted(
        RESUME_DIR.glob("candidate_*.txt")
    )

    check(
        len(resumes) == 10,
        "Exactly 10 synthetic TXT resumes exist",
    )

    job = create_demo_job()
    batch = process_batch(RESUME_DIR, job)
    summary = batch.summary()

    check(
        summary["total_files"] == 10,
        "Batch discovered 10 resume files",
    )

    check(
        summary["successful"] == 10,
        "All 10 resumes processed successfully",
    )

    check(
        summary["failed"] == 0,
        "No processing failures",
    )

    check(
        len(batch.reviews) == 10,
        "Exactly 10 structured reviews generated",
    )

    candidate_ids = {
        item["review"]["candidate_id"]
        for item in batch.reviews
    }

    expected_ids = {
        f"C{number:02d}"
        for number in range(1, 11)
    }

    check(
        candidate_ids == expected_ids,
        "Candidate IDs match C01 through C10",
    )

    check(
        all(
            item["review"]["approval_status"] == "Pending"
            for item in batch.reviews
        ),
        "All candidate approvals remain Pending",
    )

    check(
        all(
            item["review"]["evidence_notes"].strip()
            for item in batch.reviews
        ),
        "All reviews contain evidence notes",
    )

    c07 = next(
        item["review"]
        for item in batch.reviews
        if item["review"]["candidate_id"] == "C07"
    )

    check(
        c07["experience_status"] == "Conflicting",
        "C07 conflicting experience preserved",
    )

    check(
        c07["review_status"] == "Needs clarification",
        "C07 requires clarification",
    )

    check(
        bool(c07["warnings"]),
        "C07 contains a warning",
    )

    paths = export_all(batch, OUTPUT_DIR)

    check(
        set(paths) == {"json", "csv", "markdown"},
        "All three report formats generated",
    )

    for name, path in paths.items():
        check(
            path.is_file() and path.stat().st_size > 0,
            f"{name.upper()} report exists and is nonempty",
        )

    json_data = json.loads(
        paths["json"].read_text(encoding="utf-8")
    )

    check(
        json_data["summary"]["successful"] == 10,
        "JSON report contains 10 successful reviews",
    )

    check(
        len(json_data["reviews"]) == 10,
        "JSON report contains all candidate records",
    )

    with paths["csv"].open(
        newline="",
        encoding="utf-8-sig",
    ) as file:
        csv_rows = list(csv.DictReader(file))

    check(
        len(csv_rows) == 10,
        "CSV report contains 10 candidate rows",
    )

    check(
        all(
            row["approval_status"] == "Pending"
            for row in csv_rows
        ),
        "CSV approvals remain Pending",
    )

    markdown = paths["markdown"].read_text(
        encoding="utf-8"
    )

    check(
        "C07" in markdown
        and "Conflicting" in markdown,
        "Markdown report includes C07 conflict",
    )

    # Separate temporary folder: does not modify
    # the real resume dataset.
    with tempfile.TemporaryDirectory() as temp:
        temp_folder = Path(temp)

        (temp_folder / "candidate_01.txt").write_text(
            "Skills: Python, Machine Learning, "
            "Scikit-learn, Pandas, SQL.\n"
            "Experience: 2 years.",
            encoding="utf-8",
        )

        (temp_folder / "broken.pdf").write_bytes(
            b"not a valid PDF"
        )

        error_batch = process_batch(
            temp_folder, job
        )

        check(
            error_batch.successful == 1,
            "Valid resume survives a corrupted file",
        )

        check(
            error_batch.failed == 1,
            "Corrupted PDF is recorded as an error",
        )

    print("\n" + "=" * 65)
    print("DAY 2 INTEGRATION VERIFICATION PASSED")
    print("=" * 65)

    print("\nReport locations:")
    for name, path in paths.items():
        print(f"  {name.upper()}: {path}")

    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (
        AssertionError,
        ValueError,
        OSError,
        KeyError,
        StopIteration,
    ) as exc:
        print(f"\n[FAIL] {exc}")
        raise SystemExit(1)
