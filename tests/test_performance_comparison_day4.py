"""Day 4 Task 4 tests. Run: python -m pytest tests/test_performance_comparison_day4.py -v"""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / 'evaluation' / 'compare_performance_day4.py'
spec = importlib.util.spec_from_file_location('compare_performance_day4', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixtures():
    manual = {'baseline_type': 'timed_independent_human_review', 'reviewed_count': 10, 'expected_count': 10, 'complete': True, 'total_seconds': 153.16, 'average_seconds': 15.32}
    automated = {'benchmark_type': 'automated_document_extraction_and_screening', 'resume_count': 10, 'candidate_ids': [f'C{i:02}' for i in range(1, 11)], 'failed_files': 0, 'measured_runs': 10, 'total_seconds_mean': .003918, 'seconds_per_resume_mean': .000392, 'scope': 'Local batch only'}
    accuracy = {'evaluation_type': 'agreement_with_synthetic_reference_expectations', 'candidate_count': 10, 'metrics': {}}
    for category, man, auto in [('status', 5, 8), ('experience', 2, 9), ('missing_skills', 1, 10)]:
        accuracy['metrics'][f'manual_{category}'] = {'matches': man, 'total': 10, 'agreement_percent': 10 * man}
        accuracy['metrics'][f'automated_{category}'] = {'matches': auto, 'total': 10, 'agreement_percent': 10 * auto}
    return manual, automated, accuracy


def test_build_report_candidate_count():
    assert module.build_comparison(*fixtures())['candidate_count'] == 10


def test_manual_seconds():
    assert module.build_comparison(*fixtures())['manual']['total_seconds'] == 153.16


def test_automated_seconds():
    assert module.build_comparison(*fixtures())['automated']['mean_batch_seconds'] == .003918


def test_no_end_to_end_claim():
    report = module.build_comparison(*fixtures())
    assert report['timing_comparison']['end_to_end_recruiter_time_savings_percent'] is None
    assert report['timing_comparison']['scopes_equivalent'] is False


def test_ratio_is_positive():
    assert module.build_comparison(*fixtures())['timing_comparison']['manual_to_automated_measured_stage_ratio'] > 1


def test_accuracy_difference():
    assert module.build_comparison(*fixtures())['reference_agreement']['status']['difference_percentage_points'] == 30


def test_incomplete_manual_rejected():
    m, a, c = fixtures()
    m['complete'] = False
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_arbitrary_baseline_rejected():
    m, a, c = fixtures()
    m['baseline_type'] = 'manual_timer_guess'
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_mismatched_counts_rejected():
    m, a, c = fixtures()
    a['resume_count'] = 9
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_failed_files_rejected():
    m, a, c = fixtures()
    a['failed_files'] = 1
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_zero_time_rejected():
    m, a, c = fixtures()
    a['total_seconds_mean'] = 0
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_duplicate_candidate_ids_rejected():
    m, a, c = fixtures()
    a['candidate_ids'][1] = 'C01'
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_inconsistent_agreement_rejected():
    m, a, c = fixtures()
    c['metrics']['manual_status']['agreement_percent'] = 90
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)


def test_markdown_includes_disclaimer():
    md = module.render_markdown(module.build_comparison(*fixtures()))
    assert 'not an end-to-end productivity' in md
    assert 'Screening status' in md


def test_write_reports(tmp_path):
    report = module.build_comparison(*fixtures())
    json_path = tmp_path / 'a' / 'comparison.json'
    md_path = tmp_path / 'b' / 'comparison.md'
    module.write_reports(report, json_path, md_path)
    assert json.loads(json_path.read_text(encoding='utf-8'))['candidate_count'] == 10
    assert '# RecruitFlow AI' in md_path.read_text(encoding='utf-8')


def test_load_json_invalid(tmp_path):
    p = tmp_path / 'bad.json'
    p.write_text('{bad json', encoding='utf-8')
    with pytest.raises(module.ComparisonError):
        module.load_json(p)


def test_cli_custom_paths(tmp_path, capsys):
    m, a, c = fixtures()
    paths = [tmp_path / x for x in ('manual.json', 'auto.json', 'accuracy.json')]
    for path, data in zip(paths, (m, a, c)):
        path.write_text(json.dumps(data), encoding='utf-8')
    out_json = tmp_path / 'out.json'
    out_md = tmp_path / 'out.md'
    assert module.main(['--manual', str(paths[0]), '--automated', str(paths[1]), '--accuracy', str(paths[2]), '--json-output', str(out_json), '--markdown-output', str(out_md)]) == 0
    assert out_json.exists() and out_md.exists()
    assert 'candidate_count' in capsys.readouterr().out


def test_manual_average_inconsistent_rejected():
    m, a, c = fixtures()
    m['average_seconds'] = 45.49
    with pytest.raises(module.ComparisonError):
        module.build_comparison(m, a, c)
