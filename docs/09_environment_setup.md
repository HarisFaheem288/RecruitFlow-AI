# \# RecruitFlow AI — Environment Setup

# 

# \## 1. Development Environment

# 

# \- Operating system: Windows 11

# \- Language: Python 3.11 or 3.12 recommended

# \- Application framework: Streamlit

# \- Document processing: PyMuPDF, python-docx

# \- Data handling: pandas

# \- Storage: SQLite

# \- Testing: unittest and pytest

# 

# \## 2. Project Location

# 

# D:\\RecruitFlow-AI

# 

# \## 3. Create Virtual Environment

# 

# ```cmd

# cd /d D:\\RecruitFlow-AI

# python -m venv .venv

# .venv\\Scripts\\activate.bat

# ```

# 

# \## 4. Install Dependencies

# 

# ```cmd

# python -m pip install --upgrade pip setuptools wheel

# python -m pip install -r requirements.txt

# ```

# 

# \## 5. Verify Environment

# 

# ```cmd

# python verify\_environment.py

# python -m pip check

# ```

# 

# \## 6. Run Automated Tests

# 

# ```cmd

# python -m unittest discover -s tests -p "test\_\*.py" -v

# python -m pytest tests -v

# ```

# 

# Expected: 12 tests executed successfully.

# 

# \## 7. Dependency Files

# 

# \- requirements.txt: Declared project dependencies

# \- requirements-lock.txt: Resolved installed package versions

# 

# \## 8. Development Rules

# 

# \- Activate the virtual environment before running project commands.

# \- Do not commit secrets or local environment files.

# \- Keep application logic in src/.

# \- Keep automated tests in tests/.

# \- Run tests after changing schemas or validators.

# \- Do not interpret zero discovered tests as a successful test run.

# 

# \## 9. Current Status

# 

# Environment installation and validation must be confirmed from actual terminal results.

# 

# Document extraction, matching, database persistence, and the user interface are not yet implemented.



