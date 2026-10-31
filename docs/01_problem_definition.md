# RecruitFlow AI — Problem Definition

## Target User
A recruitment specialist working at a small IT recruitment agency.

**User type:** Simulated/proxy user.

## Job to Be Done
When a new candidate applies for a job, the recruiter needs to compare the resume against the job requirements, identify supporting evidence, record missing qualifications, and prepare a review for human shortlisting.

## Current Problem
The recruiter manually opens each resume, searches for relevant qualifications, compares them with the job description, and records findings in a spreadsheet.

This process involves repetitive reading, manual data entry, and inconsistent candidate summaries.

## Assumptions
- Approximately 50 resumes are reviewed per week.
- Each manual review may take 5–10 minutes.
- The recruiter uses email, PDF documents, and Excel.
- Hiring decisions require human approval.

These assumptions must be validated or labeled as synthetic in the final case study.

## Proposed Improvement
Build a system that:
1. Accepts a job description and candidate resume.
2. Extracts relevant candidate information.
3. Compares evidence against job requirements.
4. Identifies missing or uncertain qualifications.
5. Generates a structured review report.
6. Allows the recruiter to correct and approve results.
7. Records review decisions for later reference.

## Scope
The system supports candidate screening preparation, not autonomous hiring.

## Non-Goals
- Automatically rejecting applicants.
- Making final hiring decisions.
- Predicting candidate personality or cultural fit.
- Evaluating protected personal characteristics.
- Integrating directly with a production applicant tracking system.
