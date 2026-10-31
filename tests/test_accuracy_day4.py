"""Tests for Day 4 Task 3; run from project root with pytest."""
import csv
import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / 'evaluation' / 'evaluate_accuracy_day4.py'
spec = importlib.util.spec_from_file_location('accuracy_day4', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixtures():
    reference = {'C01': {'candidate_id':'C01', 'expected_status':'Meets requirements', 'experience_status':'Meets', 'missing_required_skills':'None'},
                 'C02': {'candidate_id':'C02', 'expected_status':'Missing requirements', 'experience_status':'Below minimum', 'missing_required_skills':'SQL; Pandas'}}
    manual = {'C01': {'candidate_id':'C01', 'review_status':'Meets requirements', 'experience_status':'Meets', 'missing_required_skills':'', 'evidence_notes':'Python used', 'duration_seconds':'10'},
              'C02': {'candidate_id':'C02', 'review_status':'Meets requirements', 'experience_status':'Below minimum', 'missing_required_skills':'SQL', 'evidence_notes':'Experience 0.5 years', 'duration_seconds':'12'}}
    automated = {'C01': {'candidate_id':'C01', 'review_status':'Meets requirements', 'experience_status':'Meets', 'missing_required_skills':[], 'evidence_notes':'Python listed'},
                 'C02': {'candidate_id':'C02', 'review_status':'Missing requirements', 'experience_status':'Unknown', 'missing_required_skills':['Pandas','SQL'], 'evidence_notes':'No claim'}}
    return reference, manual, automated


def test_skill_delimiters():
    assert module.parse_skills('SQL; Pandas, Python') == {'sql','pandas','python'}


def test_skill_case_insensitive():
    assert module.parse_skills(['SQL', 'sql']) == {'sql'}


def test_none_means_empty():
    assert module.parse_skills('None') == set()


def test_empty_skills():
    assert module.parse_skills('') == set()


def test_bad_skill_input():
    with pytest.raises(ValueError): module.parse_skills(None)


def test_percent():
    assert module.percent(1, 2) == 50.0


def test_percent_zero():
    assert module.percent(0, 0) == 0.0


def test_metrics():
    summary, rows, errors = module.evaluate(*fixtures())
    assert summary['metrics']['manual_status']['agreement_percent'] == 50
    assert summary['metrics']['automated_status']['agreement_percent'] == 100
    assert summary['metrics']['automated_experience']['agreement_percent'] == 50
    assert summary['metrics']['manual_missing_skills']['agreement_percent'] == 50
    assert summary['metrics']['automated_missing_skills']['agreement_percent'] == 100
    assert len(rows) == 2 and len(errors) == 1


def test_disagreement_flags():
    _, _, disagreements = module.evaluate(*fixtures())
    assert 'manual_status' in disagreements[0]['disagreement_flags']
    assert 'automated_experience' in disagreements[0]['disagreement_flags']
    assert 'manual_vs_automated_status' in disagreements[0]['disagreement_flags']


def test_candidate_id_mismatch():
    reference, manual, auto = fixtures()
    del manual['C02']
    with pytest.raises(ValueError, match='Candidate IDs differ'): module.evaluate(reference, manual, auto)


def test_invalid_status():
    reference, manual, auto = fixtures()
    auto['C01']['review_status'] = 'Hired'
    with pytest.raises(ValueError, match='Invalid automated review status'): module.evaluate(reference, manual, auto)


def test_blank_evidence():
    reference, manual, auto = fixtures()
    manual['C01']['evidence_notes'] = ''
    with pytest.raises(ValueError, match='Missing manual evidence'): module.evaluate(reference, manual, auto)


def test_duplicate_csv_ids(tmp_path):
    path = tmp_path / 'duplicate.csv'
    path.write_text('candidate_id,expected_status,missing_required_skills,experience_status\nC01,Meets requirements,None,Meets\nC01,Meets requirements,None,Meets\n', encoding='utf-8')
    with pytest.raises(ValueError, match='duplicate'): module.read_csv(path, module.REQUIRED_REFERENCE)


def test_missing_csv_column(tmp_path):
    path = tmp_path / 'bad.csv'
    path.write_text('candidate_id\nC01\n', encoding='utf-8')
    with pytest.raises(ValueError, match='Missing required CSV columns'): module.read_csv(path, module.REQUIRED_REFERENCE)


def test_export_csv_empty_disagreements(tmp_path):
    path = tmp_path / 'disagreements.csv'
    module.write_csv(path, [], ['candidate_id','disagreement_flags'])
    with path.open(encoding='utf-8-sig', newline='') as handle:
        assert list(csv.DictReader(handle)) == []


def test_csv_formula_guard(tmp_path):
    path = tmp_path / 'data.csv'
    module.write_csv(path, [{'candidate_id':'C01', 'scenario':'=1+1'}], ['candidate_id','scenario'])
    with path.open(encoding='utf-8-sig', newline='') as handle:
        assert next(csv.DictReader(handle))['scenario'] == "'=1+1"
