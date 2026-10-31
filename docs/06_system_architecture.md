# \# RecruitFlow AI — System Architecture

# 

# \## 1. Overview

# 

# RecruitFlow AI is a local, Python-based recruitment review assistant designed to support repeatable, evidence-based candidate screening.

# 

# The system converts job descriptions and resumes into structured review drafts that a human recruiter can inspect, correct, and approve.

# 

# The MVP is designed for local execution and does not require a paid LLM API.

# 

# \## 2. Architecture Style

# 

# The application uses a modular architecture with separate components for:

# 

# \- User interface

# \- Document ingestion

# \- Text extraction

# \- Job requirement processing

# \- Candidate evidence matching

# \- Review generation

# \- Human approval

# \- Data persistence

# \- Reporting and logging

# 

# The user interface does not directly implement matching logic. Business rules are separated from document parsing and database operations.

# 

# \## 3. Technology Stack

# 

# | Layer | Technology | Responsibility |

# |---|---|---|

# | Interface | Streamlit | Uploads, review, approval, export |

# | Application | Python | Coordinate the workflow |

# | TXT parsing | Python standard library | Read text files |

# | PDF parsing | PyMuPDF | Extract PDF text |

# | DOCX parsing | python-docx | Extract Word text |

# | Matching | Python rules and text normalization | Compare qualifications |

# | Storage | SQLite | Reviews, corrections, approvals |

# | Reporting | CSV and JSON | Portable review outputs |

# | Logging | Python logging | Processing events and failures |

# 

# \## 4. End-to-End Workflow

# 

# 1\. The recruiter uploads a job description and candidate resume.

# 2\. The interface validates file extensions and file sizes.

# 3\. The document parser extracts readable text.

# 4\. The application normalizes extracted text.

# 5\. The system identifies required job qualifications.

# 6\. The matching engine searches for supporting resume evidence.

# 7\. Experience requirements are checked against explicit information.

# 8\. Missing or uncertain information is flagged.

# 9\. A structured draft review is generated.

# 10\. The recruiter inspects and optionally corrects the review.

# 11\. The recruiter explicitly approves the assessment.

# 12\. The approved review is saved to SQLite.

# 13\. A CSV or JSON report is made available for export.

# 

# \## 5. Core Components

# 

# \### UI Layer

# 

# Displays the application, accepts uploaded files, presents assessments, and collects human decisions.

# 

# \### Document Parser

# 

# Supports TXT, PDF, and DOCX documents.

# 

# Returns extracted text or a structured error.

# 

# \### Job Requirement Processor

# 

# Transforms job requirements into structured required skills, preferred skills, and experience criteria.

# 

# For the MVP, the recruiter can review or correct extracted requirements.

# 

# \### Matching Engine

# 

# Compares candidate evidence against required qualifications.

# 

# Explicit evidence is distinguished from missing or uncertain information.

# 

# \### Review Generator

# 

# Creates consistent candidate assessments with missing skills, experience evidence, review status, and warnings.

# 

# \### Human Review Module

# 

# Allows correction, approval, and clarification requests.

# 

# Final approval requires an explicit human action.

# 

# \### Database Layer

# 

# Stores review records, corrections, timestamps, and approval status.

# 

# \### Reporting Module

# 

# Exports assessments in CSV or JSON format.

# 

# \### Logging Module

# 

# Records processing outcomes and technical errors without unnecessarily storing sensitive resume contents.

# 

# \## 6. Error Handling

# 

# | Failure | Expected Behavior |

# |---|---|

# | Empty resume | Stop processing and display error |

# | Unsupported file | Reject upload with explanation |

# | Corrupted PDF/DOCX | Return parsing error |

# | Missing experience | Mark Unknown |

# | Conflicting experience | Flag for clarification |

# | Missing skill evidence | Record as not evidenced |

# | Database error | Show failure and preserve draft where possible |

# | Unapproved review | Do not present as approved |

# 

# \## 7. Privacy and Permissions

# 

# \- Synthetic data is used during development.

# \- The application runs locally.

# \- No candidate data is sent to an external LLM in the MVP.

# \- Final assessment approval remains a human action.

# \- Logs avoid unnecessary personal information.

# \- Review history is retained locally.

# 

# \## 8. Architectural Trade-offs

# 

# \### Rule-Based Matching

# 

# Advantages:

# \- Deterministic behavior

# \- Low cost

# \- Easy to test

# \- No external API dependency

# 

# Limitations:

# \- May miss synonyms and implicit skills

# \- Cannot reliably infer skill proficiency

# \- Requires careful handling of ambiguous text

# 

# \### SQLite

# 

# Advantages:

# \- Lightweight

# \- No separate database server

# \- Easy local setup

# 

# Limitations:

# \- Not ideal for large multi-user deployments

# 

# \### Streamlit

# 

# Advantages:

# \- Fast development

# \- Simple local deployment

# \- Accessible to non-developers

# 

# Limitations:

# \- Less control over complex enterprise workflows

# 

# \## 9. Future Improvements

# 

# Potential later iterations include semantic evidence extraction, recruiter feedback analytics, configurable job requirements, and ATS integrations.

# 

# These improvements are outside the initial five-day MVP unless core requirements are completed early.

# 

# \## 10. Definition of Architectural Success

# 

# The design is successful when one valid resume can move from upload through extraction, matching, structured review, human approval, and export, with understandable errors and reproducible behavior.



