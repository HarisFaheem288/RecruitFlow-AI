# \# RecruitFlow AI — Initial Skill-Matching Engine

# 

# \## Objective

# 

# Generate evidence-based draft candidate reviews by comparing extracted resume text with predefined job requirements.

# 

# \## Technology

# 

# \- Python

# \- Regular expressions

# \- Explicit skill aliases

# \- Existing RecruitFlow AI schemas and validators

# 

# No external LLM or paid API is required.

# 

# \## Inputs

# 

# \- Validated JobDescription

# \- Candidate ID

# \- Extracted resume text

# 

# \## Outputs

# 

# A CandidateReview containing:

# 

# \- Candidate and job IDs

# \- Matched required skills

# \- Missing required skill evidence

# \- Experience status

# \- Review status

# \- Evidence notes

# \- Warnings

# \- Pending approval status

# \- Processing timestamp

# 

# \## Skill Matching

# 

# The engine uses case-insensitive phrase matching and known aliases.

# 

# For example:

# 

# \- sklearn → Scikit-learn

# \- ML → Machine Learning

# \- scikit learn → Scikit-learn

# 

# Missing evidence does not establish that a candidate lacks the skill.

# 

# \## Experience Evaluation

# 

# The engine recognizes simple numeric durations, including years and months.

# 

# Possible outcomes:

# 

# \- Meets

# \- Below minimum

# \- Unknown

# \- Conflicting

# 

# Different numeric duration claims are conservatively flagged for human review rather than added automatically.

# 

# \## Review Categories

# 

# \- Meets requirements

# \- Missing requirements

# \- Needs clarification

# 

# These categories describe evidence against job requirements and are not automatic hiring or rejection decisions.

# 

# \## Human Oversight

# 

# All generated reviews remain Pending.

# 

# A recruiter must verify evidence and explicitly approve final assessments in a later workflow.

# 

# \## Known Limitations

# 

# \- Skill mentions may be negated, hypothetical, or out of context.

# \- Alias coverage is limited.

# \- Employment date ranges are not calculated.

# \- Multiple durations may represent legitimate separate roles.

# \- Project experience and professional employment are not distinguished reliably.

# \- The initial engine does not calculate candidate rankings.

# \- Results require human verification.

# 

# \## Testing

# 

# The matching engine adds 15 automated tests covering:

# 

# \- Skill matching and aliases

# \- Substring avoidance

# \- Experience duration extraction

# \- Missing experience

# \- Conflicting duration claims

# \- Missing required skills

# \- Full required-skill matches

# \- Pending approval

# \- Processing of an existing synthetic resume

# 

# Expected total project tests: 42.

# 

# \## Current Status

# 

# Implementation is considered verified only after all automated tests pass and the ten synthetic resumes can be processed.

# 

# Classification accuracy against the reference dataset remains a separate evaluation activity.



