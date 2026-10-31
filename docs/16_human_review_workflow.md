# \# RecruitFlow AI — Human Review and Approval

# 

# \*\*Day:\*\* 3  

# \*\*Task:\*\* 3  

# \*\*Status:\*\* Pending verification

# 

# \## Objective

# 

# Enable recruiters to review, correct, and explicitly approve AI-generated screening assessments.

# 

# \## Features

# 

# \- Edit matched and missing skills

# \- Correct experience and review statuses

# \- Update evidence notes

# \- Record reviewer identity

# \- Require a verification reason

# \- Approve a verified review

# \- Mark a review as needing correction

# \- Preserve previous and updated review snapshots in an audit table

# 

# \## Approval States

# 

# \- Pending — No human approval recorded

# \- Approved — Recruiter verified the review

# \- Needs correction — Further verification or changes required

# 

# Approval of a screening review is not a decision to hire or reject a candidate.

# 

# \## Safeguards

# 

# \- Reviewer name is mandatory.

# \- Verification reason is mandatory.

# \- Matched and missing skills cannot overlap.

# \- Reviews needing clarification cannot be approved.

# \- Unknown or conflicting experience must be resolved before approval.

# \- Human updates and audit entries are saved in one database transaction.

# 

# \## Database

# 

# The `review\_audit` table records each human action with its reviewer, action, previous review, updated review, and timestamp.

# 

# \## Limitations

# 

# \- Reviewer names are self-reported; authentication is not implemented.

# \- Audit entries are append-only through the application, but database administrators can modify SQLite directly.

# \- The system does not independently verify edited evidence.

# \- Re-running automated screening for the same candidate and job can overwrite the latest human-reviewed record. A later task must address this before production use.

# 

# \## Verification

# 

# ```cmd

# python -m pytest tests/test\_human\_review.py -v

# python -m pytest tests -q

# ```

# 

# Expected result: 88 passing tests.

# 

# \## Acceptance Criteria

# 

# \- \[ ] Human review editor loads

# \- \[ ] Reviewer can save corrections

# \- \[ ] Approval state updates in SQLite

# \- \[ ] Invalid approvals are blocked

# \- \[ ] Audit history is created

# \- \[ ] Existing candidate reviews remain accessible

# \- \[ ] All 88 automated tests pass

# \- \[ ] Browser verification succeeds

