# RecruitFlow AI — Automated Screening Benchmark

**Day:** 4  
**Task:** 2  
**Status:** Pending local verification

## Objective

Measure the elapsed time of RecruitFlow AI's existing document extraction and rule-based screening pipeline on the same ten synthetic resumes used for the Day 4 human review baseline.

## Files

- `evaluation/benchmark_automation.py`: Benchmark runner.
- `tests/test_automated_benchmark.py`: Unit tests.
- `evaluation/10_automated_benchmark_summary.json`: Generated summary.
- `evaluation/11_automated_benchmark_runs.csv`: Generated run-by-run measurements.

## Methodology

1. Load the same demo job requirements used by `run_batch.py`.
2. Run one unmeasured warm-up batch.
3. Run ten measured batches with `time.perf_counter()`.
4. Fail if any file cannot be processed or results differ between runs.
5. Record mean, median, minimum, maximum, and mean time per resume.
6. Save results to JSON and CSV.

Timing covers **local document extraction and screening**. It excludes Streamlit UI, user uploads, SQLite writes, report exports, human verification and approval. The mean per-resume figure is batch time divided by the number of resumes, not a separately timed individual-resume measurement.

## Commands

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests/test_automated_benchmark.py -v
python -m pytest tests -q
python evaluation/benchmark_automation.py
```

## Limitations

- Small synthetic dataset of ten resumes.
- Single Windows machine and local filesystem.
- Repeated runs can benefit from operating-system caches.
- Manual times are self-recorded and not independently verified.
- No time-saving percentage or accuracy conclusion should be claimed until later evaluation tasks.

## Acceptance criteria

- [ ] New benchmark tests pass.
- [ ] Full existing test suite passes.
- [ ] Exactly ten candidate IDs processed in each run.
- [ ] No processing errors.
- [ ] JSON and CSV files generated.
- [ ] Summary contains measured timing statistics.

**Completion status:** Pending verification using the user's local benchmark output.
