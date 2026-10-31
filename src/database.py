"""
RecruitFlow AI - SQLite Database
Stores job descriptions and structured draft reviews.
"""

import json
import sqlite3
from pathlib import Path
from contextlib import contextmanager

from .schemas import JobDescription, CandidateReview


DEFAULT_DB = Path("data/recruitflow.db")
class ProtectedReviewError(ValueError):
    """Raised when screening would overwrite human-reviewed data."""
    pass

@contextmanager
def connect_db(db_path=DEFAULT_DB):
    """
    Open a SQLite connection and always close it.

    Commit successful operations and roll back failures.
    """
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def initialize_database(db_path=DEFAULT_DB):
    with connect_db(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                required_skills TEXT NOT NULL,
                preferred_skills TEXT NOT NULL,
                min_experience_years REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reviews (
                candidate_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_required_skills TEXT NOT NULL,
                experience_status TEXT NOT NULL,
                review_status TEXT NOT NULL,
                evidence_notes TEXT NOT NULL,
                warnings TEXT NOT NULL,
                approval_status TEXT NOT NULL,
                human_corrections TEXT NOT NULL,
                processing_timestamp TEXT NOT NULL,
                PRIMARY KEY (candidate_id, job_id),
                FOREIGN KEY (job_id)
                    REFERENCES jobs(job_id)
            );
        """)


def save_job(job, db_path=DEFAULT_DB):
    if not isinstance(job, JobDescription):
        raise TypeError("Expected JobDescription")

    initialize_database(db_path)

    with connect_db(db_path) as conn:
        conn.execute("""
            INSERT INTO jobs (
                job_id, title, required_skills,
                preferred_skills, min_experience_years
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                title = excluded.title,
                required_skills = excluded.required_skills,
                preferred_skills = excluded.preferred_skills,
                min_experience_years =
                    excluded.min_experience_years
        """, (
            job.job_id,
            job.title,
            json.dumps(job.required_skills),
            json.dumps(job.preferred_skills),
            job.min_experience_years,
        ))



def save_review(review, db_path=DEFAULT_DB):
    """
    Save an automated screening review safely.

    New reviews are inserted.
    Unreviewed Pending reviews can be refreshed.
    Human-reviewed reviews cannot be overwritten.
    """
    if not isinstance(review, CandidateReview):
        raise TypeError("Expected CandidateReview")

    initialize_database(db_path)
    data = review.to_dict()

    # This function is for fresh automated reviews only.
    if data["approval_status"] != "Pending":
        raise ValueError(
            "Automated screening must have Pending approval."
        )

    if data["human_corrections"]:
        raise ValueError(
            "Automated screening cannot contain human corrections."
        )

    with connect_db(db_path) as conn:
        # The check and write happen in one transaction.
        # BEGIN IMMEDIATE prevents concurrent writers from
        # changing the review between these operations.
        conn.execute("BEGIN IMMEDIATE")

        existing = conn.execute("""
            SELECT approval_status, human_corrections
            FROM reviews
            WHERE candidate_id = ? AND job_id = ?
        """, (
            data["candidate_id"],
            data["job_id"],
        )).fetchone()

        if existing is not None:
            corrections = json.loads(
                existing["human_corrections"]
            )

            audit_exists = False

            # Audit table may not exist in older databases.
            audit_table = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type = 'table'
                  AND name = 'review_audit'
            """).fetchone()

            if audit_table is not None:
                audit_exists = conn.execute("""
                    SELECT 1
                    FROM review_audit
                    WHERE candidate_id = ?
                      AND job_id = ?
                    LIMIT 1
                """, (
                    data["candidate_id"],
                    data["job_id"],
                )).fetchone() is not None

            if (
                existing["approval_status"] != "Pending"
                or corrections
                or audit_exists
            ):
                raise ProtectedReviewError(
                    "Candidate "
                    f"{data['candidate_id']} for "
                    f"{data['job_id']} has human review "
                    "history and cannot be overwritten."
                )

        conn.execute("""
            INSERT INTO reviews (
                candidate_id, job_id, matched_skills,
                missing_required_skills, experience_status,
                review_status, evidence_notes, warnings,
                approval_status, human_corrections,
                processing_timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(candidate_id, job_id) DO UPDATE SET
                matched_skills = excluded.matched_skills,
                missing_required_skills =
                    excluded.missing_required_skills,
                experience_status =
                    excluded.experience_status,
                review_status = excluded.review_status,
                evidence_notes = excluded.evidence_notes,
                warnings = excluded.warnings,
                approval_status = excluded.approval_status,
                human_corrections =
                    excluded.human_corrections,
                processing_timestamp =
                    excluded.processing_timestamp
        """, (
            data["candidate_id"],
            data["job_id"],
            json.dumps(data["matched_skills"]),
            json.dumps(data["missing_required_skills"]),
            data["experience_status"],
            data["review_status"],
            data["evidence_notes"],
            json.dumps(data["warnings"]),
            data["approval_status"],
            json.dumps(data["human_corrections"]),
            data["processing_timestamp"],
        ))


def get_review(candidate_id, job_id, db_path=DEFAULT_DB):
    initialize_database(db_path)

    with connect_db(db_path) as conn:
        row = conn.execute("""
            SELECT * FROM reviews
            WHERE candidate_id = ? AND job_id = ?
        """, (candidate_id, job_id)).fetchone()

    if row is None:
        return None

    result = dict(row)

    for key in (
        "matched_skills",
        "missing_required_skills",
        "warnings",
        "human_corrections",
    ):
        result[key] = json.loads(result[key])

    return result


def list_reviews(job_id=None, db_path=DEFAULT_DB):
    initialize_database(db_path)

    with connect_db(db_path) as conn:
        if job_id is None:
            rows = conn.execute("""
                SELECT candidate_id, job_id,
                       review_status, experience_status,
                       approval_status, processing_timestamp
                FROM reviews
                ORDER BY job_id, candidate_id
            """).fetchall()
        else:
            rows = conn.execute("""
                SELECT candidate_id, job_id,
                       review_status, experience_status,
                       approval_status, processing_timestamp
                FROM reviews
                WHERE job_id = ?
                ORDER BY candidate_id
            """, (job_id,)).fetchall()

    return [dict(row) for row in rows]

def initialize_review_audit(db_path=DEFAULT_DB):
    """Create an append-only history of human review changes."""
    initialize_database(db_path)

    with connect_db(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS review_audit (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id TEXT NOT NULL,
                job_id TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                action TEXT NOT NULL,
                previous_review TEXT NOT NULL,
                updated_review TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (job_id)
                    REFERENCES jobs(job_id)
            )
        """)


def update_human_review(
    candidate_id,
    job_id,
    reviewer,
    review_status,
    experience_status,
    matched_skills,
    missing_required_skills,
    evidence_notes,
    approval_status,
    correction_reason,
    db_path=DEFAULT_DB,
):
    """
    Apply an explicit human correction or approval.

    Changes and audit entries are committed together.
    """
    from datetime import datetime, timezone

    from .schemas import (
        ApprovalStatus,
        ExperienceStatus,
        ReviewStatus,
        clean_skills,
    )

    reviewer = reviewer.strip()
    correction_reason = correction_reason.strip()
    evidence_notes = evidence_notes.strip()

    if not reviewer:
        raise ValueError("Reviewer name is required.")

    if not correction_reason:
        raise ValueError(
            "A review reason or verification note is required."
        )

    if not evidence_notes:
        raise ValueError("Evidence notes cannot be empty.")

    valid_reviews = {
        item.value for item in ReviewStatus
    }
    valid_experience = {
        item.value for item in ExperienceStatus
    }
    valid_approvals = {
        item.value for item in ApprovalStatus
    }

    if review_status not in valid_reviews:
        raise ValueError("Invalid review status.")

    if experience_status not in valid_experience:
        raise ValueError("Invalid experience status.")

    if approval_status not in valid_approvals:
        raise ValueError("Invalid approval status.")

    matched_skills = clean_skills(matched_skills)
    missing_required_skills = clean_skills(
        missing_required_skills
    )

    overlap = {
        skill.casefold() for skill in matched_skills
    } & {
        skill.casefold()
        for skill in missing_required_skills
    }

    if overlap:
        raise ValueError(
            "A skill cannot be both matched and missing."
        )

    if (
        approval_status == ApprovalStatus.APPROVED.value
        and review_status
        == ReviewStatus.CLARIFY.value
    ):
        raise ValueError(
            "Resolve clarification before approving."
        )

    if (
        approval_status == ApprovalStatus.APPROVED.value
        and experience_status in {
            ExperienceStatus.UNKNOWN.value,
            ExperienceStatus.CONFLICTING.value,
            ExperienceStatus.NEEDS_REVIEW.value,
        }
    ):
        raise ValueError(
            "Resolve experience uncertainty before approving."
        )

    initialize_review_audit(db_path)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    with connect_db(db_path) as conn:
        row = conn.execute("""
            SELECT * FROM reviews
            WHERE candidate_id = ? AND job_id = ?
        """, (candidate_id, job_id)).fetchone()

        if row is None:
            raise ValueError("Saved review not found.")

        previous = dict(row)

        corrections = json.loads(
            previous["human_corrections"]
        )

        corrections.append({
            "reviewer": reviewer,
            "reason": correction_reason,
            "approval_status": approval_status,
            "timestamp": timestamp,
        })

        updated = dict(previous)

        updated.update({
            "matched_skills": json.dumps(
                matched_skills
            ),
            "missing_required_skills": json.dumps(
                missing_required_skills
            ),
            "experience_status": experience_status,
            "review_status": review_status,
            "evidence_notes": evidence_notes,
            "approval_status": approval_status,
            "human_corrections": json.dumps(
                corrections
            ),
        })

        conn.execute("""
            UPDATE reviews SET
                matched_skills = ?,
                missing_required_skills = ?,
                experience_status = ?,
                review_status = ?,
                evidence_notes = ?,
                approval_status = ?,
                human_corrections = ?
            WHERE candidate_id = ? AND job_id = ?
        """, (
            updated["matched_skills"],
            updated["missing_required_skills"],
            updated["experience_status"],
            updated["review_status"],
            updated["evidence_notes"],
            updated["approval_status"],
            updated["human_corrections"],
            candidate_id,
            job_id,
        ))

        conn.execute("""
            INSERT INTO review_audit (
                candidate_id, job_id, reviewer,
                action, previous_review,
                updated_review, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            candidate_id,
            job_id,
            reviewer,
            approval_status,
            json.dumps(previous),
            json.dumps(updated),
            timestamp,
        ))

    return get_review(
        candidate_id, job_id, db_path
    )


def get_review_audit(
    candidate_id,
    job_id,
    db_path=DEFAULT_DB,
):
    initialize_review_audit(db_path)

    with connect_db(db_path) as conn:
        rows = conn.execute("""
            SELECT audit_id, reviewer, action,
                   previous_review, updated_review,
                   created_at
            FROM review_audit
            WHERE candidate_id = ? AND job_id = ?
            ORDER BY audit_id DESC
        """, (candidate_id, job_id)).fetchall()

    result = []

    for row in rows:
        item = dict(row)
        item["previous_review"] = json.loads(
            item["previous_review"]
        )
        item["updated_review"] = json.loads(
            item["updated_review"]
        )
        result.append(item)

    return result
