
from pathlib import Path

output = Path(__file__).parent / "resumes"
output.mkdir(exist_ok=True)

resumes = {
    "candidate_01.txt": """Candidate ID: C01
Experience: 2 years
Skills: Python, Machine Learning, Scikit-learn,
Pandas, SQL, TensorFlow, Git.
Projects: Built ML classification models.""",

    "candidate_02.txt": """Candidate ID: C02
Experience: 1.5 years
Skills: Python, Machine Learning, Scikit-learn,
Pandas, Git.
Projects: Built predictive analytics pipelines.""",

    "candidate_03.txt": """Candidate ID: C03
Experience: 2 years
Skills: Python, Pandas, Git.
Projects: Automated data reporting workflows.""",

    "candidate_04.txt": """Candidate ID: C04
Experience: 3 years
Skills: Python, Machine Learning, Scikit-learn,
Pandas, SQL, Docker, FastAPI, PyTorch, Git.
Projects: Deployed ML models through REST APIs.""",

    "candidate_05.txt": """Candidate ID: C05
Experience: 3 months
Skills: Python, Machine Learning, Scikit-learn,
Pandas, SQL.
Projects: University ML coursework.""",

    "candidate_06.txt": """Candidate ID: C06
Experience: Not specified
Skills: Python, Machine Learning, SQL, Pandas.
Projects: Worked on AI-related tasks.""",

    "candidate_07.txt": """Candidate ID: C07
Summary: Claims 3 years of ML experience.
Employment History: 6 months as an ML intern.
Skills: Python, Machine Learning, Scikit-learn,
Pandas, SQL.""",

    "candidate_08.txt": """Candidate ID: C08
Experience: 1 year
Skills: Python.
Projects: Not provided.""",

    "candidate_09.txt": """Candidate ID: C09
Experience: 2 years
Skills: Python, Machine Learning, Pandas, SQL.
Additional Notes: Resume content is incomplete.""",

    "candidate_10.txt": """Candidate ID: C10
Experience: 2 years in data analytics
Skills: Python, Pandas, SQL, Scikit-learn.
Projects: Built predictive forecasting models."""
}

for filename, content in resumes.items():
    (output / filename).write_text(
        content, encoding="utf-8"
    )

print(f"Created {len(resumes)} resumes in {output}")
