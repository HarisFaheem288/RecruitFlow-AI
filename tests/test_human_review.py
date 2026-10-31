
import tempfile
import unittest
from pathlib import Path

from src.database import (
    initialize_database,
    save_job,
    save_review,
    get_review,
    get_review_audit,
    update_human_review,
)
from src.matching_engine import screen_candidate
from src.schemas import JobDescription


class TestHumanReview(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = (
            Path(self.temp.name) / "review_test.db"
        )

        self.job = JobDescription(
            job_id="JOB001",
            title="Junior AI/ML Engineer",
            required_skills=["Python", "SQL"],
            min_experience_years=1.0,
        )

        self.review = screen_candidate(
            self.job,
            "C01",
            "Python and SQL. 2 years experience.",
        )

        initialize_database(self.db_path)
        save_job(self.job, self.db_path)
        save_review(self.review, self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def update(self, **overrides):
        values = {
            "candidate_id": "C01",
            "job_id": "JOB001",
            "reviewer": "Test Recruiter",
            "review_status": "Meets requirements",
            "experience_status": "Meets",
            "matched_skills": ["Python", "SQL"],
            "missing_required_skills": [],
            "evidence_notes": "Verified resume evidence.",
            "approval_status": "Approved",
            "correction_reason": "Manually checked.",
            "db_path": self.db_path,
        }

        values.update(overrides)

        return update_human_review(**values)

    def test_approval_saved(self):
        result = self.update()

        self.assertEqual(
            result["approval_status"],
            "Approved",
        )

    def test_correction_saved(self):
        result = self.update(
            approval_status="Needs correction",
            review_status="Missing requirements",
            matched_skills=["Python"],
            missing_required_skills=["SQL"],
        )

        self.assertEqual(
            result["missing_required_skills"],
            ["SQL"],
        )

    def test_audit_created(self):
        self.update()

        history = get_review_audit(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(len(history), 1)

    def test_audit_preserves_previous_status(self):
        self.update()

        history = get_review_audit(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            history[0]["previous_review"][
                "approval_status"
            ],
            "Pending",
        )

    def test_reviewer_required(self):
        with self.assertRaises(ValueError):
            self.update(reviewer="")

    def test_reason_required(self):
        with self.assertRaises(ValueError):
            self.update(correction_reason="")

    def test_invalid_approval_rejected(self):
        with self.assertRaises(ValueError):
            self.update(
                approval_status="Auto-hired"
            )

    def test_overlapping_skills_rejected(self):
        with self.assertRaises(ValueError):
            self.update(
                missing_required_skills=["Python"]
            )

    def test_clarification_cannot_be_approved(self):
        with self.assertRaises(ValueError):
            self.update(
                review_status="Needs clarification"
            )

    def test_conflicting_experience_cannot_be_approved(self):
        with self.assertRaises(ValueError):
            self.update(
                experience_status="Conflicting"
            )

    def test_failed_update_creates_no_audit(self):
        try:
            self.update(reviewer="")
        except ValueError:
            pass

        history = get_review_audit(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(history, [])

    def test_multiple_audit_entries(self):
        self.update(
            approval_status="Needs correction"
        )
        self.update()

        history = get_review_audit(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(len(history), 2)

    def test_processing_timestamp_preserved(self):
        before = get_review(
            "C01", "JOB001", self.db_path
        )

        after = self.update()

        self.assertEqual(
            before["processing_timestamp"],
            after["processing_timestamp"],
        )


if __name__ == "__main__":
    unittest.main()
