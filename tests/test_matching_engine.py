
import unittest
from pathlib import Path

from src.schemas import (
    JobDescription,
    ExperienceStatus,
    ReviewStatus,
    ApprovalStatus,
)
from src.matching_engine import (
    contains_skill,
    extract_experience_claims,
    evaluate_experience,
    screen_candidate,
)
from src.document_parser import extract_from_path


class TestMatchingEngine(unittest.TestCase):

    def setUp(self):
        self.job = JobDescription(
            job_id="JOB001",
            title="Junior AI/ML Engineer",
            required_skills=[
                "Python",
                "Machine Learning",
                "Scikit-learn",
                "Pandas",
                "SQL",
            ],
            min_experience_years=1.0,
        )

    def test_python_skill(self):
        self.assertTrue(
            contains_skill("Experienced in Python", "Python")
        )

    def test_sql_not_nosql(self):
        self.assertFalse(
            contains_skill("Worked with NoSQL", "SQL")
        )

    def test_git_not_github(self):
        self.assertFalse(
            contains_skill("GitHub profile", "Git")
        )

    def test_scikit_alias(self):
        self.assertTrue(
            contains_skill("Used sklearn", "Scikit-learn")
        )

    def test_ml_alias(self):
        self.assertTrue(
            contains_skill("Built ML models", "Machine Learning")
        )

    def test_year_extraction(self):
        self.assertEqual(
            extract_experience_claims("2 years experience"),
            [2.0],
        )

    def test_month_extraction(self):
        claims = extract_experience_claims(
            "6 months internship"
        )
        self.assertAlmostEqual(claims[0], 0.5)

    def test_unknown_experience(self):
        status, years, warnings = evaluate_experience(
            "Python and SQL skills",
            1.0,
        )
        self.assertEqual(
            status, ExperienceStatus.UNKNOWN
        )
        self.assertIsNone(years)
        self.assertTrue(warnings)

    def test_insufficient_experience(self):
        status, years, _ = evaluate_experience(
            "3 months internship",
            1.0,
        )
        self.assertEqual(
            status, ExperienceStatus.BELOW
        )

    def test_conflicting_experience(self):
        status, years, warnings = evaluate_experience(
            "3 years experience. 6 months internship.",
            1.0,
        )
        self.assertEqual(
            status, ExperienceStatus.CONFLICTING
        )
        self.assertIsNone(years)
        self.assertTrue(warnings)

    def test_full_match(self):
        text = (
            "Python, Machine Learning, Scikit-learn, "
            "Pandas, SQL. 2 years experience."
        )

        review = screen_candidate(
            self.job, "C01", text
        )

        self.assertEqual(
            review.review_status,
            ReviewStatus.MEETS,
        )
        self.assertEqual(
            review.missing_required_skills, []
        )

    def test_missing_sql(self):
        text = (
            "Python, Machine Learning, Scikit-learn, "
            "Pandas. 1.5 years experience."
        )

        review = screen_candidate(
            self.job, "C02", text
        )

        self.assertIn(
            "SQL", review.missing_required_skills
        )
        self.assertEqual(
            review.review_status,
            ReviewStatus.MISSING,
        )

    def test_unknown_experience_needs_clarification(self):
        text = (
            "Python, Machine Learning, Scikit-learn, "
            "Pandas, SQL."
        )

        review = screen_candidate(
            self.job, "C06", text
        )

        self.assertEqual(
            review.review_status,
            ReviewStatus.CLARIFY,
        )

    def test_approval_remains_pending(self):
        text = (
            "Python, Machine Learning, Scikit-learn, "
            "Pandas, SQL. 2 years experience."
        )

        review = screen_candidate(
            self.job, "C01", text
        )

        self.assertEqual(
            review.approval_status,
            ApprovalStatus.PENDING,
        )

    def test_real_candidate_01(self):
        path = Path("data/resumes/candidate_01.txt")

        self.assertTrue(path.is_file())

        result = extract_from_path(path)

        review = screen_candidate(
            self.job,
            "C01",
            result.text,
        )

        self.assertEqual(review.candidate_id, "C01")
        self.assertEqual(review.job_id, "JOB001")
        self.assertTrue(review.evidence_notes)


if __name__ == "__main__":
    unittest.main()
