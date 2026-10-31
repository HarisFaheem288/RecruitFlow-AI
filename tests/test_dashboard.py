
import unittest

from app import (
    split_skills,
    candidate_id_from_filename,
    build_job,
    results_dataframe,
)


class TestDashboard(unittest.TestCase):

    def test_split_skills(self):
        result = split_skills(
            "Python, SQL, python, Pandas"
        )

        self.assertEqual(
            result,
            ["Python", "SQL", "Pandas"],
        )

    def test_candidate_id(self):
        self.assertEqual(
            candidate_id_from_filename(
                "candidate_07.txt"
            ),
            "C07",
        )

    def test_build_job(self):
        job = build_job(
            "JOB001",
            "AI Engineer",
            "Python, SQL",
            "Docker",
            1.0,
        )

        self.assertEqual(job.job_id, "JOB001")
        self.assertEqual(
            job.required_skills,
            ["Python", "SQL"],
        )

    def test_empty_results_dataframe(self):
        frame = results_dataframe([])

        self.assertEqual(len(frame), 0)


if __name__ == "__main__":
    unittest.main()
