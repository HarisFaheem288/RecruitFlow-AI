# RecruitFlow AI — Day 4 Final Evaluation Report

**Generated (UTC):** 2026-10-28T10:55:09.626533+00:00
**Dataset:** 10 synthetic resumes for one Junior AI/ML Engineer job

## Executive summary

The independent, self-recorded manual baseline took **153.16 seconds** for 10 reviews. The local automated extraction and rule-based screening pipeline averaged **0.003918 seconds** per batch across 10 measured runs. These are **different scopes**, not an end-to-end time-savings comparison.

## Timing and scope

| Measurement | Value |
|---|---:|
| Manual review total | 153.16 sec |
| Manual review average | 15.316 sec/resume |
| Automated mean batch | 0.003918 sec |
| Measured-stage ratio | 39,091.37:1 |
| End-to-end recruiter time savings | Not established |

**Interpretation:** The ratio is a comparison of non-equivalent stages, not a validated workflow speedup.

## Agreement with synthetic reference expectations

| Dimension | Manual | Automated |
|---|---:|---:|
| Screening status | 50.0% (5/10) | 80.0% (8/10) |
| Experience classification | 20.0% (2/10) | 90.0% (9/10) |
| Missing required skills (exact set) | 10.0% (1/10) | 100.0% (10/10) |

These are reference-agreement rates, **not independently validated real-world accuracy**.

## Disagreements and evidence

**Candidates with one or more disagreement flags:** 10/10.

**Flag frequencies:**

- `automated_experience`: 1
- `automated_status`: 2
- `manual_experience`: 8
- `manual_missing_skills`: 9
- `manual_status`: 5
- `manual_vs_automated_status`: 4

Evidence notes present: manual 10/10; automated 10/10. These counts do not verify whether the notes are factually supported by resumes.

## Recommendations

- Manually inspect all disagreement cases, especially automated screening-status mismatches.
- Verify evidence notes against the original resume text; presence alone is insufficient.
- Measure complete upload-to-human-approval time before claiming recruiter time savings.
- Evaluate on more diverse, consented and appropriately de-identified resumes before production use.
- Retain human oversight and audit history; do not auto-hire or auto-reject.

## Limitations

- Only ten synthetic resumes; reference expectations are not independently adjudicated ground truth.
- Manual baseline is self-recorded and not independently observed.
- Automated time excludes upload, UI, storage, export, corrections and human approval.
- Local repeated runs may benefit from caches; measured stages are not equivalent.
- Evidence-note presence is not evidence factuality, fairness or reliability.
- No end-to-end recruiter time-savings percentage is established.

## Source files

- `evaluation/09_genuine_baseline_summary.json`
- `evaluation/10_automated_benchmark_summary.json`
- `evaluation/12_accuracy_summary.json`
- `evaluation/15_performance_comparison.json`
- `evaluation/14_disagreements.csv`

## Conclusion

The rule-based prototype demonstrates fast local processing and higher agreement with synthetic scenario expectations than the recorded manual baseline. This small study does not establish production accuracy, fairness or end-to-end recruiter time savings. Human verification and a broader evaluation are required before deployment.
