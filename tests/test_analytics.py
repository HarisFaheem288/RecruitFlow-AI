import unittest
from src.analytics import summarize_reviews


def review(candidate_id="C01", review_status="Meets requirements", experience_status="Meets", approval_status="Pending"):
    return {"candidate_id": candidate_id, "job_id": "JOB001", "review_status": review_status,
            "experience_status": experience_status, "approval_status": approval_status}


class TestAnalytics(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_reviews([])["total"], 0)

    def test_zero_filled_statuses(self):
        self.assertEqual(summarize_reviews([])["review_counts"]["Needs clarification"], 0)

    def test_total(self):
        self.assertEqual(summarize_reviews([review(), review("C02")])["total"], 2)

    def test_meets(self):
        self.assertEqual(summarize_reviews([review()])["review_counts"]["Meets requirements"], 1)

    def test_missing(self):
        self.assertEqual(summarize_reviews([review(review_status="Missing requirements")])["review_counts"]["Missing requirements"], 1)

    def test_pending(self):
        self.assertEqual(summarize_reviews([review()])["approval_counts"]["Pending"], 1)

    def test_approved(self):
        self.assertEqual(summarize_reviews([review(approval_status="Approved")])["approval_counts"]["Approved"], 1)

    def test_conflicting_attention(self):
        self.assertEqual(summarize_reviews([review(experience_status="Conflicting")])["attention_count"], 1)

    def test_needs_correction_attention(self):
        self.assertEqual(summarize_reviews([review(approval_status="Needs correction")])["attention_count"], 1)

    def test_no_duplicate_attention(self):
        result = summarize_reviews([review(review_status="Needs clarification", experience_status="Conflicting", approval_status="Needs correction")])
        self.assertEqual(result["attention_count"], 1)

    def test_ordinary_pending_not_attention(self):
        self.assertEqual(summarize_reviews([review()])["attention_count"], 0)

    def test_experience_below_minimum(self):
        self.assertEqual(summarize_reviews([review(experience_status="Below minimum")])["experience_counts"]["Below minimum"], 1)


if __name__ == "__main__":
    unittest.main()
