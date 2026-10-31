"""Offline, read-only final submission audit for RecruitFlow AI.

Run: python evaluation/final_submission_audit.py
Exit codes: 0 = automated checks passed; 1 = blockers found.
Does not commit, upload, delete, or alter project files other than its two reports.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'app.py', 'README.md', '.gitignore', 'run_batch.py',
    'src/schemas.py', 'src/matching_engine.py', 'src/review_generator.py',
    'src/database.py', 'data/resumes/candidate_01.txt',
    'docs/24_professional_case_study.md',
    'docs/25_ai_collaboration_note.md',
    'docs/26_documentation_guide.md',
    'docs/27_five_minute_demo_script.md',
    'docs/28_demo_recording_and_backup_plan.md',
    'evaluation/09_genuine_baseline_summary.json',
    'evaluation/10_automated_benchmark_summary.json',
    'evaluation/12_accuracy_summary.json',
    'evaluation/15_performance_comparison.json',
    'evaluation/17_final_evaluation_summary.json',
    'evaluation/18_final_evaluation_report.md',
]
IGNORED_SENSITIVE = ['.env', '.venv/test.txt', 'candidate_data.db', 'outputs/demo/recording.mp4']
DEMO_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.webm'}
SECRET_PATTERNS = [
    ('private_key', re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')),
    ('github_token', re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b')),
    ('openai_key', re.compile(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b')),
    ('aws_access_key', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('generic_assignment', re.compile(r'(?im)^\s*(?:api[_-]?key|secret[_-]?key|password|access[_-]?token)\s*[:=]\s*["\']?([^\s"\']{12,})')),
]
SCANNABLE = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.csv', '.sh', '.bat', '.ps1', '.env'}
EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'node_modules', 'dist', 'build'}


def git_command(root: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True, timeout=15, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def git_paths(root: Path, *args: str) -> list[str] | None:
    try:
        result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=15, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return [p.decode('utf-8', errors='replace') for p in result.stdout.split(b'\0') if p]


def check_ignore(root: Path) -> dict[str, Any]:
    p = root / '.gitignore'
    if not p.is_file():
        return {'status': 'fail', 'details': ['.gitignore missing']}
    contents = p.read_text(encoding='utf-8')
    mandatory = ['.venv/', '.env', '*.db', '*.sqlite3', 'outputs/demo/*.mp4']
    missing = [x for x in mandatory if x not in contents]
    git = git_command(root, '--version')
    if git is None or git.returncode != 0:
        return {'status': 'fail' if missing else 'manual', 'details': ['Git unavailable; ignore behavior not verified'] + missing}
    repo = git_command(root, 'rev-parse', '--is-inside-work-tree')
    if repo is None or repo.returncode != 0:
        return {'status': 'fail' if missing else 'manual', 'details': ['Git repository not initialized; ignore patterns need behavioral verification'] + missing}
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore",
         "--no-index", "-z", "--stdin"],
        input=("\0".join(IGNORED_SENSITIVE) + "\0").encode("utf-8"),
        capture_output=True,
        timeout=15,
    )

    found = {
        path.decode("utf-8", errors="replace")
        for path in result.stdout.split(b"\0")
        if path
    }
    unignored = [x for x in IGNORED_SENSITIVE if x not in found]
    issues = [f'Missing pattern: {x}' for x in missing] + [f'Not ignored: {x}' for x in unignored]
    return {'status': 'fail' if issues else 'pass', 'details': issues or ['Git ignore patterns verified']}


def scan_secrets(root: Path) -> dict[str, Any]:
    """Scan candidate publication files; ignore excluded local files and report artifacts."""
    paths = git_paths(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z')
    scope = 'git_tracked_and_untracked_nonignored' if paths is not None else 'filesystem_fallback'
    if paths is None:
        paths = [str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*') if p.is_file() and not any(x in EXCLUDE_DIRS for x in p.relative_to(root).parts)]
    findings: list[dict[str, Any]] = []
    inspected = 0
    for relative in sorted(set(paths)):
        p = root / relative
        if not p.is_file() or p.is_symlink() or p.suffix.lower() not in SCANNABLE or p.stat().st_size > 1_000_000:
            continue
        if relative in {'evaluation/19_submission_audit.json', 'evaluation/20_submission_audit.md'}:
            continue
        inspected += 1
        try:
            content = p.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        for kind, regex in SECRET_PATTERNS:
            for match in regex.finditer(content):
                # Never write actual secret values into the audit output.
                line_number = content.count('\n', 0, match.start()) + 1
                # This exact test fixture deliberately contains a dummy private-key header.
                # Exempt only the literal in that test's write_text call, not the whole test file.
                line_text = content.splitlines()[line_number - 1]
                if (relative.replace('\\', '/') == 'tests/test_final_submission_day5.py'
                        and kind == 'private_key'
                        and 'write_text(' in line_text
                        and 'BEGIN PRIVATE KEY' in line_text):
                    continue
                findings.append({'file': relative, 'line': line_number, 'type': kind})
    return {'status': 'fail' if findings else 'pass', 'scope': scope, 'files_inspected': inspected, 'findings': findings,
            'caution': 'Pattern scan is not comprehensive; manually inspect staged files and Git history.'}


def check_git(root: Path) -> dict[str, Any]:
    # Do not accept a Git repository inherited from a parent directory.
    if not (root / '.git').exists():
        return {'status': 'manual', 'details': 'Git repository not initialized in project directory'}
    result = git_command(root, 'rev-parse', '--is-inside-work-tree')
    if result is None:
        return {'status': 'manual', 'details': 'Git not installed or not accessible'}
    if result.returncode != 0 or result.stdout.strip() != 'true':
        return {'status': 'manual', 'details': 'Git repository not initialized; run git init when ready'}
    staged = git_paths(root, 'diff', '--cached', '--name-only', '-z') or []
    tracked = git_paths(root, 'ls-files', '-z') or []
    bad = [p for p in set(staged + tracked) if p.startswith(('.venv/', 'venv/')) or p == '.env' or p.endswith(('.db', '.sqlite', '.sqlite3', '.pem', '.key', '.p12', '.pfx')) or (p.startswith('outputs/demo/') and Path(p).suffix.lower() in DEMO_EXTENSIONS)]
    return {'status': 'fail' if bad else 'pass', 'tracked_count': len(tracked), 'staged_count': len(staged),
            'sensitive_tracked_or_staged': sorted(bad), 'details': 'Review git status and git diff --cached before publishing.'}


def validate_metrics(root: Path) -> dict[str, Any]:
    names = [
        "09_genuine_baseline_summary.json",
        "10_automated_benchmark_summary.json",
        "12_accuracy_summary.json",
        "17_final_evaluation_summary.json",
    ]

    try:
        manual, auto, accuracy, final = [
            json.loads((root / "evaluation" / name).read_text(encoding="utf-8"))
            for name in names
        ]

        problems = []

        def expect(ok: bool, message: str) -> None:
            if not ok:
                problems.append(message)

        baseline = final.get("manual_baseline", {})
        benchmark = final.get("automated_benchmark", {})
        status = final.get("reference_agreement", {}).get("status", {})
        disagreements = final.get("disagreements", {})
        timing = final.get("timing", {})

        manual_seconds = float(baseline.get("total_seconds", -1))
        automated_seconds = float(benchmark.get("mean_batch_seconds", -1))
        agreement_percent = float(
            status.get("automated", {}).get("agreement_percent", -1)
        )

        expect(final.get("candidate_count") == 10,
               "Final candidate count not 10")
        expect(abs(manual_seconds - 153.16) < 0.01,
               "Manual total differs from verified 153.16s")
        expect(abs(automated_seconds - 0.003918) < 0.000001,
               "Automated batch mean differs from verified 0.003918s")
        expect(abs(agreement_percent - 80.0) < 0.01,
               "Status agreement differs from 80%")
        expect(disagreements.get("candidate_count") == 10,
               "Disagreement candidate count differs from 10")
        expect(
            timing.get("end_to_end_recruiter_time_savings_percent") is None,
            "End-to-end savings must be null"
        )
        expect(abs(float(manual.get("total_seconds", -1)) - manual_seconds) < 0.01,
               "Manual and final summaries differ")
        expect(
            abs(float(auto.get("total_seconds_mean", -1)) - automated_seconds)
            < 0.000001,
            "Benchmark and final summaries differ"
        )

        return {
            "status": "fail" if problems else "pass",
            "details": problems or [
                "Final metrics agree with benchmark and baseline; "
                "synthetic reference limitations remain"
            ],
        }

    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "details": [
                f"Metric files could not be validated: {type(exc).__name__}"
            ],
        }


def audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    missing = [name for name in REQUIRED if not (root / name).is_file()]
    resume_count = len(list((root / 'data' / 'resumes').glob('candidate_*.txt')))
    if resume_count != 10:
        missing.append(f'Expected 10 synthetic candidate TXT resumes, found {resume_count}')
    demo_dir = root / 'outputs' / 'demo'
    videos = [p.relative_to(root).as_posix() for p in demo_dir.iterdir() if p.is_file() and p.suffix.lower() in DEMO_EXTENSIONS] if demo_dir.is_dir() else []
    checks = {
        'required_files': {'status': 'fail' if missing else 'pass', 'details': missing or ['All required files present'], 'synthetic_resumes': resume_count},
        'evaluation_metrics': validate_metrics(root),
        'gitignore': check_ignore(root),
        'secret_patterns': scan_secrets(root),
        'git_repository': check_git(root),
        'recorded_demo': {'status': 'manual', 'files_found': videos, 'details': 'Check actual duration, audio, playback, synthetic data and content; recording may be stored elsewhere.'},
        'test_suite': {'status': 'manual', 'details': 'Run python -m pytest tests -q; paste output for confirmation.'},
        'submission_review': {'status': 'manual', 'details': 'Confirm repository URL/access, staged files, no secrets in history, and final handoff requirements.'},
    }
    failures = [name for name, result in checks.items() if result['status'] == 'fail']
    manual = [name for name, result in checks.items() if result['status'] == 'manual']
    return {'project': 'RecruitFlow AI', 'audit_version': 1, 'automated_checks_passed': not failures,
            'ready_to_submit': False, 'blocking_checks': failures, 'manual_checks_remaining': manual, 'checks': checks}


def render_markdown(report: dict[str, Any]) -> str:
    lines = ['# RecruitFlow AI — Final Submission Audit', '', 'This audit is not proof of publication or final submission.', '',
             '| Check | Status |', '|---|---|']
    for name, result in report['checks'].items():
        lines.append(f"| {name.replace('_', ' ').title()} | {result['status'].upper()} |")
    lines += ['', '## Blocking checks', '', *(f'- {x}' for x in report['blocking_checks']), '',
              '## Manual checks remaining', '', *(f'- {x}' for x in report['manual_checks_remaining']), '',
              '## Notes', '', '- No files were uploaded or committed by this audit.',
              '- Automated secret detection is incomplete; inspect all staged content and commit history.',
              '- Local processing speed is not end-to-end recruiter time savings.',
              '- Synthetic reference agreement is not production hiring accuracy.', '']
    return '\n'.join(lines)


def main() -> int:
    report = audit(ROOT)
    output = ROOT / 'evaluation'
    output.mkdir(exist_ok=True)
    (output / '19_submission_audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (output / '20_submission_audit.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({'automated_checks_passed': report['automated_checks_passed'],
                      'blocking_checks': report['blocking_checks'], 'manual_checks_remaining': report['manual_checks_remaining'],
                      'ready_to_submit': False,
                      'reports': ['evaluation/19_submission_audit.json', 'evaluation/20_submission_audit.md']}, indent=2))
    return 1 if report['blocking_checks'] else 0


if __name__ == '__main__':
    raise SystemExit(main())