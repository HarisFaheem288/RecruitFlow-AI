
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

EXPECTED_FILE = BASE_DIR / "02_expected_results.csv"
MANUAL_FILE = BASE_DIR / "03_manual_baseline.csv"
OUTPUT_FILE = BASE_DIR / "05_manual_accuracy_results.csv"


def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(f"No CSV headers in {path.name}")

        rows = {}

        for row in reader:
            candidate_id = (
                row.get("candidate_id") or ""
            ).strip().upper()

            if not candidate_id:
                raise ValueError(
                    f"Missing candidate ID in {path.name}"
                )

            if candidate_id in rows:
                raise ValueError(
                    f"Duplicate candidate: {candidate_id}"
                )

            rows[candidate_id] = row

        return rows


def normalize(value):
    return " ".join(
        (value or "").strip().lower().split()
    )


def normalize_skills(value):
    text = normalize(value)

    if text in ("", "none"):
        return set()

    return {
        skill.strip()
        for skill in text.split(";")
        if skill.strip()
    }


def evaluate():
    expected = load_csv(EXPECTED_FILE)
    manual = load_csv(MANUAL_FILE)

    if set(expected) != set(manual):
        missing = sorted(set(expected) - set(manual))
        extra = sorted(set(manual) - set(expected))

        raise ValueError(
            f"Candidate IDs do not match. "
            f"Missing: {missing}, Extra: {extra}"
        )

    results = []
    status_correct = 0
    skills_correct = 0
    experience_correct = 0
    fully_correct = 0

    for candidate_id in sorted(expected):
        exp = expected[candidate_id]
        man = manual[candidate_id]

        status_match = (
            normalize(exp.get("expected_status"))
            == normalize(man.get("manual_status"))
        )

        skills_match = (
            normalize_skills(
                exp.get("missing_required_skills")
            )
            == normalize_skills(
                man.get("missing_required_skills")
            )
        )

        experience_match = (
            normalize(exp.get("experience_status"))
            == normalize(man.get("experience_status"))
        )

        all_match = (
            status_match
            and skills_match
            and experience_match
        )

        status_correct += status_match
        skills_correct += skills_match
        experience_correct += experience_match
        fully_correct += all_match

        results.append({
            "candidate_id": candidate_id,
            "status_match": status_match,
            "skills_match": skills_match,
            "experience_match": experience_match,
            "fully_correct": all_match,
            "expected_status": exp.get("expected_status"),
            "manual_status": man.get("manual_status")
        })

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    total = len(results)

    print("\n===== RecruitFlow AI =====")
    print("MANUAL ACCURACY EVALUATION\n")

    print(f"Total candidates: {total}")
    print(
        f"Status accuracy: "
        f"{status_correct / total * 100:.2f}%"
    )
    print(
        f"Missing skills accuracy: "
        f"{skills_correct / total * 100:.2f}%"
    )
    print(
        f"Experience accuracy: "
        f"{experience_correct / total * 100:.2f}%"
    )
    print(
        f"Fully correct reviews: "
        f"{fully_correct}/{total}"
    )
    print(
        f"Full review accuracy: "
        f"{fully_correct / total * 100:.2f}%"
    )

    print("\nCandidate Results:")

    for result in results:
        outcome = (
            "PASS" if result["fully_correct"]
            else "FAIL"
        )
        print(
            f"{result['candidate_id']}: {outcome}"
        )

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        evaluate()
    except (ValueError, FileNotFoundError) as error:
        print(f"\nERROR: {error}")
        raise SystemExit(1)
