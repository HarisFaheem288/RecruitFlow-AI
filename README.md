# RecruitFlow AI

**Human-in-the-loop resume screening and evaluation prototype**

RecruitFlow AI is a local Python application that extracts text from candidate resumes, compares documented skills and experience against a job description, produces structured screening reviews, and lets a recruiter inspect, correct, and approve results. It is an **assistive prototype**, not an autonomous hiring decision-maker.

## Project status

- Completed implementation and evaluation using **10 synthetic candidate resumes**.
- **195 automated tests passed** at the end of Day 5, Task 2. Re-run the suite to verify your checkout.
- Evaluation measures agreement with **synthetic scenario expectations**, not real-world hiring accuracy.
- Human approval remains part of the intended workflow.

## Features

- Extract resume text from TXT, PDF, and DOCX files.
- Compare required/preferred skills and stated experience against job requirements using rule-based logic.
- Produce structured reviews with status, missing skills, experience assessment, and evidence notes.
- Screen a folder of resumes in a batch and export results.
- Store jobs and candidate reviews in SQLite.
- Inspect and update reviews in a Streamlit interface, with review history/audit information.
- Protect human-reviewed records against accidental replacement during re-screening.
- Display recruitment analytics in the dashboard.
- Evaluate a manual baseline, automated batch processing, and agreement with synthetic reference expectations.

## Architecture

```text
Resumes (TXT / PDF / DOCX) + Job Description
                    |
                    v
          Document extraction
                    |
                    v
        Rule-based matching engine
                    |
                    v
        Structured candidate reviews
                    |
          +---------+----------+
          |                    |
          v                    v
      Batch export        SQLite storage
                               |
                               v
                      Streamlit dashboard
                               |
                               v
                    Human review and audit
```

Key project files:

| Path | Purpose |
| --- | --- |
| `app.py` | Streamlit user interface and analytics |
| `run_batch.py` | Example job configuration and batch entry point |
| `src/schemas.py` | Job, candidate, and review data models |
| `src/matching_engine.py` | Rule-based screening logic |
| `src/review_generator.py` | Batch review generation |
| `src/database.py` | SQLite persistence, human review, and audit |
| `data/resumes/` | Ten synthetic sample resumes |
| `evaluation/` | Baselines, benchmarks, accuracy analysis, and reports |
| `tests/` | Automated test suite |
| `docs/` | Project documentation and case study |

## Requirements

- Windows 11 (development/test environment)
- Python 3.12 (Python 3.12.8 used during development)
- A local virtual environment and the dependencies required by the project

> **Dependency note:** Install from the project's existing dependency manifest if one is present. The exact manifest and pinned package versions have not been verified in this documentation update. Do not assume a `requirements.txt` exists without checking.

## Local setup (Windows CMD)

```cmd
cd /d D:\RecruitFlow-AI
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

If your checkout includes `requirements.txt`, install dependencies with:

```cmd
python -m pip install -r requirements.txt
```

If the virtual environment is already configured, simply activate it; you do not need to recreate it.

## Run the application

From the activated virtual environment:

```cmd
cd /d D:\RecruitFlow-AI
python -m streamlit run app.py
```

Use the dashboard to screen sample resumes, inspect results, and perform human review. The example job definition is in `run_batch.py` (`create_demo_job()`).

## Run tests

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests -q
```

The most recently user-verified suite before this documentation update had **260 passing tests**. The documentation checks added in Day 5 Task 3 are separate and should be run before claiming a new total.

## Evaluation methodology and results

The evaluation compares **10 synthetic resumes** against synthetic reference expectations. One person timed a manual review of the same set, while an automated benchmark measured local document extraction and rule-based screening. The scopes differ.

| Measure | Manual | Automated |
| --- | ---: | ---: |
| Total manual review time (10 resumes) | 153.16 s | — |
| Mean automated batch processing time (10 resumes) | — | 0.003918 s |
| Screening-status agreement with reference | 50% | 80% |
| Experience assessment agreement | 20% | 90% |
| Missing-skills agreement | 10% | 100% |

**Important limitations:**

- Manual review times were self-recorded and not independently observed.
- Automated benchmark excludes the dashboard, upload, export, SQLite persistence, recruiter corrections, and approval.
- The measured-stage timing ratio is **not** an end-to-end productivity or recruiter time-savings estimate.
- The reference labels are synthetic expectations, not independently adjudicated ground truth.
- Evidence-note presence does not demonstrate that evidence is correct.
- All ten candidates had at least one recorded disagreement across the evaluated dimensions.
- The evaluation is too small and synthetic to support deployment accuracy, fairness, or generalization claims.

See `evaluation/18_final_evaluation_report.md` and `docs/24_professional_case_study.md` for discussion and context.

## Human oversight and responsible use

RecruitFlow AI supports screening and triage. A human recruiter must inspect evidence, resolve ambiguities, and make any consequential decisions. Do not use this prototype to automatically reject applicants or as proof of suitability for production hiring. Before real-world use, conduct representative-data validation, privacy/security review, bias and accessibility testing, and a documented human-review process.

## Documentation

- [`docs/24_professional_case_study.md`](docs/24_professional_case_study.md) — implementation and evaluation case study
- [`docs/25_ai_collaboration_note.md`](docs/25_ai_collaboration_note.md) — AI-assisted development disclosure
- [`docs/26_documentation_guide.md`](docs/26_documentation_guide.md) — project navigation, verification, and documentation maintenance
- [`evaluation/18_final_evaluation_report.md`](evaluation/18_final_evaluation_report.md) — consolidated evaluation

## Known limitations and future work

The current rules can miss nuanced qualifications, conflicting evidence, and ambiguous experience descriptions. Improve parsing, add transparent evidence traceability, evaluate more diverse and independently labeled resumes, and perform human-factors and fairness reviews before considering any production integration.

## License and data

No license is asserted by this README. Confirm the repository's actual license before redistribution. The included candidate examples are synthetic; do not commit real applicant data, credentials, or private recruitment records.
