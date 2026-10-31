# \# RecruitFlow AI — Project Scope

# 

# \## 1. Project Overview

# 

# \*\*Project Name:\*\* RecruitFlow AI — Candidate Screening and Review Assistant

# 

# \*\*Domain:\*\* Recruiting and Operations

# 

# \*\*Duration:\*\* Five working days

# 

# \*\*Target User:\*\* Recruitment specialist at a small IT recruitment agency

# 

# \*\*User Type:\*\* Simulated recruiter / proxy user

# 

# \*\*Development Environment:\*\* Windows 11, Python, Streamlit

# 

# \## 2. Problem Statement

# 

# Recruiters repeatedly review candidate resumes, compare qualifications against job descriptions, and prepare structured assessment notes.

# 

# The current simulated workflow involves manually opening resumes, identifying skills and experience, recording findings, and preparing reports.

# 

# This creates repetitive work and opportunities for inconsistent assessments.

# 

# \## 3. Job to Be Done

# 

# When a recruiter receives a candidate resume, they need to identify evidence relevant to the job requirements, record missing or unclear qualifications, and produce a consistent review for human consideration.

# 

# \## 4. Proposed Solution

# 

# RecruitFlow AI will provide a web interface where a recruiter can:

# 

# 1\. Upload a job description.

# 2\. Upload candidate resumes.

# 3\. Extract text from supported documents.

# 4\. Compare candidate evidence against job requirements.

# 5\. Identify missing and uncertain qualifications.

# 6\. Generate structured candidate assessments.

# 7\. Review and correct system-generated findings.

# 8\. Approve the assessment.

# 9\. Export reports and preserve an audit trail.

# 

# \## 5. Minimum Viable Product (MVP)

# 

# The Day 5 MVP will include:

# 

# \- Streamlit web interface.

# \- TXT, PDF, and DOCX text extraction.

# \- Structured job requirements.

# \- Evidence-based required-skill matching.

# \- Experience checks.

# \- Missing-information and contradiction warnings.

# \- Human review and approval.

# \- SQLite review storage.

# \- CSV or JSON report export.

# \- Processing logs and error messages.

# \- Automated functional evaluation.

# 

# \## 6. Integrations

# 

# The MVP will integrate:

# 

# 1\. Local document-processing tools for TXT, PDF, and DOCX.

# 2\. SQLite for persistent review records and approval history.

# 

# External ATS and email integrations are excluded from the MVP.

# 

# \## 7. Non-Goals

# 

# The system will not:

# 

# \- Automatically hire or reject candidates.

# \- Infer personality or cultural fit.

# \- Evaluate protected personal characteristics.

# \- Make unsupported assumptions about candidate qualifications.

# \- Scrape LinkedIn or private recruitment platforms.

# \- Send emails without approval.

# \- Integrate with a production ATS.

# \- Guarantee that an applicant is suitable for employment.

# 

# \## 8. Privacy and Human Oversight

# 

# \- Synthetic candidate data will be used for development and testing.

# \- Candidate assessments are decision-support outputs.

# \- A human recruiter retains final authority.

# \- Missing evidence will not automatically be treated as proof of missing ability.

# \- Assessment corrections and approvals will be recorded.

# \- No production candidate data will be shared with external AI services during MVP testing.

# 

# \## 9. Success Criteria

# 

# The project will target:

# 

# \- At least 40% reduction in screening time.

# \- At least 90% agreement with validated reference evidence.

# \- 100% mandatory report-field completeness.

# \- At least 9 of 10 functional tests passing.

# \- Human approval required for all final shortlist decisions.

# \- Clear handling of invalid or incomplete documents.

# 

# These are targets, not achieved results.

# 

# \## 10. Day 5 Definition of Done

# 

# The MVP is complete when:

# 

# 1\. A non-developer can launch the application using the README.

# 2\. A recruiter can upload a job description and candidate resume.

# 3\. The system produces an evidence-based review.

# 4\. The user can inspect, correct, and approve the review.

# 5\. The assessment and approval are stored.

# 6\. A report can be exported.

# 7\. The 10-case evaluation can be reproduced.

# 8\. Limitations and failure cases are documented.

# 9\. A five-minute demo is recorded.

# 10\. The final repository contains no credentials or private candidate data.



