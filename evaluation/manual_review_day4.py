"""Day 4: independently timed, resumable human screening baseline.

Run from project root: python evaluation/manual_review_day4.py
"""
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESUMES = ROOT / 'data' / 'resumes'
JOB = ROOT / 'data' / 'job_description.txt'
OUTPUT = ROOT / 'evaluation' / '08_genuine_manual_baseline.csv'
SUMMARY = ROOT / 'evaluation' / '09_genuine_baseline_summary.json'
FIELDS = ['candidate_id', 'filename', 'review_status', 'experience_status', 'matched_skills', 'missing_required_skills', 'evidence_notes', 'duration_seconds', 'reviewed_at_utc']
REVIEW_STATUSES = {'1': 'Meets requirements', '2': 'Missing requirements', '3': 'Needs clarification'}
EXPERIENCE_STATUSES = {'1': 'Meets', '2': 'Below minimum', '3': 'Unknown', '4': 'Conflicting', '5': 'Needs review'}


def candidate_id(path):
    suffix = path.stem.removeprefix('candidate_')
    return 'C' + suffix if path.stem.startswith('candidate_') and suffix.isdigit() else path.stem.upper()


def validate_record(row):
    if row['review_status'] not in REVIEW_STATUSES.values():
        raise ValueError('Invalid review status')
    if row['experience_status'] not in EXPERIENCE_STATUSES.values():
        raise ValueError('Invalid experience status')
    if not row['evidence_notes'].strip():
        raise ValueError('Evidence notes are required')
    if float(row['duration_seconds']) <= 0:
        raise ValueError('Duration must be positive')
    return row


def read_records(path=OUTPUT):
    path = Path(path)
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8-sig', newline='') as file:
        records = list(csv.DictReader(file))
    for record in records:
        validate_record(record)
    ids = [r['candidate_id'] for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate candidate IDs in baseline')
    return records


def save_records(records, path=OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(validate_record(record))


def summarize(records, expected_total=10):
    durations = [float(r['duration_seconds']) for r in records]
    total = round(sum(durations), 2)
    return {
        'baseline_type': 'timed_independent_human_review',
        'reviewed_count': len(records),
        'expected_count': expected_total,
        'complete': len(records) == expected_total,
        'total_seconds': total,
        'average_seconds': round(total / len(records), 2) if records else None,
        'min_seconds': round(min(durations), 2) if durations else None,
        'max_seconds': round(max(durations), 2) if durations else None,
        'status_counts': {v: sum(r['review_status'] == v for r in records) for v in REVIEW_STATUSES.values()},
        'note': 'Self-recorded manual review times; not independently observed or verified.',
    }


def prompt_choice(label, options):
    while True:
        print(f'\n{label}')
        for key, value in options.items():
            print(f'  {key}. {value}')
        value = input('Select number: ').strip()
        if value in options:
            return options[value]
        print('Invalid selection. Try again.')


def prompt_required(label):
    while True:
        value = input(f'{label}: ').strip()
        if value:
            return value
        print('This field is required.')


def run():
    if not JOB.is_file() or not RESUMES.is_dir():
        raise FileNotFoundError('Missing data/job_description.txt or data/resumes/')
    resumes = sorted(RESUMES.glob('*.txt'))
    if not resumes:
        raise ValueError('No TXT resumes found in data/resumes/')
    records = read_records()
    reviewed = {r['candidate_id'] for r in records}
    print('\nDAY 4 — GENUINE MANUAL BASELINE')
    print('Do not consult AI predictions or expected-results files while reviewing.')
    print('Previous manual baseline entries are NOT used.')
    print('\nJOB DESCRIPTION\n' + '=' * 60)
    print(JOB.read_text(encoding='utf-8-sig'))
    print('=' * 60)
    print(f'Existing completed reviews: {len(records)}')
    for path in resumes:
        cid = candidate_id(path)
        if cid in reviewed:
            continue
        print(f'\nNEXT: {cid} ({path.name})')
        input('Press ENTER when ready to begin a real manual review...')
        started = time.perf_counter()
        print('\n' + '=' * 60)
        print(path.read_text(encoding='utf-8-sig'))
        print('=' * 60)
        status = prompt_choice('Your screening decision:', REVIEW_STATUSES)
        experience = prompt_choice('Your experience assessment:', EXPERIENCE_STATUSES)
        matched = input('Matched required skills (comma-separated; blank if none): ').strip()
        missing = input('Missing required skills (comma-separated; blank if none): ').strip()
        notes = prompt_required('Evidence notes (cite resume text or uncertainty)')
        duration = round(time.perf_counter() - started, 2)
        row = {
            'candidate_id': cid, 'filename': path.name,
            'review_status': status, 'experience_status': experience,
            'matched_skills': matched, 'missing_required_skills': missing,
            'evidence_notes': notes, 'duration_seconds': duration,
            'reviewed_at_utc': datetime.now(timezone.utc).isoformat(),
        }
        records.append(row)
        save_records(records)
        SUMMARY.write_text(json.dumps(summarize(records, len(resumes)), indent=2), encoding='utf-8')
        print(f'Saved {cid}: {duration:.2f} seconds. Completed {len(records)}/{len(resumes)}.')
        if len(records) < len(resumes) and input('Continue? [Y/n]: ').strip().lower() == 'n':
            break
    report = summarize(records, len(resumes))
    print('\nSUMMARY\n' + json.dumps(report, indent=2))
    print(f'CSV: {OUTPUT}\nJSON: {SUMMARY}')
    if not report['complete']:
        print('INCOMPLETE: rerun the same command to resume.')


if __name__ == '__main__':
    try:
        run()
    except (ValueError, OSError, EOFError, KeyboardInterrupt) as exc:
        print(f'\nStopped: {exc}', file=sys.stderr)
        sys.exit(1)
