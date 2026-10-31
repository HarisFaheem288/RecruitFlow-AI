"""Generate Day 4 final evaluation from verified Task 1–4 JSON/CSV files.

Run from project root: python evaluation/generate_final_evaluation.py
This script never changes inputs, source resumes, or the SQLite database.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / 'evaluation'
MANUAL = EVAL / '09_genuine_baseline_summary.json'
BENCHMARK = EVAL / '10_automated_benchmark_summary.json'
ACCURACY = EVAL / '12_accuracy_summary.json'
COMPARISON = EVAL / '15_performance_comparison.json'
DISAGREEMENTS = EVAL / '14_disagreements.csv'
OUTPUT_JSON = EVAL / '17_final_evaluation_summary.json'
OUTPUT_MD = EVAL / '18_final_evaluation_report.md'

class EvaluationReportError(ValueError):
    """Required evaluation evidence is missing or inconsistent."""


def load_object(path: Path) -> dict[str, Any]:
    try:
        with path.open('r', encoding='utf-8-sig') as file:
            obj = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationReportError(f'Unable to read {path}: {exc}') from exc
    if not isinstance(obj, dict):
        raise EvaluationReportError(f'{path.name} must contain a JSON object')
    return obj


def number(value: Any, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvaluationReportError(f'{label} must be numeric')
    result = float(value)
    if not math.isfinite(result) or (positive and result <= 0):
        raise EvaluationReportError(f'{label} must be finite' + (' and positive' if positive else ''))
    return result


def count(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EvaluationReportError(f'{label} must be a nonnegative integer')
    return value


def read_disagreements(path: Path, expected_ids: set[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    try:
        with path.open('r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)
            fields = set(reader.fieldnames or [])
            required = {'candidate_id', 'disagreement_flags'}
            if not required <= fields:
                raise EvaluationReportError(f'{path.name} missing columns: {sorted(required-fields)}')
            rows = list(reader)
    except OSError as exc:
        raise EvaluationReportError(f'Unable to read {path}: {exc}') from exc
    ids = [row['candidate_id'].strip() for row in rows]
    if any(not x for x in ids) or len(ids) != len(set(ids)):
        raise EvaluationReportError('Disagreement CSV contains blank or duplicate candidate IDs')
    if not set(ids) <= expected_ids:
        raise EvaluationReportError('Disagreement CSV contains candidates absent from benchmark')
    flags = Counter()
    for row in rows:
        values = [x.strip() for x in row['disagreement_flags'].split(';') if x.strip()]
        if not values:
            raise EvaluationReportError('Disagreement CSV contains a row with no disagreement flags')
        flags.update(set(values))
    return rows, dict(sorted(flags.items()))


def build_report(manual: dict, benchmark: dict, accuracy: dict, comparison: dict,
                 disagreements: list[dict], flag_counts: dict[str, int]) -> dict:
    if manual.get('baseline_type') != 'timed_independent_human_review' or manual.get('complete') is not True:
        raise EvaluationReportError('Genuine manual baseline is missing or incomplete')
    if benchmark.get('benchmark_type') != 'automated_document_extraction_and_screening':
        raise EvaluationReportError('Unexpected benchmark type')
    if accuracy.get('evaluation_type') != 'agreement_with_synthetic_reference_expectations':
        raise EvaluationReportError('Unexpected accuracy evaluation type')
    if comparison.get('comparison_type') != 'day4_measured_stage_comparison':
        raise EvaluationReportError('Unexpected performance comparison type')
    n = count(manual.get('reviewed_count'), 'manual.reviewed_count')
    if n == 0 or any(count(v, name) != n for name, v in (
        ('manual.expected_count', manual.get('expected_count')),
        ('benchmark.resume_count', benchmark.get('resume_count')),
        ('accuracy.candidate_count', accuracy.get('candidate_count')),
        ('comparison.candidate_count', comparison.get('candidate_count')))):
        raise EvaluationReportError('All sources must cover the same nonzero number of candidates')
    if count(benchmark.get('failed_files'), 'benchmark.failed_files') != 0:
        raise EvaluationReportError('Automated benchmark has failed files')
    if count(benchmark.get('measured_runs'), 'benchmark.measured_runs') < 1:
        raise EvaluationReportError('Automated benchmark has no measured runs')
    ids = benchmark.get('candidate_ids')
    if not isinstance(ids, list) or len(ids) != n or len(set(ids)) != n or not all(isinstance(x, str) and x.strip() for x in ids):
        raise EvaluationReportError('Benchmark candidate IDs are invalid')
    if len(disagreements) != count(accuracy.get('candidates_with_any_disagreement'), 'accuracy.disagreement_count'):
        raise EvaluationReportError('Disagreement CSV count differs from accuracy summary')
    if any(v > len(disagreements) for v in flag_counts.values()):
        raise EvaluationReportError('Disagreement flag count exceeds number of disagreements')

    manual_time = number(manual.get('total_seconds'), 'manual.total_seconds', positive=True)
    auto_time = number(benchmark.get('total_seconds_mean'), 'benchmark.total_seconds_mean', positive=True)
    time_info = comparison.get('timing_comparison')
    if not isinstance(time_info, dict) or time_info.get('scopes_equivalent') is not False or time_info.get('end_to_end_recruiter_time_savings_percent') is not None:
        raise EvaluationReportError('Comparison must explicitly reject an end-to-end savings claim')
    if abs(number(comparison.get('manual', {}).get('total_seconds'), 'comparison.manual.total_seconds') - manual_time) > 0.02:
        raise EvaluationReportError('Manual timing differs across sources')
    if abs(number(comparison.get('automated', {}).get('mean_batch_seconds'), 'comparison.automated.mean_batch_seconds') - auto_time) > 0.000002:
        raise EvaluationReportError('Automated timing differs across sources')
    if abs(number(time_info.get('manual_to_automated_measured_stage_ratio'), 'comparison.ratio') - manual_time / auto_time) > 0.05:
        raise EvaluationReportError('Measured-stage ratio is inconsistent')

    metrics = accuracy.get('metrics')
    if not isinstance(metrics, dict):
        raise EvaluationReportError('Accuracy metrics missing')
    agreement = {}
    for key in ('status', 'experience', 'missing_skills'):
        agreement[key] = {}
        for actor in ('manual', 'automated'):
            label = f'{actor}_{key}'
            metric = metrics.get(label)
            if not isinstance(metric, dict):
                raise EvaluationReportError(f'Missing metric: {label}')
            matches = count(metric.get('matches'), f'{label}.matches')
            total = count(metric.get('total'), f'{label}.total')
            if total != n or matches > n:
                raise EvaluationReportError(f'Invalid metric counts: {label}')
            pct = number(metric.get('agreement_percent'), f'{label}.agreement_percent')
            if abs(pct - 100 * matches / n) > 0.11:
                raise EvaluationReportError(f'Invalid metric percentage: {label}')
            prior = comparison.get('reference_agreement', {}).get(key, {}).get(actor, {})
            if not isinstance(prior, dict) or abs(number(prior.get('agreement_percent'), f'comparison.{label}') - pct) > 0.11:
                raise EvaluationReportError(f'Accuracy and comparison disagree: {label}')
            agreement[key][actor] = {'matches': matches, 'total': n, 'agreement_percent': round(100*matches/n, 2)}
    return {
        'report_type': 'recruitflow_day4_final_evaluation',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'candidate_count': n,
        'test_suite_last_reported': '172 passed (user-reported Day 4 Task 4; rerun tests to verify current state)',
        'manual_baseline': {'total_seconds': manual_time, 'average_seconds': round(manual_time/n, 3), 'self_recorded': True},
        'automated_benchmark': {'mean_batch_seconds': auto_time, 'measured_runs': benchmark['measured_runs'], 'failed_files': 0},
        'timing': {'measured_stage_ratio': round(manual_time/auto_time, 2), 'scopes_equivalent': False, 'end_to_end_recruiter_time_savings_percent': None},
        'reference_agreement': agreement,
        'disagreements': {'candidate_count': len(disagreements), 'candidate_ids': [r['candidate_id'] for r in disagreements], 'flag_counts': flag_counts},
        'evidence_note_presence': {'manual': count(accuracy.get('manual_evidence_notes_present'), 'manual.evidence_notes'), 'automated': count(accuracy.get('automated_evidence_notes_present'), 'automated.evidence_notes'), 'factual_quality_verified': False},
        'recommendations': [
            'Manually inspect all disagreement cases, especially automated screening-status mismatches.',
            'Verify evidence notes against the original resume text; presence alone is insufficient.',
            'Measure complete upload-to-human-approval time before claiming recruiter time savings.',
            'Evaluate on more diverse, consented and appropriately de-identified resumes before production use.',
            'Retain human oversight and audit history; do not auto-hire or auto-reject.'
        ],
        'limitations': [
            'Only ten synthetic resumes; reference expectations are not independently adjudicated ground truth.',
            'Manual baseline is self-recorded and not independently observed.',
            'Automated time excludes upload, UI, storage, export, corrections and human approval.',
            'Local repeated runs may benefit from caches; measured stages are not equivalent.',
            'Evidence-note presence is not evidence factuality, fairness or reliability.',
            'No end-to-end recruiter time-savings percentage is established.'
        ],
        'source_files': [str(x.relative_to(ROOT)).replace('\\', '/') for x in (MANUAL, BENCHMARK, ACCURACY, COMPARISON, DISAGREEMENTS)]
    }


def render_markdown(report: dict) -> str:
    n = report['candidate_count']
    lines = [
        '# RecruitFlow AI — Day 4 Final Evaluation Report', '',
        f"**Generated (UTC):** {report['generated_at_utc']}",
        f'**Dataset:** {n} synthetic resumes for one Junior AI/ML Engineer job', '',
        '## Executive summary', '',
        f"The independent, self-recorded manual baseline took **{report['manual_baseline']['total_seconds']:.2f} seconds** for {n} reviews. "
        f"The local automated extraction and rule-based screening pipeline averaged **{report['automated_benchmark']['mean_batch_seconds']:.6f} seconds** per batch across "
        f"{report['automated_benchmark']['measured_runs']} measured runs. These are **different scopes**, not an end-to-end time-savings comparison.", '',
        '## Timing and scope', '',
        '| Measurement | Value |', '|---|---:|',
        f"| Manual review total | {report['manual_baseline']['total_seconds']:.2f} sec |",
        f"| Manual review average | {report['manual_baseline']['average_seconds']:.3f} sec/resume |",
        f"| Automated mean batch | {report['automated_benchmark']['mean_batch_seconds']:.6f} sec |",
        f"| Measured-stage ratio | {report['timing']['measured_stage_ratio']:,.2f}:1 |",
        '| End-to-end recruiter time savings | Not established |', '',
        '**Interpretation:** The ratio is a comparison of non-equivalent stages, not a validated workflow speedup.', '',
        '## Agreement with synthetic reference expectations', '',
        '| Dimension | Manual | Automated |', '|---|---:|---:|'
    ]
    for key, label in [('status', 'Screening status'), ('experience', 'Experience classification'), ('missing_skills', 'Missing required skills (exact set)')]:
        metric = report['reference_agreement'][key]
        lines.append(f"| {label} | {metric['manual']['agreement_percent']:.1f}% ({metric['manual']['matches']}/{n}) | {metric['automated']['agreement_percent']:.1f}% ({metric['automated']['matches']}/{n}) |")
    lines += ['', 'These are reference-agreement rates, **not independently validated real-world accuracy**.', '',
              '## Disagreements and evidence', '',
              f"**Candidates with one or more disagreement flags:** {report['disagreements']['candidate_count']}/{n}.", '',
              '**Flag frequencies:**', '']
    lines.extend(f'- `{flag}`: {count}' for flag, count in report['disagreements']['flag_counts'].items())
    lines += ['', f"Evidence notes present: manual {report['evidence_note_presence']['manual']}/{n}; automated {report['evidence_note_presence']['automated']}/{n}. "
              'These counts do not verify whether the notes are factually supported by resumes.', '',
              '## Recommendations', '']
    lines.extend(f'- {item}' for item in report['recommendations'])
    lines += ['', '## Limitations', '']
    lines.extend(f'- {item}' for item in report['limitations'])
    lines += ['', '## Source files', '']
    lines.extend(f'- `{item}`' for item in report['source_files'])
    lines += ['', '## Conclusion', '',
              'The rule-based prototype demonstrates fast local processing and higher agreement with synthetic scenario expectations than the recorded manual baseline. '
              'This small study does not establish production accuracy, fairness or end-to-end recruiter time savings. '
              'Human verification and a broader evaluation are required before deployment.', '']
    return '\n'.join(lines)


def generate(manual_path=MANUAL, benchmark_path=BENCHMARK, accuracy_path=ACCURACY,
             comparison_path=COMPARISON, disagreements_path=DISAGREEMENTS,
             output_json=OUTPUT_JSON, output_md=OUTPUT_MD) -> dict:
    manual = load_object(Path(manual_path))
    benchmark = load_object(Path(benchmark_path))
    accuracy = load_object(Path(accuracy_path))
    comparison = load_object(Path(comparison_path))
    ids = benchmark.get('candidate_ids')
    if not isinstance(ids, list) or not all(isinstance(x, str) for x in ids):
        raise EvaluationReportError('Benchmark candidate IDs missing')
    rows, flags = read_disagreements(Path(disagreements_path), set(ids))
    report = build_report(manual, benchmark, accuracy, comparison, rows, flags)
    json_path, md_path = Path(output_json), Path(output_md)
    if json_path.resolve() == md_path.resolve():
        raise EvaluationReportError('Output JSON and Markdown paths must differ')
    for path in (json_path, md_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
    md_path.write_text(render_markdown(report), encoding='utf-8')
    return report


def main() -> int:
    try:
        report = generate()
    except (EvaluationReportError, OSError, TypeError, KeyError) as exc:
        print(f'Final evaluation failed: {exc}', file=sys.stderr)
        return 1
    print(json.dumps({'candidate_count': report['candidate_count'],
                      'manual_total_seconds': report['manual_baseline']['total_seconds'],
                      'automated_mean_batch_seconds': report['automated_benchmark']['mean_batch_seconds'],
                      'automated_status_agreement_percent': report['reference_agreement']['status']['automated']['agreement_percent'],
                      'disagreement_candidates': report['disagreements']['candidate_count'],
                      'end_to_end_time_savings': report['timing']['end_to_end_recruiter_time_savings_percent'],
                      'output_files': [str(OUTPUT_JSON), str(OUTPUT_MD)]}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
