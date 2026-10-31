"""Tests for Day 4 Task 2 automated screening benchmark."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evaluation.benchmark_automation import benchmark, main, save_results


class FakeResult:
    def __init__(self, statuses=None, errors=None):
        statuses = statuses if statuses is not None else ["Meets requirements", "Needs clarification"]
        self.reviews = [
            {"source_file": f"candidate_{i:02}.txt", "review": {"candidate_id": f"C{i:02}", "review_status": status}}
            for i, status in enumerate(statuses, 1)
        ]
        self.errors = errors or []
        self.successful = len(self.reviews)
        self.failed = len(self.errors)


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def run_fake(self, iterations=2, warmups=1, results=None):
        results = results or FakeResult()
        times = iter(range(100, 100 + 2 * (iterations + warmups)))
        with patch("evaluation.benchmark_automation.create_demo_job") as job, patch(
            "evaluation.benchmark_automation.process_batch", return_value=results
        ) as process:
            job.return_value.job_id = "JOB001"
            result = benchmark(self.folder, iterations, warmups, clock=lambda: next(times))
            return result, process.call_count

    def test_measured_run_count(self):
        summary, calls = self.run_fake()
        self.assertEqual(summary["measured_runs"], 2)
        self.assertEqual(calls, 3)

    def test_warmups_excluded(self):
        summary, _ = self.run_fake()
        self.assertEqual(len(summary["run_seconds"]), 2)

    def test_total_mean(self):
        summary, _ = self.run_fake()
        self.assertEqual(summary["total_seconds_mean"], 1)

    def test_per_resume_mean(self):
        summary, _ = self.run_fake()
        self.assertEqual(summary["seconds_per_resume_mean"], 0.5)

    def test_status_counts(self):
        summary, _ = self.run_fake()
        self.assertEqual(summary["screening_status_counts"]["Needs clarification"], 1)

    def test_candidate_ids(self):
        summary, _ = self.run_fake()
        self.assertEqual(summary["candidate_ids"], ["C01", "C02"])

    def test_reject_zero_iterations(self):
        with self.assertRaises(ValueError):
            benchmark(self.folder, iterations=0)

    def test_reject_negative_warmups(self):
        with self.assertRaises(ValueError):
            benchmark(self.folder, warmups=-1)

    def test_reject_missing_folder(self):
        with self.assertRaises(ValueError):
            benchmark(self.folder / "missing")

    def test_reject_file_failures(self):
        with patch("evaluation.benchmark_automation.create_demo_job"), patch(
            "evaluation.benchmark_automation.process_batch", return_value=FakeResult(errors=[{"source_file": "bad.pdf", "error": "corrupt"}])
        ):
            with self.assertRaisesRegex(RuntimeError, "file\\(s\\) failed"):
                benchmark(self.folder, 1, 0)

    def test_reject_inconsistent_runs(self):
        with patch("evaluation.benchmark_automation.create_demo_job"), patch(
            "evaluation.benchmark_automation.process_batch", side_effect=[FakeResult(), FakeResult(["Missing requirements", "Needs clarification"])]
        ):
            with self.assertRaisesRegex(RuntimeError, "inconsistent"):
                benchmark(self.folder, 2, 0)

    def test_reject_no_resumes(self):
        with patch("evaluation.benchmark_automation.create_demo_job"), patch(
            "evaluation.benchmark_automation.process_batch", return_value=FakeResult([])
        ):
            with self.assertRaisesRegex(RuntimeError, "no resumes"):
                benchmark(self.folder, 1, 0)

    def test_json_saved(self):
        summary, _ = self.run_fake()
        json_path, _ = save_results(summary, self.folder)
        self.assertEqual(json.loads(json_path.read_text())["resume_count"], 2)

    def test_csv_saved(self):
        summary, _ = self.run_fake()
        _, csv_path = save_results(summary, self.folder)
        with csv_path.open(newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 2)

    def test_output_directory_created(self):
        summary, _ = self.run_fake()
        path, _ = save_results(summary, self.folder / "nested")
        self.assertTrue(path.exists())

    def test_main_prints_summary(self):
        with patch("evaluation.benchmark_automation.benchmark", return_value=self.run_fake()[0]), patch(
            "evaluation.benchmark_automation.save_results", return_value=(Path("summary.json"), Path("runs.csv"))
        ), patch("builtins.print") as print_mock:
            self.assertEqual(main(["--iterations", "2"]), 0)
            self.assertTrue(print_mock.called)


if __name__ == "__main__":
    unittest.main()
