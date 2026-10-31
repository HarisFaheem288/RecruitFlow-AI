# \# RecruitFlow AI — Data Flow Documentation

# 

# \## 1. Input Sources

# 

# \### Job Description

# 

# Contains:

# \- Job title

# \- Required skills

# \- Preferred skills

# \- Minimum experience

# \- Responsibilities

# 

# \### Candidate Resume

# 

# Contains:

# \- Candidate identifier

# \- Skills

# \- Work experience

# \- Projects

# \- Other relevant qualification evidence

# 

# \## 2. Processing Stages

# 

# \### Stage A — Input Validation

# 

# Validate:

# \- Supported file format

# \- Nonempty file

# \- Maximum upload size

# \- Basic readability

# 

# \### Stage B — Text Extraction

# 

# Convert TXT, PDF, or DOCX content into normalized text.

# 

# \### Stage C — Requirement Extraction

# 

# Create structured job requirements from the job description.

# 

# \### Stage D — Candidate Evidence Extraction

# 

# Identify explicit skill evidence, experience information, and incomplete or conflicting claims.

# 

# \### Stage E — Matching

# 

# Compare candidate evidence against each required qualification.

# 

# For each requirement, return:

# \- Matched

# \- Not evidenced

# \- Uncertain

# 

# \### Stage F — Review Generation

# 

# Create a structured review containing:

# \- Candidate ID

# \- Job ID

# \- Matched skills

# \- Missing required skills

# \- Experience status

# \- Evidence notes

# \- Warnings

# \- Draft review status

# 

# \### Stage G — Human Review

# 

# The recruiter:

# \- Reads the generated assessment

# \- Corrects errors

# \- Requests clarification if needed

# \- Approves the final review

# 

# \### Stage H — Storage and Export

# 

# Store the approved review and associated corrections in SQLite.

# 

# Generate CSV or JSON output.

# 

# \## 3. Example Input

# 

# Job:

# Junior AI/ML Engineer

# 

# Required skills:

# Python, Machine Learning, Scikit-learn, Pandas, SQL

# 

# Minimum experience:

# 1 year

# 

# Candidate:

# C02

# 

# Experience:

# 1.5 years

# 

# Skills:

# Python, Machine Learning, Scikit-learn, Pandas, Git

# 

# \## 4. Example Expected Output

# 

# Candidate ID: C02

# 

# Matched required skills:

# Python, Machine Learning, Scikit-learn, Pandas

# 

# Missing evidence:

# SQL

# 

# Experience status:

# Meets

# 

# Review status:

# Missing requirements

# 

# Approval status:

# Pending

# 

# Note:

# SQL was not explicitly mentioned in the resume. This does not prove that the candidate lacks SQL knowledge.

# 

# \## 5. Exception Handling

# 

# Unreadable files do not proceed to normal review generation.

# 

# Missing or contradictory information is flagged rather than fabricated.

# 

# An unapproved review remains a draft.

# 

# \## 6. Audit Trail

# 

# The system will record:

# \- Review identifier

# \- Candidate identifier

# \- Processing timestamp

# \- Generated assessment

# \- Human corrections

# \- Approval status

# \- Approval timestamp, when applicable

# \- Error details, when processing fails

# 

# \## 7. Data Flow Boundary

# 

# Raw document contents remain within the local application during MVP processing.

# 

# External API transmission is not part of the Day 5 scope.



