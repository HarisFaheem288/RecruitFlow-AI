# RecruitFlow AI — Day 4 Performance Comparison

**Candidates:** 10 synthetic resumes

## Measured timing

| Measurement | Manual review | Automated extraction + screening |
|---|---:|---:|
| Total / mean batch time (seconds) | 153.160 | 0.003918 |
| Mean per resume (seconds) | 15.316 | 0.000392 |

**Measured-stage time ratio:** 39,091.37:1 (manual time / automated batch time).

**This is not an end-to-end productivity or time-saving claim.** The measurement scopes differ. Automated time excludes UI, upload, storage, exports and human verification.

## Agreement with synthetic reference expectations

| Category | Manual agreement | Automated agreement | Difference (percentage points) |
|---|---:|---:|---:|
| Screening status | 50.0% | 80.0% | +30.0 |
| Experience | 20.0% | 90.0% | +70.0 |
| Missing required skills | 10.0% | 100.0% | +90.0 |

## Limitations

- Ten synthetic resumes; findings are not representative of production recruiting.
- Reference expectations are not independently adjudicated ground truth.
- Manual review times and decisions are self-recorded, not independently observed.
- Automated timings exclude upload, UI, database writes, exports, human verification and approval.
- Repeated local benchmark runs may benefit from OS caches and warm-up effects.
- Evidence-note presence is not proof of evidence quality; human inspection is required.
- No end-to-end time savings percentage is claimed.

## Interpretation

On this synthetic dataset, the rule-based screening pipeline had higher reference agreement than the self-recorded manual baseline. These observations do not establish real-world accuracy, fairness or recruiter productivity. An end-to-end timed workflow study and independent review of reference labels are needed for stronger claims.
