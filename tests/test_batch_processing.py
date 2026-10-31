import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.schemas import JobDescription
from src.review_generator import (
    candidate_id_from_path,
    generate_review,
    process_batch,
)
from src.reporting import export_all


FULL_RESUME = (
    "Skills: Python, Machine Learning, "
    "Scikit-learn, Pandas, SQL.\n"
    "Experience: 2 years."
)

MISSING_SQL_RESUME = (
    "Skills: Python, Machine Learning, "
    "Scikit-learn, Pandas.\n"
    "Experience: 1.5 years."
)


class TestBatchProcessing(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.resume_dir = self.root / "resumes"
        self.resume_dir.mkdir()

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

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_resume(self, name, text):
        path = self.resume_dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_candidate_id(self):
        result = candidate_id_from_path(
            Path("candidate_07.txt")
        )
        self.assertEqual(result, "C07")

    def test_other_candidate_id(self):
        result = candidate_id_from_path(
            Path("john_resume.pdf")
        )
        self.assertEqual(result, "JOHN_RESUME")

    def test_single_review(self):
        path = self.write_resume(
            "candidate_01.txt",
            FULL_RESUME,
        )

        item = generate_review(path, self.job)

        self.assertEqual(
            item["review"]["candidate_id"], "C01"
        )
        self.assertEqual(
            item["review"]["review_status"],
            "Meets requirements",
        )

    def test_document_metadata(self):
        path = self.write_resume(
            "candidate_01.txt",
            FULL_RESUME,
        )

        item = generate_review(path, self.job)

        self.assertEqual(
            item["document"]["file_type"], "TXT"
        )
        self.assertGreater(
            item["document"]["character_count"], 0
        )

    def test_two_resumes(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )
        self.write_resume(
            "candidate_02.txt", MISSING_SQL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        self.assertEqual(batch.total, 2)
        self.assertEqual(batch.successful, 2)
        self.assertEqual(batch.failed, 0)

    def test_missing_skill_in_batch(self):
        self.write_resume(
            "candidate_02.txt", MISSING_SQL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        review = batch.reviews[0]["review"]

        self.assertIn(
            "SQL",
            review["missing_required_skills"],
        )

    def test_invalid_file_does_not_stop_batch(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )
        (self.resume_dir / "bad.pdf").write_bytes(
            b"not a pdf"
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        self.assertEqual(batch.total, 2)
        self.assertEqual(batch.successful, 1)
        self.assertEqual(batch.failed, 1)

    def test_unsupported_files_ignored(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )
        self.write_resume(
            "notes.csv", "Not a resume"
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        self.assertEqual(batch.total, 1)

    def test_empty_folder_rejected(self):
        with self.assertRaises(ValueError):
            process_batch(self.resume_dir, self.job)

    def test_missing_folder_rejected(self):
        with self.assertRaises(ValueError):
            process_batch(
                self.root / "missing",
                self.job,
            )

    def test_duplicate_candidate_id(self):
        from docx import Document

        # First resume: valid TXT
        self.write_resume(
            "candidate_01.txt",
            FULL_RESUME
        )

        # Second resume: valid DOCX with same candidate ID
        document = Document()
        document.add_paragraph(FULL_RESUME)
        document.save(
            self.resume_dir / "candidate_01.docx"
        )

        # Process both resumes
        batch = process_batch(
            self.resume_dir,
            self.job
        )

        # One candidate should be processed
        # and the duplicate should be rejected.
        self.assertEqual(batch.total, 2)
        self.assertEqual(batch.successful, 1)
        self.assertEqual(batch.failed, 1)

        self.assertIn(
            "Duplicate candidate ID",
            batch.errors[0]["error"]
        )

    def test_all_approvals_pending(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )
        self.write_resume(
            "candidate_02.txt", MISSING_SQL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        for item in batch.reviews:
            self.assertEqual(
                item["review"]["approval_status"],
                "Pending",
            )

    def test_summary_counts(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )
        self.write_resume(
            "candidate_02.txt", MISSING_SQL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        counts = batch.summary()[
            "review_status_counts"
        ]

        self.assertEqual(
            counts["Meets requirements"], 1
        )
        self.assertEqual(
            counts["Missing requirements"], 1
        )

    def test_export_files_created(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        paths = export_all(
            batch, self.root / "outputs"
        )

        self.assertEqual(len(paths), 3)

        for path in paths.values():
            self.assertTrue(path.is_file())

    def test_json_export_content(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        paths = export_all(
            batch, self.root / "outputs"
        )

        data = json.loads(
            paths["json"].read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            data["summary"]["successful"], 1
        )
        self.assertEqual(
            data["reviews"][0]["review"][
                "candidate_id"
            ],
            "C01",
        )

    def test_csv_export_content(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        paths = export_all(
            batch, self.root / "outputs"
        )

        with paths["csv"].open(
            newline="",
            encoding="utf-8-sig",
        ) as file:
            rows = list(csv.DictReader(file))

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["candidate_id"], "C01"
        )
        self.assertEqual(
            rows[0]["approval_status"], "Pending"
        )

    def test_markdown_export_content(self):
        self.write_resume(
            "candidate_01.txt", FULL_RESUME
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        paths = export_all(
            batch, self.root / "outputs"
        )

        content = paths["markdown"].read_text(
            encoding="utf-8"
        )

        self.assertIn("RecruitFlow AI", content)
        self.assertIn("C01", content)
        self.assertIn("human", content.lower())

    def test_error_in_json_report(self):
        (self.resume_dir / "bad.pdf").write_bytes(
            b"invalid PDF"
        )

        batch = process_batch(
            self.resume_dir, self.job
        )

        paths = export_all(
            batch, self.root / "outputs"
        )

        data = json.loads(
            paths["json"].read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            data["summary"]["failed"], 1
        )
        self.assertEqual(
            len(data["errors"]), 1
        )

    def test_real_synthetic_batch(self):
        project_folder = (
            Path(__file__).resolve().parents[1]
            / "data"
            / "resumes"
        )

        batch = process_batch(
            project_folder, self.job
        )

        self.assertEqual(batch.total, 10)
        self.assertEqual(batch.successful, 10)
        self.assertEqual(batch.failed, 0)


if __name__ == "__main__":
    unittest.main()