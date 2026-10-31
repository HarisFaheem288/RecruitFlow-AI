# \# RecruitFlow AI — Recruitment Analytics

# 

# \*\*Day:\*\* 3  

# \*\*Task:\*\* 5  

# \*\*Status:\*\* Pending verification

# 

# \## 1. Objective

# 

# Show recruiter-facing summary metrics based on saved SQLite candidate reviews.

# 

# \## 2. Files

# 

# \- `src/analytics.py`: Pure summary and attention-flag logic.

# \- `app.py`: Recruitment Analytics sidebar page and charts.

# \- `tests/test\_analytics.py`: 12 automated tests.

# 

# \## 3. Metrics

# 

# The Recruitment Analytics dashboard displays:

# 

# \- \*\*Saved candidate reviews:\*\* Total number of candidate/job review records.

# \- \*\*Screening outcomes:\*\* Meets requirements, Missing requirements, Needs clarification.

# \- \*\*Experience assessments:\*\* Distribution of experience assessment statuses.

# \- \*\*Human approval statuses:\*\* Pending, Approved, Needs correction.

# \- \*\*Candidates needing attention:\*\* Reviews marked Needs correction, Needs clarification, or with Unknown, Conflicting, or Needs review experience.

# 

# A candidate with multiple attention flags is counted only once per candidate/job record.

# 

# Filters apply to job ID. The All jobs view counts review records, so a candidate appearing in multiple jobs may be counted more than once.

# 

# \## 4. Data Source

# 

# The dashboard retrieves saved reviews from the SQLite database using:

# 

# ```python

# list\_reviews(db\_path=DB\_PATH)

# ```

# 

# Analytics refresh on each Streamlit rerun.

# 

# \## 5. Limitations

# 

# \- Historical processing errors are not stored in the current database.

# \- Dashboard metrics do not establish screening accuracy, time savings, or hiring outcomes.

# \- Human approval means a screening review was verified, not that a candidate was hired.

# \- Authentication and database encryption are not implemented.

# \- Cross-job candidate deduplication is not implemented.

# 

# \## 6. Verification

# 

# Open Windows CMD and run:

# 

# ```cmd

# cd /d D:\\RecruitFlow-AI

# .venv\\Scripts\\activate.bat

# python -m pytest tests/test\_analytics.py -v

# python -m pytest tests -q

# python -m streamlit run app.py

# ```

# 

# \*\*Expected results:\*\*

# 

# \- 12 new analytics tests pass.

# \- 110 total tests pass, assuming the previous 98 tests pass.

# \- Streamlit launches successfully.

# \- Recruitment Analytics appears in the sidebar.

# 

# \## 7. Acceptance Checklist

# 

# \- \[ ] Recruitment Analytics appears in the sidebar.

# \- \[ ] Job filter works correctly.

# \- \[ ] Review outcome counts match stored records.

# \- \[ ] Approval status counts match stored records.

# \- \[ ] Experience assessment chart renders.

# \- \[ ] Attention list includes candidate C07 where applicable.

# \- \[ ] No historical processing error count is invented.

# \- \[ ] All 110 automated tests pass.

# 

# \## 8. Completion Status

# 

# \*\*Pending verification.\*\*

# 

# Task 5 will be marked complete after automated tests pass and the Recruitment Analytics dashboard is verified in the browser.

