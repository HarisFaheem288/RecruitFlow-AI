
import unittest

from src.schemas import (
    JobDescription,
    Candidate,
    CandidateReview,
    ReviewStatus,
    ExperienceStatus,
    ApprovalStatus,
)

from src.validators import (
    validate_job_candidate,
    validate_review,
)


class TestRecruitFlowSchemas(unittest.TestCase):

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
            preferred_skills=["Git", "Docker"],
            min_experience_years=1.0,
        )

        self.candidate = Candidate(
            candidate_id="C02",
            skills=[
                "Python",
                "Machine Learning",
                "Scikit-learn",
                "Pandas",
                "Git",
            ],
            experience_years=1.5,
            experience_evidence="Experience: 1.5 years",
            project_evidence=(
                "Built predictive analytics pipelines"
            ),
        )

    def make_review(self):
        return CandidateReview(
            candidate_id="C02",
            job_id="JOB001",
            matched_skills=[
                "Python",
                "Machine Learning",
                "Scikit-learn",
                "Pandas",
            ],
            missing_required_skills=["SQL"],
            experience_status=ExperienceStatus.MEETS,
            review_status=ReviewStatus.MISSING,
            evidence_notes="SQL is not evidenced in the resume.",
        )

    def test_valid_job(self):
        self.assertEqual(
            self.job.min_experience_years, 1.0
        )

    def test_valid_candidate(self):
        self.assertTrue(
            validate_job_candidate(
                self.job, self.candidate
            )
        )

    def test_duplicate_skills_removed(self):
        candidate = Candidate(
            candidate_id="C01",
            skills=["Python", "python", "SQL"],
        )
        self.assertEqual(
            candidate.skills, ["Python", "SQL"]
        )

    def test_negative_experience_rejected(self):
        with self.assertRaises(ValueError):
            Candidate(
                candidate_id="C03",
                skills=["Python"],
                experience_years=-1,
            )

    def test_empty_candidate_id_rejected(self):
        with self.assertRaises(ValueError):
            Candidate(
                candidate_id="",
                skills=["Python"],
            )

    def test_missing_required_skills_rejected(self):
        with self.assertRaises(ValueError):
            JobDescription(
                job_id="JOB002",
                title="Engineer",
                required_skills=[],
            )

    def test_valid_review(self):
        review = self.make_review()
        self.assertTrue(
            validate_review(
                review, self.job, self.candidate
            )
        )

    def test_review_defaults_pending(self):
        review = self.make_review()
        self.assertEqual(
            review.approval_status,
            ApprovalStatus.PENDING,
        )

    def test_skill_overlap_rejected(self):
        with self.assertRaises(ValueError):
            CandidateReview(
                candidate_id="C02",
                job_id="JOB001",
                matched_skills=["Python", "SQL"],
                missing_required_skills=["SQL"],
                experience_status="Meets",
                review_status="Missing requirements",
                evidence_notes="Contradictory skills.",
            )

    def test_incomplete_review_rejected(self):
        review = self.make_review()
        review.missing_required_skills = []

        with self.assertRaises(ValueError):
            validate_review(
                review, self.job, self.candidate
            )

    def test_wrong_candidate_rejected(self):
        review = self.make_review()
        review.candidate_id = "C99"

        with self.assertRaises(ValueError):
            validate_review(
                review, self.job, self.candidate
            )

    def test_json_output(self):
        review = self.make_review()
        output = review.to_json()

        self.assertIn('"candidate_id": "C02"', output)
        self.assertIn('"approval_status": "Pending"', output)


if __name__ == "__main__":
    unittest.main()
