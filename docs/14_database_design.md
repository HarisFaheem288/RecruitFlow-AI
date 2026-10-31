# \# RecruitFlow AI — SQLite Database Design

# 

# \## Objective

# 

# Persist job requirements and structured candidate screening reviews so results can be retrieved and inspected in later workflow stages.

# 

# \## Database

# 

# \- Engine: SQLite

# \- Location: `data/recruitflow.db`

# \- Python module: `src/database.py`

# 

# \## Tables

# 

# \### jobs

# 

# Stores job identifiers, titles, required skills, preferred skills, and minimum experience requirements.

# 

# Primary key: `job\_id`.

# 

# \### reviews

# 

# Stores candidate and job identifiers, matched skills, missing required skills, experience status, review status, evidence notes, warnings, approval status, human corrections, and processing timestamp.

# 

# Composite primary key: `(candidate\_id, job\_id)`.

# 

# Foreign key: `reviews.job\_id` references `jobs.job\_id`.

# 

# \## Database Operations

# 

# \- Initialize database tables

# \- Save or update a job

# \- Save or update a candidate review

# \- Retrieve an individual review

# \- List reviews by job

# 

# \## Data Integrity

# 

# \- Parameterized SQL statements

# \- Foreign key enforcement

# \- Unique review per candidate and job

# \- Structured lists serialized as JSON

# \- Pending approval status preserved from the review model

# 

# \## Limitations

# 

# \- No database encryption

# \- No access-control or user authentication

# \- No audit history of changes

# \- No recruiter approval interface

# \- Updating a review overwrites the previous stored version

# 

# \## Verification

# 

# ```cmd

# python test\_database.py

# python -m pytest tests/test\_database.py -v

# python -m pytest tests -q

# ```

# 

# \## Acceptance Criteria

# 

# \- SQLite database is created successfully.

# \- Ten synthetic candidate reviews can be stored.

# \- Stored reviews can be retrieved.

# \- Duplicate saves do not create duplicate records.

# \- Foreign key relationships are enforced.

# \- All generated reviews remain Pending.

# \- All automated tests pass.

