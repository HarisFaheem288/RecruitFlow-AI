# RecruitFlow AI — Day 4, Task 4: Performance Comparison

**Status:** Pending local verification

## Objective

Reproducibly compare the Day 4 genuine manual baseline, automated extraction/screening benchmark, and agreement with synthetic reference expectations.

## Input files

- `evaluation/09_genuine_baseline_summary.json`: ten self-recorded timed manual reviews.
- `evaluation/10_automated_benchmark_summary.json`: one warm-up plus ten local measured batch runs.
- `evaluation/12_accuracy_summary.json`: manual and automated reference-agreement metrics.

The script validates input types, completion, counts, failed files, timing consistency, and agreement percentages. It refuses to combine inconsistent datasets.

## Source code and outputs

- `evaluation/compare_performance_day4.py`: complete comparison implementation.
- `tests/test_performance_comparison_day4.py`: 18 tests.
- `evaluation/15_performance_comparison.json`: machine-readable results, created when script runs.
- `evaluation/16_performance_comparison.md`: readable comparison report, created when script runs.

## Commands (Windows CMD)

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests/test_performance_comparison_day4.py -v
python -m pytest tests -q
python evaluation/compare_performance_day4.py
type evaluation\15_performance_comparison.json
type evaluation\16_performance_comparison.md
```

Expected full-suite test count: **172** if the previously verified 154 tests remain unchanged.

## Interpretation rules

- Report manual total time and automated *mean* batch time, with their different scopes.
- A calculated manual/automated measured-stage ratio is **not** an end-to-end time-saving or productivity claim.
- End-to-end recruiter time savings is intentionally `null` until a full workflow study includes upload, storage, review, correction, and approval.
- Agreement with synthetic reference expectations is not validated real-world accuracy.
- Manual times are self-recorded, not independently observed.
- Evidence note presence is not evidence correctness.

## Acceptance checklist

- [ ] 18 new tests pass.
- [ ] 172 full-suite tests pass.
- [ ] Script runs using existing Day 4 input files.
- [ ] JSON and Markdown outputs are created.
- [ ] Counts and timing match the recorded source data.
- [ ] End-to-end time savings remains `null`.

**Do not mark Task 4 complete until the local outputs are verified.**
