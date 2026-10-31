"""RecruitFlow AI analytics computed from saved review records."""
from collections import Counter

REVIEW_STATUSES = ("Meets requirements", "Missing requirements", "Needs clarification")
APPROVAL_STATUSES = ("Pending", "Approved", "Needs correction")
EXPERIENCE_STATUSES = ("Meets", "Below minimum", "Unknown", "Conflicting", "Needs review")


def summarize_reviews(reviews):
    """Return deterministic counts for reviews from database.list_reviews()."""
    records = list(reviews)
    review_counts = Counter(row["review_status"] for row in records)
    approval_counts = Counter(row["approval_status"] for row in records)
    experience_counts = Counter(row["experience_status"] for row in records)
    attention = [row for row in records if (
        row["approval_status"] == "Needs correction"
        or row["review_status"] == "Needs clarification"
        or row["experience_status"] in ("Unknown", "Conflicting", "Needs review")
    )]
    return {
        "total": len(records),
        "review_counts": {s: review_counts[s] for s in REVIEW_STATUSES},
        "approval_counts": {s: approval_counts[s] for s in APPROVAL_STATUSES},
        "experience_counts": {s: experience_counts[s] for s in EXPERIENCE_STATUSES},
        "attention_count": len(attention),
        "attention_rows": attention,
    }
