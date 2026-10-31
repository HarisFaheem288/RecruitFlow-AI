
"""
RecruitFlow AI - Manual Database Verification
"""

from pathlib import Path

from run_batch import create_demo_job
from src.review_generator import process_batch
from src.schemas import CandidateReview
from src.database import (
    initialize_database,
    save_job,
    save_review,
    get_review,
    list_reviews,
)


def main():
    db_path = Path("data/recruitflow.db")

    job = create_demo_job()
    batch = process_batch("data/resumes", job)

    initialize_database(db_path)
    save_job(job, db_path)

    for item in batch.reviews:
        review = CandidateReview(**item["review"])
        save_review(review, db_path)

    saved = list_reviews(job.job_id, db_path)

    print("=" * 55)
    print("RECRUITFLOW AI - DATABASE VERIFICATION")
    print("=" * 55)

    print(f"Database: {db_path}")
    print(f"Saved reviews: {len(saved)}")

    for review in saved:
        print(
            review["candidate_id"],
            "|",
            review["review_status"],
            "|",
            review["approval_status"],
        )

    c07 = get_review("C07", job.job_id, db_path)

    print("\nC07 experience:", c07["experience_status"])
    print("C07 approval:", c07["approval_status"])

    assert len(saved) == 10
    assert c07["experience_status"] == "Conflicting"
    assert all(
        item["approval_status"] == "Pending"
        for item in saved
    )

    print("\nDATABASE VERIFICATION PASSED")


if __name__ == "__main__":
    main()
