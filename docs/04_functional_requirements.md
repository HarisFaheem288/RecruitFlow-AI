# \# RecruitFlow AI — Functional Requirements

# 

# \## Functional Requirements

# 

# | ID | Requirement | Priority | Acceptance Test |

# |---|---|---|---|

# | FR-01 | Upload a job description | Must | Valid TXT job description is accepted |

# | FR-02 | Upload candidate resumes | Must | Valid TXT, PDF, DOCX files are processed |

# | FR-03 | Extract document text | Must | Readable text is returned without invented content |

# | FR-04 | Identify required skills | Must | Required skills are matched against explicit evidence |

# | FR-05 | Evaluate experience evidence | Must | Known, unknown, insufficient, and conflicting experience are distinguished |

# | FR-06 | Generate structured reviews | Must | Each report includes all mandatory fields |

# | FR-07 | Display missing evidence | Must | Unverified requirements are clearly identified |

# | FR-08 | Support human corrections | Must | Recruiter can edit assessments |

# | FR-09 | Require human approval | Must | No final assessment is marked approved automatically |

# | FR-10 | Store review history | Must | Records persist in SQLite |

# | FR-11 | Export review reports | Must | Valid CSV or JSON report is generated |

# | FR-12 | Handle invalid documents | Must | Useful error message is shown without crashing |

# | FR-13 | Record processing logs | Must | Success and failure events are recorded |

# | FR-14 | Process multiple candidates | Should | Several resumes can be reviewed in one session |

# | FR-15 | LLM-based evidence extraction | Optional | Only added if measurable quality improves |

# 

# \## Structured Review Schema

# 

# Each review will contain:

# 

# \- candidate\_id

# \- job\_id

# \- required\_skills

# \- matched\_skills

# \- missing\_required\_skills

# \- experience\_evidence

# \- experience\_status

# \- review\_status

# \- evidence\_notes

# \- warnings

# \- human\_corrections

# \- approval\_status

# \- processing\_timestamp

# 

# \## Allowed Review Statuses

# 

# \- Meets requirements

# \- Missing requirements

# \- Needs clarification

# 

# These are evidence-review categories, not automatic hiring or rejection decisions.

# 

# \## Allowed Experience Statuses

# 

# \- Meets

# \- Below minimum

# \- Unknown

# \- Conflicting

# \- Needs review

# 

# \## Validation Rules

# 

# 1\. Candidate ID must not be empty.

# 2\. A resume with no extractable text must produce an error.

# 3\. Every required skill must have a recorded evidence state.

# 4\. Unsupported qualifications must not be invented.

# 5\. Missing or contradictory experience must be flagged.

# 6\. Every review must start as unapproved.

# 7\. Human corrections must be distinguishable from generated assessments.

# 8\. Exported reports must preserve the final approved review.

# 

# \## Non-Functional Requirements

# 

# \- Local execution on Windows.

# \- No paid API required for the core workflow.

# \- Reproducible installation.

# \- Clear messages for non-technical users.

# \- No hardcoded secrets.

# \- Auditable review history.

# \- Processing failures must not erase existing records.



