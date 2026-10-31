
import sys
import sqlite3
import json
import csv
import logging
import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

PACKAGES = {
    "streamlit": "streamlit",
    "pymupdf": "PyMuPDF",
    "docx": "python-docx",
    "pandas": "pandas",
    "dotenv": "python-dotenv",
    "pytest": "pytest",
}


def main():
    print("=" * 55)
    print("RecruitFlow AI - Environment Verification")
    print("=" * 55)

    print(f"\nPython version: {sys.version.split()[0]}")
    print(f"Python executable: {sys.executable}")
    print(f"Project directory: {PROJECT_ROOT}")

    failures = []

    print("\n[1] Checking dependencies")

    for module_name, display_name in PACKAGES.items():
        try:
            importlib.import_module(module_name)
            print(f"[PASS] {display_name}")
        except Exception as exc:
            print(f"[FAIL] {display_name}: {exc}")
            failures.append(display_name)

    print("\n[2] Checking standard library")

    for name, module in [
        ("sqlite3", sqlite3),
        ("json", json),
        ("csv", csv),
        ("logging", logging),
    ]:
        print(f"[PASS] {name}")

    print("\n[3] Checking project directories")

    for folder in ["src", "tests", "data", "docs", "evaluation"]:
        path = PROJECT_ROOT / folder

        if path.is_dir():
            print(f"[PASS] {folder}/")
        else:
            print(f"[FAIL] {folder}/ is missing")
            failures.append(folder)

    print("\n[4] Checking schema imports")

    try:
        from src.schemas import (
            JobDescription,
            Candidate,
            CandidateReview,
        )
        from src.validators import validate_review

        print("[PASS] RecruitFlow schemas and validators")

    except Exception as exc:
        print(f"[FAIL] Schema import: {exc}")
        failures.append("schema imports")

    print("\n" + "=" * 55)

    if failures:
        print("ENVIRONMENT CHECK FAILED")
        print("Problems:", ", ".join(failures))
        return 1

    print("ENVIRONMENT CHECK PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
