
"""
RecruitFlow AI - Initial Skill-Matching Engine

Rule-based evidence matching for synthetic resumes.
This is decision support, not an automated hiring system.
"""

import re
from dataclasses import dataclass

from .schemas import (
    JobDescription,
    Candidate,
    CandidateReview,
    ExperienceStatus,
    ReviewStatus,
)
from .validators import validate_review


SKILL_ALIASES = {
    "python": ["python"],
    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml",
    ],
    "scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn",
    ],
    "pandas": ["pandas"],
    "sql": ["sql"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch", "torch"],
    "fastapi": ["fastapi"],
    "docker": ["docker"],
    "git": ["git"],
}


@dataclass
class SkillEvidence:
    skill: str
    matched: bool
    evidence: str = ""


def normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip()).casefold()


def aliases_for(skill: str) -> list[str]:
    key = normalize_skill(skill)
    return SKILL_ALIASES.get(key, [skill])


def contains_skill(text: str, skill: str) -> bool:
    """
    Match a skill as a phrase, not as a substring.

    Examples:
    - SQL does not match NoSQL
    - Git does not match GitHub
    """
    for alias in aliases_for(skill):
        pattern = (
            r"(?<![A-Za-z0-9])"
            + re.escape(alias)
            + r"(?![A-Za-z0-9])"
        )

        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def find_skill_evidence(
    resume_text: str,
    required_skills: list[str],
) -> list[SkillEvidence]:
    """
    Return matching evidence for every required skill.

    The first matching line is used as a traceable excerpt.
    """
    lines = resume_text.splitlines()
    results = []

    for skill in required_skills:
        evidence = ""

        for line in lines:
            if contains_skill(line, skill):
                evidence = line.strip()
                break

        results.append(
            SkillEvidence(
                skill=skill,
                matched=bool(evidence),
                evidence=evidence,
            )
        )

    return results


def extract_experience_claims(text: str) -> list[float]:
    """
    Extract simple numeric duration claims.

    Supported examples:
    - 2 years
    - 1.5 years of experience
    - 6 months

    This does not infer dates or add employment periods.
    """
    pattern = (
        r"(?<!\w)"
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(years?|yrs?|months?|mos?)"
        r"\b"
    )

    claims = []

    for match in re.finditer(
        pattern, text, flags=re.IGNORECASE
    ):
        amount = float(match.group(1))
        unit = match.group(2).casefold()

        if unit.startswith(("month", "mo")):
            amount /= 12.0

        claims.append(amount)

    return claims


def evaluate_experience(
    resume_text: str,
    minimum_years: float,
) -> tuple[ExperienceStatus, float | None, list[str]]:
    """
    Evaluate explicitly stated durations.

    Multiple different claims are flagged for review.
    The engine does not silently add overlapping periods.
    """
    claims = extract_experience_claims(resume_text)
    warnings = []

    if not claims:
        warnings.append(
            "Experience duration is not explicitly stated."
        )
        return ExperienceStatus.UNKNOWN, None, warnings

    unique_claims = sorted({
        round(value, 3) for value in claims
    })

    if len(unique_claims) > 1:
        warnings.append(
            "Multiple experience durations were found; "
            "human review is required."
        )
        return ExperienceStatus.CONFLICTING, None, warnings

    years = unique_claims[0]

    if years < minimum_years:
        return ExperienceStatus.BELOW, years, warnings

    return ExperienceStatus.MEETS, years, warnings


def build_candidate(
    candidate_id: str,
    resume_text: str,
    job: JobDescription,
) -> Candidate:
    """
    Build a Candidate from explicit evidence in resume text.
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty")

    skills = []

    for skill in (
        job.required_skills + job.preferred_skills
    ):
        if contains_skill(resume_text, skill):
            skills.append(skill)

    _, experience_years, warnings = evaluate_experience(
        resume_text,
        job.min_experience_years,
    )

    return Candidate(
        candidate_id=candidate_id,
        skills=skills,
        experience_years=experience_years,
        experience_evidence=(
            "Numeric experience claims: "
            + str(extract_experience_claims(resume_text))
        ),
        warnings=warnings,
    )


def screen_candidate(
    job: JobDescription,
    candidate_id: str,
    resume_text: str,
) -> CandidateReview:
    """
    Generate a draft review for human inspection.
    """
    candidate = build_candidate(
        candidate_id, resume_text, job
    )

    skill_results = find_skill_evidence(
        resume_text,
        job.required_skills,
    )

    matched = [
        result.skill
        for result in skill_results
        if result.matched
    ]

    missing = [
        result.skill
        for result in skill_results
        if not result.matched
    ]

    experience_status, years, exp_warnings = (
        evaluate_experience(
            resume_text,
            job.min_experience_years,
        )
    )

    warnings = list(exp_warnings)

    # Skills can be explicitly negated in resume text.
    # Flag common negation patterns for human verification.
    for result in skill_results:
        if not result.matched:
            continue

        if re.search(
            r"\b(no experience with|not familiar with|"
            r"never used|no knowledge of)\b",
            result.evidence,
            flags=re.IGNORECASE,
        ):
            warnings.append(
                f"Potential negation near {result.skill}; "
                "verify the evidence manually."
            )

    if experience_status in {
        ExperienceStatus.UNKNOWN,
        ExperienceStatus.CONFLICTING,
        ExperienceStatus.NEEDS_REVIEW,
    }:
        review_status = ReviewStatus.CLARIFY

    elif missing or experience_status == ExperienceStatus.BELOW:
        review_status = ReviewStatus.MISSING

    else:
        review_status = ReviewStatus.MEETS

    if warnings and review_status == ReviewStatus.MEETS:
        review_status = ReviewStatus.CLARIFY

    evidence_lines = []

    for result in skill_results:
        if result.matched:
            evidence_lines.append(
                f"{result.skill}: {result.evidence}"
            )
        else:
            evidence_lines.append(
                f"{result.skill}: not evidenced"
            )

    evidence_lines.append(
        f"Experience status: {experience_status.value}"
    )

    if years is not None:
        evidence_lines.append(
            f"Experience duration: {years:g} years"
        )

    review = CandidateReview(
        candidate_id=candidate_id,
        job_id=job.job_id,
        matched_skills=matched,
        missing_required_skills=missing,
        experience_status=experience_status,
        review_status=review_status,
        evidence_notes="\n".join(evidence_lines),
        warnings=warnings,
    )

    validate_review(review, job, candidate)

    return review
