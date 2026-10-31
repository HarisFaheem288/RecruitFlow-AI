
import csv
from pathlib import Path

path = Path(__file__).parent / "03_manual_baseline.csv"

if not path.exists():
    print("ERROR: Manual baseline CSV file not found.")
    raise SystemExit(1)

with path.open("r", newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    required_columns = [
        "candidate_id",
        "manual_time_seconds"
    ]

    if not reader.fieldnames or any(
        col not in reader.fieldnames
        for col in required_columns
    ):
        print("ERROR: CSV headers are missing or incorrect.")
        print("Found headers:", reader.fieldnames)
        raise SystemExit(1)

    rows = list(reader)

times = []
invalid_rows = []

for row in rows:
    candidate_id = (row.get("candidate_id") or "").strip()
    raw_time = (row.get("manual_time_seconds") or "").strip()

    if not raw_time:
        invalid_rows.append(candidate_id or "Unknown")
        continue

    try:
        seconds = float(raw_time)

        if seconds <= 0:
            raise ValueError("Time must be positive")

        times.append(seconds)

    except ValueError:
        invalid_rows.append(candidate_id or "Unknown")

print("\n===== RecruitFlow AI: Manual Baseline =====")

print(f"Total candidate rows: {len(rows)}")
print(f"Valid time records: {len(times)}")

if invalid_rows:
    print("Missing/invalid time records:",
          ", ".join(invalid_rows))

if len(times) != 10 or len(rows) != 10:
    print("\nBaseline is incomplete.")
    print("Complete all 10 candidate reviews first.")
else:
    total = sum(times)
    average = total / len(times)

    print(f"\nTotal manual time: {total:.2f} seconds")
    print(f"Average time per resume: {average:.2f} seconds")
    print(f"Average time per resume: {average / 60:.2f} minutes")

    print("\nBaseline measurement completed successfully!")
