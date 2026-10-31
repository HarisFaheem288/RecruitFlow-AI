"""Day 4 Task 2: reproducible automated resume screening benchmark.

Run from the project root: python evaluation/benchmark_automation.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_batch import create_demo_job
from src.review_generator import process_batch

DEFAULT_RESUMES = ROOT / "data" / "resumes"
DEFAULT_OUTPUT = ROOT / "evaluation"


def benchmark(resume_dir: Path, iterations: int = 10, warmups: int = 1, clock=None):
    """Benchmark extraction + screening, excluding export, DB, UI, and approval."""
    if clock is None:
        clock = time.perf_counter
    if iterations < 1 or warmups < 0:
        raise ValueError("Iterations must be >= 1 and warmups must be >= 0.")
    if not resume_dir.is_dir():
        raise ValueError(f"Resume directory not found: {resume_dir}")

    job = create_demo_job()
    timings = []
    reference_ids = None
    reference_statuses = None
    reference_files = None
    for index in range(warmups + iterations):
        start = clock()
        result = process_batch(resume_dir, job)
        elapsed = clock() - start
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError("Invalid clock measurement.")
        if result.failed:
            details = "; ".join(f"{e['source_file']}: {e['error']}" for e in result.errors)
            raise RuntimeError(f"Benchmark aborted: {result.failed} file(s) failed: {details}")
        if not result.successful:
            raise RuntimeError("Benchmark aborted: no resumes processed.")
        ids = [entry["review"]["candidate_id"] for entry in result.reviews]
        statuses = [(entry["review"]["candidate_id"], entry["review"]["review_status"]) for entry in result.reviews]
        files = [entry["source_file"] for entry in result.reviews]
        if len(ids) != len(set(ids)):
            raise RuntimeError("Benchmark aborted: duplicate candidate IDs.")
        if reference_ids is None:
            reference_ids, reference_statuses, reference_files = ids, statuses, files
        elif ids != reference_ids or statuses != reference_statuses or files != reference_files:
            raise RuntimeError("Benchmark aborted: inconsistent results between iterations.")
        if index >= warmups:
            timings.append(round(elapsed, 6))

    return {
        "benchmark_type": "automated_document_extraction_and_screening",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "job_id": job.job_id,
        "source_folder": str(resume_dir.resolve()),
        "resume_count": len(reference_ids),
        "candidate_ids": reference_ids,
        "source_files": reference_files,
        "warmup_runs": warmups,
        "measured_runs": iterations,
        "run_seconds": timings,
        "total_seconds_mean": round(statistics.mean(timings), 6),
        "total_seconds_median": round(statistics.median(timings), 6),
        "total_seconds_min": round(min(timings), 6),
        "total_seconds_max": round(max(timings), 6),
        "seconds_per_resume_mean": round(statistics.mean(timings) / len(reference_ids), 6),
        "screening_status_counts": {
            status: sum(value == status for _, value in reference_statuses)
            for status in ("Meets requirements", "Missing requirements", "Needs clarification")
        },
        "status_by_candidate": dict(reference_statuses),
        "failed_files": 0,
        "scope": "Local batch extraction and rule-based screening only; excludes UI, file upload, report export, SQLite, recruiter corrections and approval.",
        "limitations": "Single machine, synthetic resumes, repeated local runs; caching and operating-system effects may influence timings.",
    }


def save_results(summary: dict, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "10_automated_benchmark_summary.json"
    csv_path = output_dir / "11_automated_benchmark_runs.csv"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["run", "elapsed_seconds", "resume_count", "seconds_per_resume"])
        writer.writeheader()
        for index, elapsed in enumerate(summary["run_seconds"], 1):
            writer.writerow({
                "run": index,
                "elapsed_seconds": elapsed,
                "resume_count": summary["resume_count"],
                "seconds_per_resume": round(elapsed / summary["resume_count"], 6),
            })
    return json_path, csv_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Benchmark RecruitFlow AI automated resume screening")
    parser.add_argument("--resumes", type=Path, default=DEFAULT_RESUMES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--warmups", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        summary = benchmark(args.resumes, args.iterations, args.warmups)
        json_path, csv_path = save_results(summary, args.output)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f"Benchmark failed: {exc}\n")
    print(f"Resumes processed: {summary['resume_count']}")
    print(f"Warmups: {summary['warmup_runs']} | Measured runs: {summary['measured_runs']}")
    print(f"Mean batch time: {summary['total_seconds_mean']:.6f} sec")
    print(f"Median batch time: {summary['total_seconds_median']:.6f} sec")
    print(f"Mean per resume: {summary['seconds_per_resume_mean']:.6f} sec")
    print(f"Failed files: {summary['failed_files']}")
    print(f"Summary: {json_path}")
    print(f"Runs: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
