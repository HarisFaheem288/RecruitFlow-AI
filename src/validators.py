
from .schemas import (
    JobDescription,
    Candidate,
    CandidateReview,
    ApprovalStatus,
)


def validate_job_candidate(job, candidate):
    if not isinstance(job, JobDescription):
        raise TypeError("Expected a JobDescription object")

    if not isinstance(candidate, Candidate):
        raise TypeError("Expected a Candidate object")

    return True


def validate_review(review, job, candidate):
    validate_job_candidate(job, candidate)

    if not isinstance(review, CandidateReview):
        raise TypeError("Expected a CandidateReview object")

    if review.job_id != job.job_id:
        raise ValueError("Review job ID does not match job")

    if review.candidate_id != candidate.candidate_id:
        raise ValueError("Review candidate ID does not match")

    required = {
        skill.casefold() for skill in job.required_skills
    }

    matched = {
        skill.casefold() for skill in review.matched_skills
    }

    missing = {
        skill.casefold()
        for skill in review.missing_required_skills
    }

    if matched | missing != required:
        raise ValueError(
            "Review must account for every required skill"
        )

    if matched & missing:
        raise ValueError(
            "A skill cannot be matched and missing"
        )

    if review.approval_status != ApprovalStatus.PENDING:
        raise ValueError(
            "New generated reviews must be Pending"
        )

    return True
