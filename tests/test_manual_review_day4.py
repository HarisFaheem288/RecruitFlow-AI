"""Day 4 manual baseline tests; no Streamlit or live recruiter input needed."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'evaluation' / 'manual_review_day4.py'
spec = importlib.util.spec_from_file_location('manual_review_day4', MODULE)
manual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manual)


def sample(candidate='C01', duration=25.5):
    return dict(candidate_id=candidate, filename='candidate_01.txt', review_status='Meets requirements',
                experience_status='Meets', matched_skills='Python', missing_required_skills='',
                evidence_notes='Python is explicitly listed.', duration_seconds=duration,
                reviewed_at_utc='2026-10-28T00:00:00+00:00')


class ManualBaselineTests(unittest.TestCase):
    def test_candidate_id(self):
        self.assertEqual(manual.candidate_id(Path('candidate_07.txt')), 'C07')

    def test_other_candidate_id(self):
        self.assertEqual(manual.candidate_id(Path('alex.txt')), 'ALEX')

    def test_valid_record(self):
        self.assertEqual(manual.validate_record(sample())['candidate_id'], 'C01')

    def test_invalid_review_status(self):
        with self.assertRaises(ValueError):
            manual.validate_record({**sample(), 'review_status': 'Hired'})

    def test_invalid_experience_status(self):
        with self.assertRaises(ValueError):
            manual.validate_record({**sample(), 'experience_status': 'Definitely'})

    def test_missing_evidence(self):
        with self.assertRaises(ValueError):
            manual.validate_record({**sample(), 'evidence_notes': '  '})

    def test_zero_duration(self):
        with self.assertRaises(ValueError):
            manual.validate_record({**sample(), 'duration_seconds': 0})

    def test_csv_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'baseline.csv'
            manual.save_records([sample()], path)
            self.assertEqual(manual.read_records(path)[0]['candidate_id'], 'C01')

    def test_duplicate_id_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'baseline.csv'
            manual.save_records([sample(), sample()], path)
            with self.assertRaises(ValueError):
                manual.read_records(path)

    def test_missing_file_empty(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(manual.read_records(Path(temp) / 'missing.csv'), [])

    def test_empty_summary(self):
        result = manual.summarize([])
        self.assertFalse(result['complete'])
        self.assertIsNone(result['average_seconds'])

    def test_summary_totals(self):
        result = manual.summarize([sample(), sample('C02', 34.5)], 2)
        self.assertEqual(result['total_seconds'], 60.0)
        self.assertEqual(result['average_seconds'], 30.0)
        self.assertTrue(result['complete'])


if __name__ == '__main__':
    unittest.main()
