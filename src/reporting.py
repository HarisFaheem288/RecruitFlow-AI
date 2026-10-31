
"""
RecruitFlow AI - Batch Reporting

Exports structured draft reviews to:
- JSON
- CSV
- Markdown

All outputs are intended for human verification.
"""

import csv
import json
from pathlib import Path

from .review_generator import BatchResult


CSV_COLUMNS = [
    "candidate_id",
    "source_file",
    "job_id",
    "file_type",
    "matched_skills",
    "missing_required_skills",
    "experience_status",
    "review_status",
    "approval_status",
    "warnings",
    "evidence_notes",
    "processing_timestamp",
]


def export_json(
    batch: BatchResult,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    output_path.write_text(
        json.dumps(
            batch.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path


def export_csv(
    batch: BatchResult,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_COLUMNS,
        )
        writer.writeheader()

        for item in batch.reviews:
            review = item["review"]
            document = item["document"]

            row = {
                "candidate_id": review["candidate_id"],
                "source_file": item["source_file"],
                "job_id": review["job_id"],
                "file_type": document["file_type"],
                "matched_skills": "; ".join(
                    review["matched_skills"]
                ),
                "missing_required_skills": "; ".join(
                    review["missing_required_skills"]
                ),
                "experience_status": (
                    review["experience_status"]
                ),
                "review_status": review["review_status"],
                "approval_status": (
                    review["approval_status"]
                ),
                "warnings": "; ".join(
                    review["warnings"]
                    + document["warnings"]
                ),
                "evidence_notes": review["evidence_notes"],
                "processing_timestamp": (
                    review["processing_timestamp"]
                ),
            }

            # Reduce spreadsheet formula interpretation risk
            # when exported content is opened in Excel.
            for key, value in row.items():
                if isinstance(value, str):
                    stripped = value.lstrip(
                        " \t\r\n"
                    )
                    if stripped.startswith(
                        ("=", "+", "-", "@")
                    ):
                        row[key] = "'" + value

            writer.writerow(row)

    return output_path


def markdown_safe(value: object) -> str:
    """
    Escape content for a Markdown table cell.
    """
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("\r", " ")
        .replace("\n", " ")
    )


def export_markdown(
    batch: BatchResult,
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True, exist_ok=True
    )

    summary = batch.summary()

    lines = [
        "# RecruitFlow AI — Batch Screening Report",
        "",
        "**Draft assessments — human verification required.**",
        "",
        f"Job ID: {summary['job_id']}",
        "",
        f"Files processed: {summary['total_files']}",
        "",
        f"Successful reviews: {summary['successful']}",
        "",
        f"Failed files: {summary['failed']}",
        "",
        "## Review Summary",
        "",
        "| Candidate | Matched Skills | Missing Skills | "
        "Experience | Review Status | Approval |",
        "|---|---|---|---|---|---|",
    ]

    for item in batch.reviews:
        review = item["review"]

        values = [
            review["candidate_id"],
            ", ".join(review["matched_skills"]),
            ", ".join(
                review["missing_required_skills"]
            ) or "None evidenced as missing",
            review["experience_status"],
            review["review_status"],
            review["approval_status"],
        ]

        lines.append(
            "| " + " | ".join(
                markdown_safe(value)
                for value in values
            ) + " |"
        )

    lines.extend([
        "",
        "## Individual Candidate Evidence",
        "",
    ])

    for item in batch.reviews:
        review = item["review"]
        document = item["document"]

        lines.extend([
            f"### {review['candidate_id']}",
            "",
            f"Source: `{markdown_safe(item['source_file'])}`",
            "",
            f"Review status: {review['review_status']}",
            "",
            f"Experience status: {review['experience_status']}",
            "",
            f"Approval: {review['approval_status']}",
            "",
            "**Evidence notes:**",
            "",
            "```text",
            review["evidence_notes"].replace("```", "'''"),
            "```",
            "",
        ])

        warnings = (
            review["warnings"]
            + document["warnings"]
        )

        if warnings:
            lines.append("**Warnings:**")
            lines.append("")

            for warning in warnings:
                lines.append(
                    f"- {markdown_safe(warning)}"
                )

            lines.append("")

    if batch.errors:
        lines.extend([
            "## Processing Errors",
            "",
        ])

        for error in batch.errors:
            lines.append(
                f"- **{markdown_safe(error['source_file'])}:** "
                f"{markdown_safe(error['error'])}"
            )

        lines.append("")

    lines.extend([
        "## Human Review Notice",
        "",
        "All assessments are preliminary. "
        "A recruiter must verify the underlying resume "
        "evidence before approving any review.",
        "",
    ])

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path


def export_all(
    batch: BatchResult,
    output_dir: str | Path,
) -> dict[str, Path]:
    output_dir = Path(output_dir)

    return {
        "json": export_json(
            batch,
            output_dir / "batch_reviews.json",
        ),
        "csv": export_csv(
            batch,
            output_dir / "batch_reviews.csv",
        ),
        "markdown": export_markdown(
            batch,
            output_dir / "batch_report.md",
        ),
    }
