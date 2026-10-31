# RecruitFlow AI — Genuine Manual Screening Baseline

**Day:** 4  
**Task:** 1  
**Status:** Pending independent manual review and verification

## Objective
Record actual recruiter decisions and elapsed review times for the ten synthetic resumes against `data/job_description.txt`.

## Integrity of measurement
The original `evaluation/03_manual_baseline.csv` contains arbitrary durations and is not a valid measured baseline. Preserve it unchanged; do not use its timing values to claim productivity gains.

For this task, independently read each resume and record a decision without viewing RecruitFlow AI's predicted results or `evaluation/02_expected_results.csv`. The timer starts when the resume text is displayed and stops after evidence notes are submitted. These are self-recorded times, not externally observed timings. Pauses, interruptions and differences between CLI viewing and normal recruiter practice are limitations.

## Inputs
- `data/job_description.txt`
- `data/resumes/candidate_01.txt` through `candidate_10.txt`

## Outputs
- `evaluation/08_genuine_manual_baseline.csv`
- `evaluation/09_genuine_baseline_summary.json`

## Run
```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests/test_manual_review_day4.py -v
python evaluation/manual_review_day4.py
```

The CLI saves each completed review and can resume after stopping. Do not manually populate times. Preserve original results and document any interruptions.

## Acceptance criteria
- [ ] Twelve automated tests pass
- [ ] All ten resumes independently reviewed
- [ ] Each record includes review status, experience status, skill assessments, evidence notes and measured duration
- [ ] Summary says `"complete": true` and `"reviewed_count": 10`
- [ ] Original Day 1 baseline is unchanged
- [ ] Timing limitations disclosed in final evaluation

## Important interpretation
A human baseline is not an accuracy ground truth by itself. Accuracy requires independently defined reference labels or adjudicated reviews, and agreement with the automation must not be misrepresented as correctness.
