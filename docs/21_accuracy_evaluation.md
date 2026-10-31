# RecruitFlow AI — Day 4, Task 3: Accuracy & Evidence Evaluation

**Status:** Pending local verification.

## Purpose
Compare independent manual decisions and rule-based automated screening against synthetic scenario reference expectations for the same ten resumes. This is **reference agreement**, not independently established real-world accuracy.

## Inputs
- `evaluation/02_expected_results.csv`: expected review status, experience status, and missing required skills.
- `evaluation/08_genuine_manual_baseline.csv`: self-recorded human decisions, notes, and timing.
- `data/resumes/`: original ten synthetic resume files.
- `run_batch.create_demo_job()` and `src.review_generator.process_batch()`: fresh automated predictions.

## Outputs
- `evaluation/12_accuracy_summary.json`: field-level exact-match agreement and coverage.
- `evaluation/13_candidate_comparison.csv`: all candidate decisions side by side.
- `evaluation/14_disagreements.csv`: candidate rows with one or more mismatches.

## Methodology
1. Require identical candidate IDs across reference, manual and automated sets.
2. Compare review status and experience status as exact strings.
3. Compare missing required skills as normalized, case-insensitive sets (order ignored; `None` means empty).
4. Flag differences from reference and human/automation status disagreements.
5. Record whether human and automated evidence notes are present. **Presence is not evidence correctness**: check the source resume text manually before making any factual-support claim.
6. Do not modify the database, previous baseline, or expected labels.

## Known limitations
- Ten synthetic resumes are not representative of a real hiring population.
- Scenario expectations are not independently adjudicated ground truth.
- Self-recorded manual decisions may be incomplete or mistaken.
- Exact-match skill sets do not measure partial correctness.
- Evidence-note presence does not prove that the note is supported by the resume.
- Human and automated outcomes must be reviewed for disagreements before interpreting results.

## Commands
From `D:\RecruitFlow-AI` with the virtual environment activated:

```cmd
python -m pytest tests/test_accuracy_day4.py -v
python -m pytest tests -q
python evaluation/evaluate_accuracy_day4.py
type evaluation\12_accuracy_summary.json
```

## Acceptance criteria
- [ ] New evaluation tests pass.
- [ ] Existing project tests still pass.
- [ ] Candidate count equals 10 with no missing/duplicate IDs.
- [ ] All three output files exist.
- [ ] Every disagreement is retained for investigation.
- [ ] Results are described as reference agreement, not verified real-world accuracy.
