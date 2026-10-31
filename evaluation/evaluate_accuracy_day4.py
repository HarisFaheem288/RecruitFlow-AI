"""Day 4 Task 3: compare manual and automated reviews to synthetic reference labels.

Run from project root: python evaluation/evaluate_accuracy_day4.py
No database updates, no LLM calls, no changes to source resumes.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


EVALUATION = ROOT / "evaluation"
REFERENCE = EVALUATION / "02_expected_results.csv"
MANUAL = EVALUATION / "08_genuine_manual_baseline.csv"
RESUMES = ROOT / "data" / "resumes"
SUMMARY_PATH = EVALUATION / "12_accuracy_summary.json"
COMPARISON_PATH = EVALUATION / "13_candidate_comparison.csv"
DISAGREEMENTS_PATH = EVALUATION / "14_disagreements.csv"
STATUSES = {"Meets requirements", "Missing requirements", "Needs clarification"}
EXPERIENCES = {"Meets", "Below minimum", "Unknown", "Conflicting", "Needs review"}
REQUIRED_REFERENCE = {"candidate_id", "expected_status", "missing_required_skills", "experience_status"}
REQUIRED_MANUAL = {"candidate_id", "review_status", "experience_status", "missing_required_skills", "evidence_notes", "duration_seconds"}


def read_csv(path: Path, required: set[str]) -> dict[str, dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Required input missing: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Missing required CSV columns in {path.name}: {sorted(required - set(reader.fieldnames or []))}")
        rows = list(reader)
    if not rows:
        raise ValueError(f"Input CSV is empty: {path}")
    output = {}
    for row in rows:
        cid = row["candidate_id"].strip()
        if not cid or cid in output:
            raise ValueError(f"Blank or duplicate candidate ID in {path.name}: {cid!r}")
        output[cid] = row
    return output


def parse_skills(value) -> set[str]:
    """Normalize comma/semicolon skill lists; 'None' means no missing skills."""
    if isinstance(value, list):
        parts = value
    elif isinstance(value, str):
        parts = value.replace(";", ",").split(",")
    else:
        raise ValueError("Skills must be a list or delimited string")
    skills = {str(part).strip().casefold() for part in parts if str(part).strip()}
    skills.discard("none")
    return skills


def percent(matches: int, total: int) -> float:
    return round(100 * matches / total, 2) if total else 0.0


def validate_inputs(reference: dict, manual: dict, automated: dict):
    ids = set(reference)
    for label, data in (("manual", manual), ("automated", automated)):
        if set(data) != ids:
            raise ValueError(f"Candidate IDs differ for {label}: missing={sorted(ids - set(data))}, extra={sorted(set(data) - ids)}")
    for cid in sorted(ids):
        ref, human, auto = reference[cid], manual[cid], automated[cid]
        for label, status in (("reference", ref["expected_status"]), ("manual", human["review_status"]), ("automated", auto["review_status"])):
            if status not in STATUSES:
                raise ValueError(f"Invalid {label} review status for {cid}: {status!r}")
        for label, experience in (("reference", ref["experience_status"]), ("manual", human["experience_status"]), ("automated", auto["experience_status"])):
            if experience not in EXPERIENCES:
                raise ValueError(f"Invalid {label} experience status for {cid}: {experience!r}")
        if not human["evidence_notes"].strip():
            raise ValueError(f"Missing manual evidence notes: {cid}")
        if float(human["duration_seconds"]) <= 0:
            raise ValueError(f"Invalid manual duration: {cid}")
        if not isinstance(auto.get("evidence_notes"), str) or not auto["evidence_notes"].strip():
            raise ValueError(f"Missing automated evidence notes: {cid}")
        for value in (ref["missing_required_skills"], human["missing_required_skills"], auto["missing_required_skills"]):
            parse_skills(value)


def evaluate(reference: dict, manual: dict, automated: dict):
    validate_inputs(reference, manual, automated)
    rows = []
    disagreements = []
    metrics = Counter()
    for cid in sorted(reference):
        ref, human, auto = reference[cid], manual[cid], automated[cid]
        expected_missing = parse_skills(ref["missing_required_skills"])
        manual_missing = parse_skills(human["missing_required_skills"])
        auto_missing = parse_skills(auto["missing_required_skills"])
        flags = []
        for label, value, expected in (
            ("manual_status", human["review_status"], ref["expected_status"]),
            ("automated_status", auto["review_status"], ref["expected_status"]),
            ("manual_experience", human["experience_status"], ref["experience_status"]),
            ("automated_experience", auto["experience_status"], ref["experience_status"]),
            ("manual_missing_skills", manual_missing, expected_missing),
            ("automated_missing_skills", auto_missing, expected_missing),
        ):
            match = value == expected
            metrics[label + "_correct"] += int(match)
            if not match:
                flags.append(label)
        if human["review_status"] != auto["review_status"]:
            flags.append("manual_vs_automated_status")
        row = {
            "candidate_id": cid,
            "scenario": ref.get("scenario", ""),
            "reference_status": ref["expected_status"],
            "manual_status": human["review_status"],
            "automated_status": auto["review_status"],
            "reference_experience": ref["experience_status"],
            "manual_experience": human["experience_status"],
            "automated_experience": auto["experience_status"],
            "reference_missing_skills": "; ".join(sorted(expected_missing)),
            "manual_missing_skills": "; ".join(sorted(manual_missing)),
            "automated_missing_skills": "; ".join(sorted(auto_missing)),
            "manual_evidence_present": bool(human["evidence_notes"].strip()),
            "automated_evidence_present": bool(auto["evidence_notes"].strip()),
            "disagreement_flags": "; ".join(flags),
        }
        rows.append(row)
        if flags:
            disagreements.append(row)
    n = len(rows)
    summary = {
        "evaluation_type": "agreement_with_synthetic_reference_expectations",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_count": n,
        "reference_status_counts": dict(Counter(r["expected_status"] for r in reference.values())),
        "manual_status_counts": dict(Counter(r["review_status"] for r in manual.values())),
        "automated_status_counts": dict(Counter(r["review_status"] for r in automated.values())),
        "metrics": {name: {"matches": metrics[name + "_correct"], "total": n, "agreement_percent": percent(metrics[name + "_correct"], n)} for name in ("manual_status", "automated_status", "manual_experience", "automated_experience", "manual_missing_skills", "automated_missing_skills")},
        "manual_automated_status_agreements": sum(r["manual_status"] == r["automated_status"] for r in rows),
        "candidates_with_any_disagreement": len(disagreements),
        "manual_evidence_notes_present": sum(r["manual_evidence_present"] for r in rows),
        "automated_evidence_notes_present": sum(r["automated_evidence_present"] for r in rows),
        "limitations": ["Reference labels are scenario expectations, not independently adjudicated ground truth.", "Evidence presence does not establish factual support or quality; inspect cited resume passages manually.", "Only ten synthetic resumes; no claims about real-world screening accuracy or fairness.", "Manual decisions are self-recorded; no independent observer verified them."],
    }
    return summary, rows, disagreements


def write_csv(path: Path, rows: list[dict], columns: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            # Guard spreadsheet exports against formula injection.
            writer.writerow({key: "'" + str(value) if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value for key, value in row.items()})


def main():
    from run_batch import create_demo_job
    from src.review_generator import process_batch
    reference = read_csv(REFERENCE, REQUIRED_REFERENCE)
    manual = read_csv(MANUAL, REQUIRED_MANUAL)
    batch = process_batch(RESUMES, create_demo_job())
    if batch.errors:
        raise RuntimeError(f"Automated screening failed: {batch.errors}")
    automated = {item["review"]["candidate_id"]: item["review"] for item in batch.reviews}
    if len(automated) != len(batch.reviews):
        raise ValueError("Duplicate automated candidate IDs")
    summary, rows, disagreements = evaluate(reference, manual, automated)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    columns = list(rows[0])
    write_csv(COMPARISON_PATH, rows, columns)
    write_csv(DISAGREEMENTS_PATH, disagreements, columns)
    print(json.dumps({"candidate_count": summary["candidate_count"], "metrics": summary["metrics"], "candidates_with_any_disagreement": len(disagreements), "output_files": [str(SUMMARY_PATH), str(COMPARISON_PATH), str(DISAGREEMENTS_PATH)]}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        print(f"Evaluation failed: {exc}", file=sys.stderr)
        sys.exit(1)
