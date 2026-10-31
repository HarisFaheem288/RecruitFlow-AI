# RecruitFlow AI — Five-Minute Demo Script

**Purpose:** Demonstrate the implemented recruitment-screening workflow, human oversight, and measured evaluation without overstating results.

**Target duration:** 5 minutes (300 seconds). **Audience:** Technical reviewer / hiring team.

> Recording guidance: Speak naturally rather than reading every sentence verbatim. UI labels may differ; use the equivalent controls in your installed version. Never present synthetic candidates as real applicants.

## 1. 0:00–0:35 — Problem and objective (35 seconds)

**On screen:** README.md title or Streamlit landing page.

**Say:**

"RecruitFlow AI is a local resume-screening assistant built to reduce repetitive initial review work while keeping a human recruiter in control. A recruiter defines a role, submits resumes, and receives structured reviews of required skills and experience. This is a decision-support prototype, not an autonomous hiring system. For the demonstration, I use ten synthetic candidate resumes."

**Show:** Project name, role description, and synthetic dataset folder.

## 2. 0:35–1:15 — Architecture (40 seconds)

**On screen:** README architecture section or project tree.

**Say:**

"The pipeline extracts text from TXT, PDF and DOCX documents, compares the text with job requirements using rule-based matching, and produces structured reviews. Results can be persisted in SQLite and inspected in a Streamlit interface. The system includes review status, missing-skills information, evidence notes, and a human approval workflow. It also records an audit trail and protects human-reviewed records from accidental overwriting during re-screening."

**Show:** `src/` directory, `app.py`, and `run_batch.py` without opening sensitive or unrelated files.

## 3. 1:15–2:45 — Live screening workflow (90 seconds)

**On screen:** Running Streamlit application.

**Say:**

"Here is the screening workflow. I am using the demonstration job, Junior AI/ML Engineer, with requirements including Python, machine learning, scikit-learn, pandas and SQL, and a minimum of one year of experience. I submit the synthetic resumes, run screening, and inspect the structured output. Each candidate receives a screening status and supporting details rather than an unexplained binary decision. Where information is missing or conflicting, the reviewer can inspect it and make the final judgment."

**Show, in order:**

1. Locate the job description or selected demonstration job.
2. Locate the resume selection/upload/batch control in your actual UI.
3. Run screening if safe to do so; otherwise show existing saved screening results.
4. Open one candidate review and point to screening status, skills and evidence.
5. If available, contrast a Meets requirements review with a Needs clarification or Missing requirements review.

**Important:** Do not assume any specific button label. Do not re-screen a human-reviewed candidate if it could alter the demonstration state. If the UI flow differs, describe what is visible and use previously saved results.

## 4. 2:45–3:30 — Human oversight and audit (45 seconds)

**On screen:** Saved review, human review controls, and audit history.

**Say:**

"The automated output is not a hiring verdict. A recruiter can inspect the evidence, approve a review or request correction, and leave a human decision. Those actions are recorded for traceability. The application also protects human-reviewed records against silent replacement by a later screening run. This separation between machine recommendations and human accountability is central to the design."

**Show:** A previously saved review, human approval/correction status, and audit history. If you cannot demonstrate a real audit entry, state that clearly and show the code or test instead; do not invent an event.

## 5. 3:30–4:30 — Evaluation and limitations (60 seconds)

**On screen:** `evaluation/18_final_evaluation_report.md` or `evaluation/17_final_evaluation_summary.json`.

**Say:**

"I evaluated ten synthetic resumes. The self-recorded independent manual baseline took 153.16 seconds in total. The automated extraction-and-screening benchmark averaged 0.003918 seconds for the ten-resume batch across ten measured runs, after one warmup. Those timings cover different scopes, so I do not claim an end-to-end recruiter time saving. Against synthetic reference expectations, automated screening-status agreement was 80 percent, compared with 50 percent for the manual reviews. Experience agreement was 90 versus 20 percent, and missing-skills agreement was 100 versus 10 percent. All ten candidates had at least one disagreement across the evaluated fields. These are small synthetic-scenario comparisons, not production accuracy or independent ground truth. The project currently has 215 passing automated tests."

**Show:** The summary metrics and limitations. Keep the evaluation report open before recording to avoid scrolling delays.

## 6. 4:30–5:00 — Conclusion (30 seconds)

**On screen:** README and application side by side.

**Say:**

"RecruitFlow AI demonstrates an end-to-end prototype from resume ingestion and structured screening to saved reviews, human oversight and evaluation. Its strengths are reproducible rule-based outputs, an auditable review workflow and automated tests. Before any real hiring use, I would validate on appropriately consented, representative data, test fairness and robustness, improve ambiguous-case handling, and measure full recruiter workflow time. Thank you."

## Recording checklist

- [ ] Confirm the app launches with `python -m streamlit run app.py`.
- [ ] Keep `README.md` and `evaluation/18_final_evaluation_report.md` open.
- [ ] Use synthetic resumes only; avoid personal information.
- [ ] Practice the workflow and check whether re-screening would modify existing reviewed records.
- [ ] Show one structured candidate review and, where available, a real human-review audit entry.
- [ ] Keep recording near 5 minutes; target 4:45–5:15.
- [ ] Check microphone, screen resolution, terminal readability and notifications.
- [ ] Do not claim real-world hiring accuracy, independently verified manual timing, or end-to-end time savings.
