# \# RecruitFlow AI — Data Contracts

# 

# \## Purpose

# 

# Define the structured input and output formats for the recruitment screening workflow.

# 

# \## JobDescription

# 

# Required fields:

# \- job\_id: nonempty string

# \- title: nonempty string

# \- required\_skills: nonempty list of strings

# 

# Optional fields:

# \- preferred\_skills: list of strings

# \- min\_experience\_years: nonnegative number, default 0

# 

# \## Candidate

# 

# Required fields:

# \- candidate\_id: nonempty string

# \- skills: list of strings

# 

# Optional fields:

# \- experience\_years: nonnegative number or null

# \- experience\_evidence: string

# \- project\_evidence: string

# \- warnings: list of strings

# 

# Unknown experience is represented by null, not zero.

# 

# \## CandidateReview

# 

# Required fields:

# \- candidate\_id

# \- job\_id

# \- matched\_skills

# \- missing\_required\_skills

# \- experience\_status

# \- review\_status

# \- evidence\_notes

# \- warnings

# \- approval\_status

# \- human\_corrections

# \- processing\_timestamp

# 

# \## Review Status Values

# 

# \- Meets requirements

# \- Missing requirements

# \- Needs clarification

# 

# \## Experience Status Values

# 

# \- Meets

# \- Below minimum

# \- Unknown

# \- Conflicting

# \- Needs review

# 

# \## Approval Status Values

# 

# \- Pending

# \- Approved

# \- Needs correction

# 

# \## Validation Rules

# 

# \- IDs cannot be empty.

# \- Skill names must be nonempty.

# \- Duplicate skills are removed case-insensitively.

# \- Experience must be finite and nonnegative.

# \- Matched and missing skill lists cannot overlap.

# \- Every required skill must be accounted for.

# \- New generated reviews must remain Pending.

# \- A review must reference the correct job and candidate.

# \- Evidence notes cannot be empty.

# 

# \## Current Limitations

# 

# \- Skills are represented as explicit strings.

# \- Synonym and semantic matching are not implemented.

# \- The initial validation contract does not independently verify the truth of extracted evidence.

# \- Human approval workflow is not implemented yet.

# \- Document extraction and the matching engine will be implemented in subsequent tasks.



