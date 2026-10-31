
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.schemas import JobDescription
from src.matching_engine import screen_candidate
from src.database import (
    initialize_database,
    save_job,
    save_review,
    get_review,
    list_reviews,
)


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "test.db"

        self.job = JobDescription(
            job_id="JOB001",
            title="Junior AI/ML Engineer",
            required_skills=["Python", "SQL"],
            min_experience_years=1.0,
        )

        self.review = screen_candidate(
            self.job,
            "C01",
            "Python, SQL. 2 years experience.",
        )

        initialize_database(self.db_path)
        save_job(self.job, self.db_path)

    def tearDown(self):
        self.temp.cleanup()

    def test_database_created(self):
        self.assertTrue(self.db_path.exists())
    
    def test_job_saved(self):
        from contextlib import closing

        with closing(sqlite3.connect(self.db_path)) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM jobs"
            ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_review_saved(self):
        save_review(self.review, self.db_path)

        saved = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertIsNotNone(saved)
        self.assertEqual(
            saved["candidate_id"], "C01"
        )

    def test_skill_lists_restored(self):
        save_review(self.review, self.db_path)

        saved = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            saved["matched_skills"],
            ["Python", "SQL"],
        )

    def test_pending_approval(self):
        save_review(self.review, self.db_path)

        saved = get_review(
            "C01", "JOB001", self.db_path
        )

        self.assertEqual(
            saved["approval_status"], "Pending"
        )

    def test_list_reviews(self):
        save_review(self.review, self.db_path)

        reviews = list_reviews(
            "JOB001", self.db_path
        )

        self.assertEqual(len(reviews), 1)

    def test_missing_review(self):
        saved = get_review(
            "UNKNOWN", "JOB001", self.db_path
        )

        self.assertIsNone(saved)

    def test_upsert_does_not_duplicate(self):
        save_review(self.review, self.db_path)
        save_review(self.review, self.db_path)

        reviews = list_reviews(
            "JOB001", self.db_path
        )

        self.assertEqual(len(reviews), 1)

    def test_foreign_key_enforced(self):
        other_job = JobDescription(
            job_id="OTHER",
            title="Other role",
            required_skills=["Python"],
        )

        other_review = screen_candidate(
            other_job,
            "C02",
            "Python. 2 years experience.",
        )

        with self.assertRaises(
            sqlite3.IntegrityError
        ):
            save_review(other_review, self.db_path)

    def test_filter_by_job(self):
        save_review(self.review, self.db_path)

        reviews = list_reviews(
            "OTHER", self.db_path
        )

        self.assertEqual(reviews, [])


if __name__ == "__main__":
    unittest.main()
