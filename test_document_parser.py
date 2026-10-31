
"""
RecruitFlow AI - Manual Document Parser Test
"""

import argparse
import json
import sys
from pathlib import Path

from src.document_parser import (
    extract_from_path,
    DocumentExtractionError,
)


def main():
    parser = argparse.ArgumentParser(
        description="Test RecruitFlow AI document extraction"
    )

    parser.add_argument(
        "file",
        help="Path to a TXT, PDF, or DOCX document"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Print complete extraction result as JSON"
    )

    args = parser.parse_args()

    try:
        result = extract_from_path(Path(args.file))

    except DocumentExtractionError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.json:
        print(
            json.dumps(
                result.to_dict(),
                indent=2,
                ensure_ascii=False
            )
        )
    else:
        print("=" * 60)
        print("RECRUITFLOW AI - DOCUMENT EXTRACTION")
        print("=" * 60)

        print(f"Filename: {result.filename}")
        print(f"Type: {result.file_type}")
        print(f"Characters: {result.character_count}")
        print(f"Pages: {result.page_count or 'N/A'}")

        if result.warnings:
            print("\nWarnings:")
            for warning in result.warnings:
                print(f"- {warning}")

        print("\nExtracted text:")
        print("-" * 60)
        print(result.text)
        print("-" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
