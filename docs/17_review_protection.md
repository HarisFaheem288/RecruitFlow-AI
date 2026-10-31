# \# RecruitFlow AI — Safe Re-screening and Review Protection

# 

# \*\*Day:\*\* 3  

# \*\*Task:\*\* 4  

# \*\*Status:\*\* Pending verification

# 

# \## Objective

# 

# Prevent automated screening from overwriting candidate reviews that contain human decisions, corrections, or audit history.

# 

# \## Protection Rules

# 

# \- New reviews can be saved.

# \- Pending reviews without human history can be refreshed.

# \- Approved reviews cannot be overwritten by automated screening.

# \- Reviews marked Needs correction cannot be overwritten.

# \- Pending reviews with human corrections or audit history cannot be overwritten.

# \- Other candidates in the batch continue processing when a protected review is encountered.

# 

# \## Implementation

# 

# The database `save\_review()` operation performs the protection check and update in a single SQLite write transaction.

# 

# A `ProtectedReviewError` is raised when an automated save attempts to overwrite human-reviewed data.

# 

# The Streamlit dashboard catches this exception and reports protected candidates without stopping the entire batch.

# 

# \## Human Oversight

# 

# Protected reviews retain their human decision, corrections, and audit history. Re-screening does not automatically approve or reject candidates.

# 

# \## Limitations

# 

# \- The system does not store multiple automated screening versions.

# \- Protected reviews require a separate human-controlled process to incorporate new evidence.

# \- The database is not encrypted and has no user authentication.

# \- Direct manual database edits can bypass application safeguards.

# \- Updating job requirements for an existing job ID can make stored reviews inconsistent with the new job definition; job versioning is a future improvement.

# 

# \## Verification

# 

# ```cmd

# python -m pytest tests/test\_review\_protection.py -v

# python -m pytest tests -q

# ```

# 

# Expected: 98 passing tests.

# 

# \## Acceptance Criteria

# 

# \- \[ ] New reviews save successfully

# \- \[ ] Unreviewed Pending reviews can refresh

# \- \[ ] Approved reviews are protected

# \- \[ ] Needs correction reviews are protected

# \- \[ ] Pending reviews with human history are protected

# \- \[ ] Other batch candidates continue saving

# \- \[ ] Audit history remains unchanged

# \- \[ ] Dashboard displays protection warnings

# \- \[ ] All 98 automated tests pass

