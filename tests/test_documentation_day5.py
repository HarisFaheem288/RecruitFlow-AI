"""Documentation-only checks; no application implementation changes required."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'
GUIDE = ROOT / 'docs' / '26_documentation_guide.md'


def test_readme_exists():
    assert README.is_file()


def test_guide_exists():
    assert GUIDE.is_file()


def test_readme_has_title():
    assert README.read_text(encoding='utf-8').startswith('# RecruitFlow AI')


def test_readme_documents_setup():
    s = README.read_text(encoding='utf-8')
    assert 'venv' in s and 'Windows CMD' in s


def test_readme_documents_app_command():
    assert 'python -m streamlit run app.py' in README.read_text(encoding='utf-8')


def test_readme_documents_test_command():
    assert 'python -m pytest tests -q' in README.read_text(encoding='utf-8')


def test_readme_documents_human_oversight():
    assert 'human' in README.read_text(encoding='utf-8').lower()


def test_readme_documents_synthetic_data():
    assert 'synthetic' in README.read_text(encoding='utf-8').lower()


def test_readme_avoids_end_to_end_savings_claim():
    s = README.read_text(encoding='utf-8').lower()
    assert 'not' in s and 'end-to-end' in s


def test_readme_has_no_unverified_dependency_file_claim():
    s = README.read_text(encoding='utf-8')
    assert 'if one is present' in s


def test_readme_has_expected_metrics():
    s = README.read_text(encoding='utf-8')
    for v in ('153.16', '0.003918', '80%', '90%', '100%'):
        assert v in s


def test_readme_links_to_case_study():
    assert 'docs/24_professional_case_study.md' in README.read_text(encoding='utf-8')


def test_readme_links_to_collaboration_note():
    assert 'docs/25_ai_collaboration_note.md' in README.read_text(encoding='utf-8')


def test_readme_links_to_guide():
    assert 'docs/26_documentation_guide.md' in README.read_text(encoding='utf-8')


def test_guide_has_all_nine_sections():
    s = GUIDE.read_text(encoding='utf-8')
    for n in range(1, 10):
        assert re.search(rf'^## {n}\. ', s, re.M)


def test_guide_mentions_evaluation_sources():
    s = GUIDE.read_text(encoding='utf-8')
    for n in ('09_genuine_baseline_summary.json', '10_automated_benchmark_summary.json',
              '12_accuracy_summary.json', '17_final_evaluation_summary.json'):
        assert n in s


def test_guide_has_publication_checklist():
    assert 'Repository publication checklist' in GUIDE.read_text(encoding='utf-8')


def test_guide_mentions_scope_limitations():
    s = GUIDE.read_text(encoding='utf-8')
    assert 'not equivalent end-to-end' in s.lower()


def test_readme_code_fences_balanced():
    assert README.read_text(encoding='utf-8').count('```') % 2 == 0


def test_guide_code_fences_balanced():
    assert GUIDE.read_text(encoding='utf-8').count('```') % 2 == 0
