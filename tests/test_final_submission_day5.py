"""Final submission audit tests; use temporary isolated project fixtures."""
import importlib.util
import json
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[1] / 'evaluation' / 'final_submission_audit.py'
spec = importlib.util.spec_from_file_location('final_submission_audit', SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def root(tmp_path):
    for name in module.REQUIRED:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('sample', encoding='utf-8')
    for n in range(1, 11):
        p = tmp_path / 'data' / 'resumes' / f'candidate_{n:02}.txt'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('synthetic', encoding='utf-8')
    (tmp_path / '.gitignore').write_text('.venv/\n.env\n*.db\n*.sqlite3\noutputs/demo/*.mp4\n', encoding='utf-8')
    data = {
        '09_genuine_baseline_summary.json': {'total_seconds': 153.16},
        '10_automated_benchmark_summary.json': {'total_seconds_mean': 0.003918},
        '12_accuracy_summary.json': {},
        '17_final_evaluation_summary.json': {
            'candidate_count': 10,
            'manual_baseline': {'total_seconds': 153.16},
            'automated_benchmark': {'mean_batch_seconds': 0.003918},
            'reference_agreement': {'status': {'automated': {'agreement_percent': 80.0}}},
            'disagreements': {'candidate_count': 10},
            'timing': {'end_to_end_recruiter_time_savings_percent': None},
        },
    }
    for name, value in data.items():
        (tmp_path / 'evaluation' / name).write_text(json.dumps(value), encoding='utf-8')
    return tmp_path


def test_required_paths_present(root):
    assert module.audit(root)['checks']['required_files']['status'] == 'pass'


def test_missing_file_blocked(root):
    (root / 'app.py').unlink()
    assert 'required_files' in module.audit(root)['blocking_checks']


def test_ten_synthetic_resumes(root):
    assert module.audit(root)['checks']['required_files']['synthetic_resumes'] == 10


def test_missing_resume_blocked(root):
    (root / 'data/resumes/candidate_10.txt').unlink()
    assert 'required_files' in module.audit(root)['blocking_checks']


def test_metrics_pass(root):
    assert module.validate_metrics(root)['status'] == 'pass'


def test_bad_manual_time(root):
    p = root / 'evaluation/17_final_evaluation_summary.json'
    data = json.loads(p.read_text())
    data['manual_baseline']['total_seconds'] = 100
    p.write_text(json.dumps(data))
    assert module.validate_metrics(root)['status'] == 'fail'


def test_false_savings_blocked(root):
    p = root / 'evaluation/17_final_evaluation_summary.json'
    data = json.loads(p.read_text())
    data['timing']['end_to_end_recruiter_time_savings_percent'] = 99
    p.write_text(json.dumps(data))
    assert module.validate_metrics(root)['status'] == 'fail'


def test_wrong_candidate_count(root):
    p = root / 'evaluation/17_final_evaluation_summary.json'
    data = json.loads(p.read_text())
    data['candidate_count'] = 9
    p.write_text(json.dumps(data))
    assert module.validate_metrics(root)['status'] == 'fail'


def test_invalid_json_blocked(root):
    (root / 'evaluation/17_final_evaluation_summary.json').write_text('{bad')
    assert module.validate_metrics(root)['status'] == 'fail'


def test_secret_scan_clean(root):
    assert module.scan_secrets(root)['status'] == 'pass'


def test_private_key_detected_without_exposing_value(root):
    (root / 'app.py').write_text('-----BEGIN PRIVATE KEY-----\nSECRETSECRETSECRET')
    result = module.scan_secrets(root)
    assert result['status'] == 'fail'
    assert result['findings'][0]['type'] == 'private_key'
    assert 'SECRETSECRET' not in str(result)


def test_github_token_detected(root):
    (root / 'app.py').write_text('token = ghp_' + 'A' * 30)
    assert module.scan_secrets(root)['status'] == 'fail'


def test_aws_key_detected(root):
    (root / 'app.py').write_text('AKIA' + 'A' * 16)
    assert module.scan_secrets(root)['status'] == 'fail'


def test_password_assignment_detected(root):
    (root / 'app.py').write_text('password = "not_a_real_example_password"')
    assert module.scan_secrets(root)['status'] == 'fail'


def test_no_secret_values_in_markdown(root):
    result = module.audit(root)
    assert 'ready_to_submit' in result
    assert not result['ready_to_submit']
    assert 'Manual checks remaining' in module.render_markdown(result)


def test_demo_always_requires_manual_review(root):
    assert module.audit(root)['checks']['recorded_demo']['status'] == 'manual'


def test_demo_video_found(root):
    p = root / 'outputs/demo/test.mp4'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'not a real video')
    assert module.audit(root)['checks']['recorded_demo']['files_found'] == ['outputs/demo/test.mp4']


def test_git_not_initialized_is_manual(root):
    assert module.check_git(root)['status'] == 'manual'


def test_no_gitignore_is_failure(root):
    (root / '.gitignore').unlink()
    assert module.check_ignore(root)['status'] == 'fail'


def test_missing_gitignore_pattern_is_failure(root):
    (root / '.gitignore').write_text('.venv/\n')
    assert module.check_ignore(root)['status'] == 'fail'


def test_no_upload_or_commit_functions():
    source = SOURCE.read_text()
    assert 'git push' not in source
    assert 'git commit' not in source


def test_readme_documentation_exists():
    assert (SOURCE.parents[1] / 'docs' / '29_final_submission_guide.md').exists()


def test_report_is_plain_markdown(root):
    report = module.audit(root)
    markdown = module.render_markdown(report)
    assert markdown.startswith('# RecruitFlow AI')
    assert 'Synthetic reference agreement' in markdown


def test_audit_never_claims_ready(root):
    assert module.audit(root)['ready_to_submit'] is False