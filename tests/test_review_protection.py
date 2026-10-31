
import tempfile
import unittest
from pathlib import Path

from src.database import (
    ProtectedReviewError,
    get_review,
    get_review_audit,
    initialize_database,
    save_job,
    save_review,
    update_human_review,
)
from src.matching_engine import screen_candidate
from src.schemas import JobDescription


class TestReviewProtection(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = (
            Path(self.temp.name) / "protection.db"
        )

        self.job = JobDescription(
            job_id="JOB001",
            title="Junior AI/ML Engineer",
            required_skills=["Python", "SQL"],
            min_experience_years=1.0,
        )

        initialize_database(self.db_path)
        save_job(self.job, self.db_path)

        self.original = screen_candidate(
            self.job,
            "C01",
            "Python, SQL. 2 years experience.",
        )

        self.rescreened = screen_candidate(
            self.job,
            "C01",
            "Python. 6 months experience.",
        )

    def tearDown(self):
        self.temp.cleanup()

    def human_review(
        self,
        approval_status="Approved",
        review_status="Meets requirements",
        experience_status="Meets",
    ):
        return update_human_review(
            candidate_id="C01",
            job_id="JOB001",
            reviewer="Test Recruiter",
            review_status=review_status,
            experience_status=experience_status,
            matched_skills=["Python", "SQL"],
            missing_required_skills=[],
            evidence_notes="Evidence manually verified.",
            approval_status=approval_status,
            correction_reason="Verified by recruiter.",
            db_path=self.db_path,
        )

    def test_new_review_can_be_saved(self):
        save_review(self.original, self.db_path)

        result = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertIsNotNone(result)

    def test_pending_unreviewed_can_be_refreshed(self):
        save_review(self.original, self.db_path)
        save_review(self.rescreened, self.db_path)

        result = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            result["missing_required_skills"],
            ["SQL"],
        )

    def test_approved_review_is_protected(self):
        save_review(self.original, self.db_path)
        self.human_review()

        with self.assertRaises(ProtectedReviewError):
            save_review(
                self.rescreened, self.db_path
            )

        result = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            result["approval_status"],
            "Approved",
        )

    def test_needs_correction_is_protected(self):
        save_review(self.original, self.db_path)

        self.human_review(
            approval_status="Needs correction"
        )

        with self.assertRaises(ProtectedReviewError):
            save_review(
                self.rescreened, self.db_path
            )

    def test_pending_with_history_is_protected(self):
        save_review(self.original, self.db_path)
        self.human_review(
            approval_status="Pending"
        )

        with self.assertRaises(ProtectedReviewError):
            save_review(
                self.rescreened, self.db_path
            )

    def test_original_skills_preserved(self):
        save_review(self.original, self.db_path)
        self.human_review()

        try:
            save_review(
                self.rescreened, self.db_path
            )
        except ProtectedReviewError:
            pass

        result = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            result["matched_skills"],
            ["Python", "SQL"],
        )

    def test_audit_preserved_after_block(self):
        save_review(self.original, self.db_path)
        self.human_review()

        try:
            save_review(
                self.rescreened, self.db_path
            )
        except ProtectedReviewError:
            pass

        history = get_review_audit(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(len(history), 1)

    def test_other_candidate_can_still_save(self):
        save_review(self.original, self.db_path)
        self.human_review()

        another = screen_candidate(
            self.job,
            "C02",
            "Python, SQL. 3 years experience.",
        )

        save_review(another, self.db_path)

        result = get_review(
            "C02", "JOB001", self.db_path
        )

        self.assertIsNotNone(result)

    def test_nonpending_automated_review_rejected(self):
        self.original.approval_status = "Approved"

        with self.assertRaises(ValueError):
            save_review(
                self.original, self.db_path
            )

    def test_human_corrections_in_automated_review_rejected(self):
        self.original.human_corrections = [
            {"reason": "Manual correction"}
        ]

        with self.assertRaises(ValueError):
            save_review(
                self.original, self.db_path
            )


if __name__ == "__main__":
    unittest.main()
