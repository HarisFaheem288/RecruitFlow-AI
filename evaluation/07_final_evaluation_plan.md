# \# RecruitFlow AI — Evaluation Plan

# 

# \## 1. Evaluation Objective

# 

# Determine whether RecruitFlow AI improves the speed, consistency, completeness, and reliability of candidate screening compared with the previous workflow.

# 

# \## 2. Evaluation Dataset

# 

# \- Job: Junior AI/ML Engineer

# \- Candidate resumes: 10 synthetic TXT files

# \- Reference file: 02\_expected\_results.csv

# \- Original baseline: 03\_manual\_baseline.csv

# \- CV-verified assessments: 04\_cv\_verified\_reviews.csv

# 

# \## 3. Existing Day 1 Results

# 

# | Metric | Recorded result |

# |---|---|

# | Candidates | 10 |

# | Total recorded review time | 454.90 seconds |

# | Average time per candidate | 45.49 seconds |

# | Screening status agreement | 100% |

# | Missing skills agreement | 20% |

# | Experience agreement | 40% |

# | Full review agreement | 20% |

# 

# \## 4. Important Baseline Limitation

# 

# The initial manual screening entries were entered without independently reviewing the candidate CVs.

# 

# Therefore:

# 

# \- The recorded times are not yet a validated manual-review performance baseline.

# \- The accuracy percentages measure agreement between entered values and reference answers.

# \- The 20% full-review agreement must not be presented as actual recruiter accuracy.

# \- A new independent, timed manual review is required for a defensible before-and-after comparison.

# 

# The original files must remain unchanged to preserve the evaluation history.

# 

# \## 5. Evaluation Metrics

# 

# \### A. Processing Time

# 

# Measure the time required to complete the same candidate review manually and using RecruitFlow AI, including human verification and corrections.

# 

# Time Reduction (%) = ((Manual Time - System-Assisted Time) / Manual Time) × 100

# 

# Target: At least 40%.

# 

# \### B. Evidence Accuracy

# 

# Compare extracted qualifications, missing requirements, and experience assessments against independently validated reference answers.

# 

# Target: At least 90% field-level agreement.

# 

# \### C. Report Completeness

# 

# Check that every required report field is populated or explicitly marked unknown.

# 

# Target: 100%.

# 

# \### D. Functional Reliability

# 

# Run 10 predefined test cases and record actual outcomes.

# 

# Target: At least 9/10 passing.

# 

# \### E. Human Intervention

# 

# Record:

# 

# \- Number of manual corrections

# \- Number of clarification flags

# \- Number of approvals

# \- Time spent reviewing generated assessments

# 

# \## 6. Test Scenarios

# 

# | ID | Scenario | Expected Behavior |

# |---|---|---|

# | C01 | All requirements present | Identify all required evidence |

# | C02 | SQL not mentioned | Flag missing SQL evidence |

# | C03 | Multiple skills absent | Identify three missing skills |

# | C04 | Strong qualification evidence | Identify all required skills |

# | C05 | Insufficient experience | Flag experience below minimum |

# | C06 | Experience unspecified | Request clarification |

# | C07 | Contradictory experience | Flag inconsistency |

# | C08 | Multiple qualifications absent | Identify missing evidence |

# | C09 | Incomplete resume | Flag incomplete information |

# | C10 | Transferable experience | Request human review |

# 

# A separate corrupted-document test will also be included during reliability testing.

# 

# \## 7. Failure Analysis

# 

# For at least three failures, record:

# 

# 1\. Test input

# 2\. Expected behavior

# 3\. Actual behavior

# 4\. Root cause

# 5\. Fix applied

# 6\. Regression test result

# 

# \## 8. Comparison Method

# 

# \- Use the same job description and candidate documents.

# \- Keep the expected results fixed during evaluation.

# \- Measure full human-assisted workflow time, not only model processing time.

# \- Record corrections and exceptions.

# \- Distinguish functional test success from recruiting quality.

# \- Do not claim a speed or accuracy improvement unless the measurements support it.

# 

# \## 9. Evaluation Status

# 

# Day 1: Initial dataset and reference comparison completed.

# 

# Independent manual baseline: Pending.

# 

# Automated system evaluation: Pending Day 4.

# 

# Final performance comparison: Pending.



