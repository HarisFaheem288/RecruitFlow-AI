"""Tests for Day 4 Task 5; do not depend on the user's actual evaluation files."""
import csv
import importlib.util
import json
import math
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / 'evaluation' / 'generate_final_evaluation.py'
spec = importlib.util.spec_from_file_location('day4_final_evaluation', MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def inputs():
    n = 10
    manual = {'baseline_type':'timed_independent_human_review','complete':True,'reviewed_count':n,'expected_count':n,'total_seconds':153.16}
    benchmark = {'benchmark_type':'automated_document_extraction_and_screening','resume_count':n,'failed_files':0,'measured_runs':10,'candidate_ids':[f'C{i:02}' for i in range(1,11)],'total_seconds_mean':0.003918}
    vals = {'manual_status':5,'automated_status':8,'manual_experience':2,'automated_experience':9,'manual_missing_skills':1,'automated_missing_skills':10}
    accuracy = {'evaluation_type':'agreement_with_synthetic_reference_expectations','candidate_count':n,'candidates_with_any_disagreement':10,'manual_evidence_notes_present':10,'automated_evidence_notes_present':10,'metrics':{k:{'matches':v,'total':n,'agreement_percent':v*10.0} for k,v in vals.items()}}
    comparison = {'comparison_type':'day4_measured_stage_comparison','candidate_count':n,'manual':{'total_seconds':153.16},'automated':{'mean_batch_seconds':0.003918},'timing_comparison':{'scopes_equivalent':False,'end_to_end_recruiter_time_savings_percent':None,'manual_to_automated_measured_stage_ratio':round(153.16/0.003918,2)},'reference_agreement':{key:{actor:{'agreement_percent':vals[f'{actor}_{key}']*10.0} for actor in ('manual','automated')} for key in ('status','experience','missing_skills')}}
    rows = [{'candidate_id':f'C{i:02}', 'disagreement_flags':'manual_status; manual_experience'} for i in range(1,11)]
    return manual, benchmark, accuracy, comparison, rows


def build():
    m,b,a,c,r=inputs()
    return mod.build_report(m,b,a,c,r,{'manual_status':10,'manual_experience':10})


def test_report_type(): assert build()['report_type']=='recruitflow_day4_final_evaluation'
def test_candidate_count(): assert build()['candidate_count']==10
def test_manual_time(): assert build()['manual_baseline']['total_seconds']==153.16
def test_automated_time(): assert build()['automated_benchmark']['mean_batch_seconds']==0.003918
def test_ratio(): assert build()['timing']['measured_stage_ratio']==39091.37
def test_no_end_to_end_claim(): assert build()['timing']['end_to_end_recruiter_time_savings_percent'] is None
def test_manual_status_agreement(): assert build()['reference_agreement']['status']['manual']['agreement_percent']==50
def test_automated_status_agreement(): assert build()['reference_agreement']['status']['automated']['agreement_percent']==80
def test_missing_skills_agreement(): assert build()['reference_agreement']['missing_skills']['automated']['agreement_percent']==100
def test_evidence_quality_not_verified(): assert build()['evidence_note_presence']['factual_quality_verified'] is False
def test_markdown_has_limitations(): assert '## Limitations' in mod.render_markdown(build())
def test_markdown_rejects_speedup(): assert 'not a validated workflow speedup' in mod.render_markdown(build())

def test_reject_incomplete_manual():
    m,b,a,c,r=inputs(); m['complete']=False
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_reject_candidate_mismatch():
    m,b,a,c,r=inputs(); b['resume_count']=9
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_reject_failed_files():
    m,b,a,c,r=inputs(); b['failed_files']=1
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_reject_invalid_accuracy():
    m,b,a,c,r=inputs(); a['metrics']['automated_status']['agreement_percent']=99
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_reject_end_to_end_claim():
    m,b,a,c,r=inputs(); c['timing_comparison']['end_to_end_recruiter_time_savings_percent']=99
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_reject_bad_ratio():
    m,b,a,c,r=inputs(); c['timing_comparison']['manual_to_automated_measured_stage_ratio']=100
    with pytest.raises(mod.EvaluationReportError): mod.build_report(m,b,a,c,r,{})

def test_nonfinite_number_rejected():
    with pytest.raises(mod.EvaluationReportError): mod.number(math.nan,'value')

def test_read_disagreements(tmp_path):
    p=tmp_path/'disagreements.csv'
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['candidate_id','disagreement_flags']);w.writeheader()
        w.writerow({'candidate_id':'C01','disagreement_flags':'manual_status; automated_status'})
    rows,flags=mod.read_disagreements(p,{'C01','C02'})
    assert len(rows)==1 and flags['manual_status']==1 and flags['automated_status']==1

def test_duplicate_disagreement_ids_rejected(tmp_path):
    p=tmp_path/'disagreements.csv'
    p.write_text('candidate_id,disagreement_flags\nC01,manual_status\nC01,automated_status\n',encoding='utf-8')
    with pytest.raises(mod.EvaluationReportError): mod.read_disagreements(p,{'C01'})

def test_json_loading_rejects_array(tmp_path):
    p=tmp_path/'invalid.json';p.write_text('[]',encoding='utf-8')
    with pytest.raises(mod.EvaluationReportError): mod.load_object(p)

def test_generation_writes_both_files(tmp_path):
    m,b,a,c,r=inputs()
    paths=[tmp_path/x for x in ('manual.json','benchmark.json','accuracy.json','comparison.json')]
    for p,data in zip(paths,(m,b,a,c)): p.write_text(json.dumps(data),encoding='utf-8')
    csvpath=tmp_path/'disagreements.csv'
    with csvpath.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['candidate_id','disagreement_flags']);w.writeheader();w.writerows(r)
    jp,mp=tmp_path/'out.json',tmp_path/'out.md'
    result=mod.generate(*paths,csvpath,jp,mp)
    assert json.loads(jp.read_text(encoding='utf-8'))['candidate_count']==10
    assert '# RecruitFlow AI' in mp.read_text(encoding='utf-8')
    assert result['timing']['end_to_end_recruiter_time_savings_percent'] is None
