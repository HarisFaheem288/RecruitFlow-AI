"""Day 4 Task 4: transparent comparison of manual and automated screening.

Run from project root:
    python evaluation/compare_performance_day4.py
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANUAL = PROJECT_ROOT / 'evaluation' / '09_genuine_baseline_summary.json'
DEFAULT_AUTOMATED = PROJECT_ROOT / 'evaluation' / '10_automated_benchmark_summary.json'
DEFAULT_ACCURACY = PROJECT_ROOT / 'evaluation' / '12_accuracy_summary.json'
DEFAULT_JSON = PROJECT_ROOT / 'evaluation' / '15_performance_comparison.json'
DEFAULT_MARKDOWN = PROJECT_ROOT / 'evaluation' / '16_performance_comparison.md'


class ComparisonError(ValueError):
    """Input files are missing, malformed, or not comparable."""


def load_json(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    try:
        with path.open('r', encoding='utf-8') as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ComparisonError(f'Cannot read valid JSON from {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise ComparisonError(f'Expected JSON object in {path}')
    return value


def positive_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ComparisonError(f'{label} must be a positive number')
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ComparisonError(f'{label} must be a finite positive number')
    return number


def nonnegative_integer(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ComparisonError(f'{label} must be a nonnegative integer')
    return value


def validate_agreement_metric(metrics: dict[str, Any], key: str, expected: int) -> dict[str, Any]:
    metric = metrics.get(key)
    if not isinstance(metric, dict):
        raise ComparisonError(f'Missing accuracy metric: {key}')
    matches = nonnegative_integer(metric.get('matches'), f'{key}.matches')
    total = nonnegative_integer(metric.get('total'), f'{key}.total')
    if total != expected or matches > total:
        raise ComparisonError(f'{key} must describe the same {expected} candidates')
    percent = metric.get('agreement_percent')
    if isinstance(percent, bool) or not isinstance(percent, (int, float)) or not math.isfinite(percent):
        raise ComparisonError(f'{key}.agreement_percent is invalid')
    calculated = 100 * matches / total
    if abs(float(percent) - calculated) > 0.11:
        raise ComparisonError(f'{key}.agreement_percent conflicts with matches/total')
    return {'matches': matches, 'total': total, 'agreement_percent': round(calculated, 2)}


def build_comparison(manual: dict[str, Any], automated: dict[str, Any], accuracy: dict[str, Any]) -> dict[str, Any]:
    if manual.get('baseline_type') != 'timed_independent_human_review':
        raise ComparisonError('Manual input is not the genuine timed baseline')
    if manual.get('complete') is not True:
        raise ComparisonError('Manual baseline is incomplete')
    if automated.get('benchmark_type') != 'automated_document_extraction_and_screening':
        raise ComparisonError('Unexpected automated benchmark type')
    if accuracy.get('evaluation_type') != 'agreement_with_synthetic_reference_expectations':
        raise ComparisonError('Unexpected accuracy evaluation type')

    count = nonnegative_integer(manual.get('reviewed_count'), 'manual.reviewed_count')
    expected = nonnegative_integer(manual.get('expected_count'), 'manual.expected_count')
    auto_count = nonnegative_integer(automated.get('resume_count'), 'automated.resume_count')
    accuracy_count = nonnegative_integer(accuracy.get('candidate_count'), 'accuracy.candidate_count')
    if count == 0 or count != expected or count != auto_count or count != accuracy_count:
        raise ComparisonError('All three evaluations must use the same nonzero candidate count')
    if nonnegative_integer(automated.get('failed_files'), 'automated.failed_files') != 0:
        raise ComparisonError('Automated benchmark contains failed files')
    if nonnegative_integer(automated.get('measured_runs'), 'automated.measured_runs') == 0:
        raise ComparisonError('Automated benchmark has no measured runs')
    candidate_ids = automated.get('candidate_ids')
    if not isinstance(candidate_ids, list) or len(candidate_ids) != count or len(set(candidate_ids)) != count or not all(isinstance(x, str) and x.strip() for x in candidate_ids):
        raise ComparisonError('Automated candidate IDs are missing, duplicated, or invalid')

    manual_seconds = positive_number(manual.get('total_seconds'), 'manual.total_seconds')
    auto_seconds = positive_number(automated.get('total_seconds_mean'), 'automated.total_seconds_mean')
    recorded_avg = positive_number(manual.get('average_seconds'), 'manual.average_seconds')
    if abs(recorded_avg - manual_seconds / count) > 0.02:
        raise ComparisonError('Manual average does not match total/count')
    recorded_auto_avg = positive_number(automated.get('seconds_per_resume_mean'), 'automated.seconds_per_resume_mean')
    if abs(recorded_auto_avg - auto_seconds / count) > 0.000002:
        raise ComparisonError('Automated per-resume mean does not match batch mean/count')

    metrics = accuracy.get('metrics')
    if not isinstance(metrics, dict):
        raise ComparisonError('Accuracy metrics are missing')
    metric_names = ('status', 'experience', 'missing_skills')
    agreement = {}
    for name in metric_names:
        human = validate_agreement_metric(metrics, f'manual_{name}', count)
        machine = validate_agreement_metric(metrics, f'automated_{name}', count)
        agreement[name] = {
            'manual': human,
            'automated': machine,
            'difference_percentage_points': round(machine['agreement_percent'] - human['agreement_percent'], 2),
        }

    return {
        'comparison_type': 'day4_measured_stage_comparison',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_count': count,
        'manual': {
            'measurement_scope': 'Self-recorded independent human review of synthetic resumes',
            'total_seconds': round(manual_seconds, 6),
            'seconds_per_resume': round(manual_seconds / count, 6),
            'independently_observed': False,
        },
        'automated': {
            'measurement_scope': automated.get('scope', 'Local document extraction and rule-based screening only'),
            'mean_batch_seconds': round(auto_seconds, 6),
            'mean_seconds_per_resume': round(auto_seconds / count, 9),
            'measured_runs': automated['measured_runs'],
            'failed_files': 0,
        },
        'timing_comparison': {
            'manual_to_automated_measured_stage_ratio': round(manual_seconds / auto_seconds, 2),
            'scopes_equivalent': False,
            'end_to_end_recruiter_time_savings_percent': None,
            'explanation': 'The ratio compares different measurement scopes and is not a validated end-to-end recruiter productivity gain.',
        },
        'reference_agreement': agreement,
        'limitations': [
            'Ten synthetic resumes; findings are not representative of production recruiting.',
            'Reference expectations are not independently adjudicated ground truth.',
            'Manual review times and decisions are self-recorded, not independently observed.',
            'Automated timings exclude upload, UI, database writes, exports, human verification and approval.',
            'Repeated local benchmark runs may benefit from OS caches and warm-up effects.',
            'Evidence-note presence is not proof of evidence quality; human inspection is required.',
            'No end-to-end time savings percentage is claimed.',
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    manual = report['manual']
    auto = report['automated']
    ratio = report['timing_comparison']['manual_to_automated_measured_stage_ratio']
    lines = [
        '# RecruitFlow AI — Day 4 Performance Comparison', '',
        f"**Candidates:** {report['candidate_count']} synthetic resumes", '',
        '## Measured timing', '',
        '| Measurement | Manual review | Automated extraction + screening |',
        '|---|---:|---:|',
        f"| Total / mean batch time (seconds) | {manual['total_seconds']:.3f} | {auto['mean_batch_seconds']:.6f} |",
        f"| Mean per resume (seconds) | {manual['seconds_per_resume']:.3f} | {auto['mean_seconds_per_resume']:.6f} |",
        '',
        f'**Measured-stage time ratio:** {ratio:,.2f}:1 (manual time / automated batch time).',
        '',
        '**This is not an end-to-end productivity or time-saving claim.** The measurement scopes differ. '
        'Automated time excludes UI, upload, storage, exports and human verification.',
        '', '## Agreement with synthetic reference expectations', '',
        '| Category | Manual agreement | Automated agreement | Difference (percentage points) |',
        '|---|---:|---:|---:|',
    ]
    for key, label in [('status', 'Screening status'), ('experience', 'Experience'), ('missing_skills', 'Missing required skills')]:
        metric = report['reference_agreement'][key]
        lines.append(f"| {label} | {metric['manual']['agreement_percent']:.1f}% | {metric['automated']['agreement_percent']:.1f}% | {metric['difference_percentage_points']:+.1f} |")
    lines.extend(['', '## Limitations', ''])
    lines.extend(f'- {item}' for item in report['limitations'])
    lines.extend(['', '## Interpretation', '',
                  'On this synthetic dataset, the rule-based screening pipeline had higher reference agreement '
                  'than the self-recorded manual baseline. These observations do not establish real-world '
                  'accuracy, fairness or recruiter productivity. An end-to-end timed workflow study and '
                  'independent review of reference labels are needed for stronger claims.', ''])
    return '\n'.join(lines)


def write_reports(report: dict[str, Any], json_path: str | Path, markdown_path: str | Path) -> None:
    json_path = Path(json_path)
    markdown_path = Path(markdown_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    markdown_path.write_text(render_markdown(report), encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manual', type=Path, default=DEFAULT_MANUAL)
    parser.add_argument('--automated', type=Path, default=DEFAULT_AUTOMATED)
    parser.add_argument('--accuracy', type=Path, default=DEFAULT_ACCURACY)
    parser.add_argument('--json-output', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--markdown-output', type=Path, default=DEFAULT_MARKDOWN)
    args = parser.parse_args(argv)
    try:
        report = build_comparison(load_json(args.manual), load_json(args.automated), load_json(args.accuracy))
        write_reports(report, args.json_output, args.markdown_output)
    except ComparisonError as exc:
        parser.exit(1, f'Comparison failed: {exc}\n')
    print(json.dumps({
        'candidate_count': report['candidate_count'],
        'manual_total_seconds': report['manual']['total_seconds'],
        'automated_mean_batch_seconds': report['automated']['mean_batch_seconds'],
        'measured_stage_ratio': report['timing_comparison']['manual_to_automated_measured_stage_ratio'],
        'end_to_end_time_savings': None,
        'agreement_percent': {name: {'manual': values['manual']['agreement_percent'], 'automated': values['automated']['agreement_percent']} for name, values in report['reference_agreement'].items()},
        'output_files': [str(args.json_output), str(args.markdown_output)],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
