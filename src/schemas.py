
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime, timezone
import json
import math


class ReviewStatus(str, Enum):
    MEETS = "Meets requirements"
    MISSING = "Missing requirements"
    CLARIFY = "Needs clarification"


class ExperienceStatus(str, Enum):
    MEETS = "Meets"
    BELOW = "Below minimum"
    UNKNOWN = "Unknown"
    CONFLICTING = "Conflicting"
    NEEDS_REVIEW = "Needs review"


class ApprovalStatus(str, Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    NEEDS_CORRECTION = "Needs correction"


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def clean_skills(skills):
    if not isinstance(skills, list):
        raise ValueError("Skills must be a list")

    result = []
    seen = set()

    for skill in skills:
        text = required_text(skill, "Skill")
        key = text.casefold()

        if key not in seen:
            seen.add(key)
            result.append(text)

    return result


def valid_experience(value):
    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(
        value, (int, float)
    ):
        raise ValueError("Experience must be numeric or None")

    if not math.isfinite(value) or value < 0:
        raise ValueError("Experience must be finite and nonnegative")

    return float(value)


@dataclass
class JobDescription:
    job_id: str
    title: str
    required_skills: list[str]
    preferred_skills: list[str] = field(default_factory=list)
    min_experience_years: float = 0.0

    def __post_init__(self):
        self.job_id = required_text(self.job_id, "Job ID")
        self.title = required_text(self.title, "Job title")
        self.required_skills = clean_skills(self.required_skills)
        self.preferred_skills = clean_skills(self.preferred_skills)

        if not self.required_skills:
            raise ValueError("At least one required skill is needed")

        self.min_experience_years = valid_experience(
            self.min_experience_years
        )

        if self.min_experience_years is None:
            raise ValueError("Minimum experience cannot be None")


@dataclass
class Candidate:
    candidate_id: str
    skills: list[str]
    experience_years: Optional[float] = None
    experience_evidence: str = ""
    project_evidence: str = ""
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.candidate_id = required_text(
            self.candidate_id, "Candidate ID"
        )
        self.skills = clean_skills(self.skills)
        self.experience_years = valid_experience(
            self.experience_years
        )
        self.experience_evidence = str(
            self.experience_evidence or ""
        ).strip()
        self.project_evidence = str(
            self.project_evidence or ""
        ).strip()
        self.warnings = clean_skills(self.warnings)


@dataclass
class CandidateReview:
    candidate_id: str
    job_id: str
    matched_skills: list[str]
    missing_required_skills: list[str]
    experience_status: ExperienceStatus
    review_status: ReviewStatus
    evidence_notes: str
    warnings: list[str] = field(default_factory=list)
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    human_corrections: list[str] = field(default_factory=list)
    processing_timestamp: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def __post_init__(self):
        self.candidate_id = required_text(
            self.candidate_id, "Candidate ID"
        )
        self.job_id = required_text(self.job_id, "Job ID")
        self.matched_skills = clean_skills(
            self.matched_skills
        )
        self.missing_required_skills = clean_skills(
            self.missing_required_skills
        )
        self.warnings = clean_skills(self.warnings)
        self.human_corrections = clean_skills(
            self.human_corrections
        )

        self.experience_status = ExperienceStatus(
            self.experience_status
        )
        self.review_status = ReviewStatus(
            self.review_status
        )
        self.approval_status = ApprovalStatus(
            self.approval_status
        )

        if not isinstance(self.evidence_notes, str):
            raise ValueError("Evidence notes must be text")

        if not self.evidence_notes.strip():
            raise ValueError("Evidence notes cannot be empty")

        overlap = {
            s.casefold() for s in self.matched_skills
        } & {
            s.casefold() for s in self.missing_required_skills
        }

        if overlap:
            raise ValueError(
                "Skills cannot be both matched and missing"
            )

        try:
            datetime.fromisoformat(self.processing_timestamp)
        except (ValueError, TypeError):
            raise ValueError("Invalid processing timestamp")

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False
        )
