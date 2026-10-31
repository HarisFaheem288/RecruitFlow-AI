# RecruitFlow AI — Documentation Guide

## 1. Purpose

This guide identifies the project's main files, shows how to run its application and tests on Windows, and explains how to interpret the evaluation artifacts. It supplements the root `README.md`.

## 2. Project layout

| Location | Description |
| --- | --- |
| `README.md` | GitHub-facing overview, quick start, architecture, results and caveats |
| `app.py` | Streamlit dashboard |
| `run_batch.py` | Demonstration job and batch runner |
| `src/` | Screening models, matching logic, batch processing, SQLite storage |
| `data/resumes/` | Ten synthetic resumes used for evaluation |
| `tests/` | Automated verification |
| `evaluation/` | Manual baseline, automated benchmark, comparisons, and final report |
| `docs/24_professional_case_study.md` | Professional case study |
| `docs/25_ai_collaboration_note.md` | AI collaboration disclosure |
| `docs/26_documentation_guide.md` | This guide |

## 3. Windows CMD quick start

Use the existing virtual environment if it is already configured:

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests -q
python -m streamlit run app.py
```

For a new checkout, create a Python 3.12 virtual environment and install from the **existing** project dependency manifest, if present. Confirm the manifest name before running an installation command.

## 4. Main workflow

1. Define a job and its required and preferred skills.
2. Load resumes from the local input folder.
3. Extract text and generate structured screening reviews.
4. Inspect the results in the Streamlit interface.
5. Correct or approve candidate reviews as appropriate; retain the audit trail.
6. Export or analyze results only after checking their meaning and scope.

The project is a human-in-the-loop decision-support prototype, not an automatic hiring authority.

## 5. Evaluation source-of-truth files

| File | Content |
| --- | --- |
| `evaluation/09_genuine_baseline_summary.json` | Self-recorded manual review timing |
| `evaluation/10_automated_benchmark_summary.json` | Local automated batch processing timing |
| `evaluation/12_accuracy_summary.json` | Agreement with synthetic reference expectations |
| `evaluation/15_performance_comparison.json` | Timing comparison and scope qualifications |
| `evaluation/17_final_evaluation_summary.json` | Final aggregate evaluation |
| `evaluation/18_final_evaluation_report.md` | Narrative final evaluation |

The 10-resume manual baseline totaled **153.16 seconds**. The automated batch averaged **0.003918 seconds** for extraction and screening. These are **not equivalent end-to-end activities**, so no end-to-end recruiter time savings were established.

Agreement with synthetic reference expectations was **80%** for automated screening status, **90%** for experience assessment, and **100%** for missing-skills lists. These are scenario-agreement metrics, not real-world accuracy estimates.

## 6. Reproducibility and interpretation

The evaluation uses ten synthetic examples, and the manual timing was self-recorded. The automated benchmark excludes UI, upload, persistence, export, corrections, and approval. The reference labels are synthetic expectations rather than independently verified ground truth. Re-running performance measurements on another machine may produce different timings.

Do not report the measured-stage speed ratio as end-to-end recruiter productivity improvement. Do not describe the synthetic agreement rates as deployment accuracy. Do not infer evidence quality from the presence of evidence notes alone.

## 7. Documentation checks

Run the documentation-specific tests and the complete suite:

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests\test_documentation_day5.py -v
python -m pytest tests -q
```

The previously verified suite contained **195 passing tests** before this task. The new documentation tests increase the count only after they pass locally.

## 8. Repository publication checklist

- Confirm no candidate PII, local database, API keys, `.env`, or virtual environment are staged for Git.
- Verify dependency installation instructions against the actual repository manifest.
- Confirm README links and case-study metrics against the evaluation JSON outputs.
- Confirm a license exists before describing reuse permissions.
- Keep the demo focused on synthetic data and human review.

## 9. Maintaining this documentation

Update README metrics only after re-running evaluation and verifying the corresponding JSON outputs. Update paths and installation instructions whenever the application layout or dependencies change. Record changes to matching logic or review safeguards alongside their tests.
