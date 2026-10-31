# RecruitFlow AI — Professional Case Study

**Project:** RecruitFlow AI  
**Category:** Recruitment workflow automation / explainable rule-based screening  
**Implementation:** Python, Streamlit, SQLite, PyMuPDF, python-docx, pandas, pytest  
**Project scope:** Five-day prototype; this case study covers implementation and evaluation completed through Day 4  
**Evaluation sample:** Ten synthetic resumes for a Junior AI/ML Engineer role

## Executive Summary

RecruitFlow AI is a recruiter-assistance prototype that extracts text from TXT, PDF and DOCX resumes, compares candidate evidence with job requirements, generates structured draft screening reviews, and lets a human reviewer correct and approve those reviews. Reviews and audit history are stored in SQLite, and a Streamlit interface provides screening, review and analytics workflows. The tool is designed to support—not replace—recruiter judgment.

In the ten-resume synthetic evaluation, the automated screening status agreed with scenario reference expectations for **8/10 candidates (80%)**; experience classifications agreed for **9/10 (90%)**; and missing-required-skill sets agreed for **10/10 (100%)**. The full automated test suite passed **195 tests**. Mean local extraction-and-screening time was **0.003918 seconds for ten resumes**, based on ten measured runs after one warm-up. A separate self-recorded manual review of ten resumes took **153.16 seconds** in total. These activities have different scopes; **end-to-end recruiter time savings were not established**.

## 1. Problem and Objective

The project models a small IT recruitment workflow in which a recruiter must inspect incoming resumes, identify required skills, assess experience claims, and record a screening decision with supporting evidence. Manual review can be repetitive and inconsistent, particularly when many candidates apply for the same role.

The prototype objective was to produce repeatable, evidence-oriented **draft** reviews while preserving human oversight. The initial scenario assumed approximately **50 resumes per week**. Project targets included at least 90% evidence accuracy, complete structured reports, and at least nine of ten functional tests passing. These were design targets, not demonstrated outcomes; evidence accuracy was not independently adjudicated in the completed evaluation.

### In scope

- Read TXT, PDF and DOCX resumes and validate supported file types.
- Match required skills using explicit aliases and text evidence.
- Extract and assess numeric experience claims, including conflicting claims.
- Assign draft outcomes: **Meets requirements**, **Missing requirements**, or **Needs clarification**.
- Save and export structured reviews; permit human correction and approval.
- Maintain an audit trail and prevent automated re-screening from overwriting human-reviewed records.
- Display saved-review analytics by job.

### Out of scope

Automatic hiring or rejection, identity verification, unbiased or legally compliant hiring certification, production authentication, and guarantees about real-world accuracy.

## 2. System Design and Workflow

**Flow:** Recruiter enters job criteria → uploads resumes → document validation and text extraction → rule-based evidence matching → structured draft review → optional SQLite save → human review/correction/approval → audit history and analytics.

**Components:**

| Component | Responsibility |
|---|---|
| `src/document_parser.py` | Validates and extracts text from TXT, PDF and DOCX; reports extraction errors |
| `src/matching_engine.py` | Finds skill evidence and interprets numeric experience claims |
| `src/schemas.py` and `src/validators.py` | Define and validate structured job, candidate and review records |
| `src/review_generator.py` | Processes individual files and batches, isolating failures |
| `src/reporting.py` | Exports review data in CSV, JSON and Markdown formats |
| `src/database.py` | Persists jobs and reviews, records human changes, protects reviewed records |
| `src/analytics.py` | Aggregates saved reviews and identifies records requiring attention |
| `app.py` | Streamlit interface for screening, saved reviews, human decisions and analytics |

The screening engine is **rule-based**, not an LLM classifier. This supports predictable execution and traceable matching, but its ability to interpret nuanced resume language is limited.

## 3. Human Oversight and Safeguards

Every automated review begins as **Pending**. A recruiter can inspect the review, correct matched or missing skills, revise experience and screening statuses, provide a reason, and record an approval decision. Approval refers to verification of the **screening review**, not a hiring decision.

The SQLite audit log stores before-and-after review snapshots with reviewer information and timestamps. A protected save path prevents a subsequent automated batch from overwriting records that have been human-reviewed, even when their approval state changes. Input validation, document-size checks, error isolation and CSV formula-injection protection provide additional prototype safeguards.

These controls are not a substitute for production access control, privacy engineering or independent security assessment.

## 4. Evaluation Method

The evaluation used ten synthetic TXT resumes (`C01`–`C10`) for a Junior AI/ML Engineer role and scenario reference expectations. The job required Python, Machine Learning, Scikit-learn, Pandas and SQL, with at least one year of relevant experience; preferred skills included TensorFlow, PyTorch, FastAPI, Docker and Git.

Three distinct evidence sources were compared:

1. **Self-recorded independent manual review:** ten resumes reviewed with a timed CLI tool; reviewer decisions and notes saved separately.
2. **Automated benchmark:** one warm-up plus ten measured local batch runs of document extraction and rule-based screening.
3. **Synthetic reference expectations:** candidate-level expected classifications and missing-skill sets used for agreement calculations.

The earlier Day 1 timing entries were arbitrary and **excluded** from the measured manual baseline. The newer manual times were self-recorded and not independently observed. The reference labels were scenario expectations, not independently adjudicated ground truth.

## 5. Results

### Functional verification

The complete test suite reported **195 passed, 0 failed**. The benchmark processed all **10/10** resumes with **zero file-processing failures**.

### Processing time

| Measure | Recorded result |
|---|---:|
| Manual review: ten resumes | **153.16 seconds** |
| Manual mean per resume | **15.32 seconds** |
| Automated mean batch: ten resumes | **0.003918 seconds** |
| Automated mean per resume | **0.000392 seconds** |
| Automated measured runs | **10**, after one warm-up |
| Measured-stage time ratio | **39,091.37:1** |
| End-to-end recruiter time savings | **Not established** |

The time ratio compares different measured activities and **must not** be interpreted as a complete workflow productivity gain. The automated benchmark excludes uploads, Streamlit interaction, database writes, review corrections, recruiter verification and approval. Local caching and repeated execution may influence timings.

### Agreement with synthetic reference expectations

| Dimension | Manual | Automated |
|---|---:|---:|
| Screening status | **5/10 (50%)** | **8/10 (80%)** |
| Experience classification | **2/10 (20%)** | **9/10 (90%)** |
| Missing required skills (exact set) | **1/10 (10%)** | **10/10 (100%)** |

The automated status distribution was **2 Meets**, **6 Missing**, and **2 Needs clarification**. The reference distribution was **2 Meets**, **4 Missing**, and **4 Needs clarification**. The evaluation flagged **all ten candidates** as having at least one disagreement across the compared fields or methods; this does not mean the automated screening status was wrong for all ten.

The automated screening-status mismatches included **C09 and C10**, which were marked Missing requirements by the pipeline but expected Needs clarification in the synthetic reference. This is an actionable example of where rigid decision rules may not capture the intended ambiguity.

Both manual and automated records contained evidence notes for all ten candidates. **Note presence alone does not prove that the notes are factually supported.** Evidence quality still requires human inspection against the original resumes.

## 6. Engineering Decisions and Trade-offs

**Rule-based matching rather than a paid LLM:** lowers operating cost and improves repeatability and traceability; may miss context, synonyms or implicit evidence outside configured patterns.

**Structured schema and validation:** makes outputs consistent and testable; schema completeness does not guarantee semantic correctness.

**Batch error isolation:** a malformed resume does not halt the entire batch; errors still need recruiter follow-up.

**SQLite and Streamlit:** support a lightweight local demonstration; they are not by themselves a production multi-user deployment architecture.

**Human-review protection and audit history:** preserve human decisions across re-screening; the system still requires organizational controls for authorization, privacy and retention.

## 7. Limitations and Risks

- **Small synthetic sample:** only ten resumes; no validated generalization to real applicants, job families or document layouts.
- **Unadjudicated reference labels:** agreement is not equivalent to verified real-world accuracy.
- **Manual review reliability:** self-recorded timing and decisions were not independently observed or checked.
- **Evidence quality:** notes were present, but factual support was not independently scored.
- **Experience extraction:** numeric-pattern rules can struggle with ambiguous or contradictory career histories.
- **Fairness and privacy:** no demographic fairness audit, candidate-consent workflow, access control, encryption-at-rest assessment or retention policy was completed.
- **Timing scope:** measured pipeline speed excludes recruiter verification and other end-to-end steps.
- **Production readiness:** the system is a tested prototype, not a validated autonomous hiring system.

## 8. Recommended Next Steps

1. Independently adjudicate reference labels and inspect each generated evidence note against the source resume.
2. Investigate C09 and C10 and refine clarification rules without overfitting to ten cases.
3. Run an end-to-end timed study that includes uploads, database saves, human verification, corrections and approvals.
4. Expand to a diverse, consented evaluation set with realistic PDF/DOCX layouts and negative/ambiguous examples.
5. Add authentication, role-based permissions, privacy controls, retention rules, monitoring and a documented recruiter escalation process before any real deployment.

## 9. Conclusion

RecruitFlow AI demonstrates a working, test-covered prototype for evidence-oriented resume screening with human approval, auditability and analytics. In a ten-resume synthetic evaluation, the automated rules agreed with reference expectations more often than the self-recorded manual assessments on the measured fields. Local batch processing was fast, but the evaluation does **not** establish end-to-end recruiter time savings, fairness, or production hiring suitability. The strongest supported result is a repeatable screening-assistance workflow that keeps the recruiter responsible for the final review.

## 10. Reproduction and Evidence Files

From `D:\RecruitFlow-AI` with the project virtual environment activated:

```cmd
python -m pytest tests -q
python evaluation/benchmark_automation.py
python evaluation/evaluate_accuracy_day4.py
python evaluation/compare_performance_day4.py
python evaluation/generate_final_evaluation.py
python -m streamlit run app.py
```

Supporting files:

- `evaluation/08_genuine_manual_baseline.csv`
- `evaluation/09_genuine_baseline_summary.json`
- `evaluation/10_automated_benchmark_summary.json`
- `evaluation/11_automated_benchmark_runs.csv`
- `evaluation/12_accuracy_summary.json`
- `evaluation/13_candidate_comparison.csv`
- `evaluation/14_disagreements.csv`
- `evaluation/15_performance_comparison.json`
- `evaluation/16_performance_comparison.md`
- `evaluation/17_final_evaluation_summary.json`
- `evaluation/18_final_evaluation_report.md`

**Status:** Case study drafted from reported Day 1–4 results. Final delivery requires local file verification and reviewer approval.
