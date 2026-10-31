"""Documentation checks for Day 5 Task 4; no application state is modified."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'docs' / '27_five_minute_demo_script.md'
BACKUP = ROOT / 'docs' / '28_demo_recording_and_backup_plan.md'


def read(path):
    return path.read_text(encoding='utf-8')


def test_script_exists(): assert SCRIPT.is_file()
def test_backup_exists(): assert BACKUP.is_file()
def test_script_title(): assert 'Five-Minute Demo Script' in read(SCRIPT)
def test_script_has_six_segments(): assert len(re.findall(r'^## [1-6]\. ', read(SCRIPT), re.M)) == 6
def test_script_start(): assert '0:00–0:35' in read(SCRIPT)
def test_script_finish(): assert '4:30–5:00' in read(SCRIPT)
def test_script_timing_total():
    intervals = re.findall(r'^## [1-6]\. .*?\((\d+) seconds\)$', read(SCRIPT), re.M)
    assert list(map(int, intervals)) == [35,40,90,45,60,30]
    assert sum(map(int, intervals)) == 300

def test_synthetic_data_disclosure(): assert 'synthetic' in read(SCRIPT).lower()
def test_manual_baseline(): assert '153.16' in read(SCRIPT)
def test_automated_timing(): assert '0.003918' in read(SCRIPT)
def test_status_agreement(): assert '80 percent' in read(SCRIPT)
def test_tests_count(): assert '215 passing' in read(SCRIPT)
def test_no_end_to_end_savings_claim(): assert 'do not claim an end-to-end recruiter time saving' in read(SCRIPT)
def test_manual_timing_disclosure(): assert 'self-recorded' in read(SCRIPT)
def test_human_oversight(): assert 'human' in read(SCRIPT).lower() and 'audit' in read(SCRIPT).lower()
def test_app_command(): assert 'python -m streamlit run app.py' in read(BACKUP)
def test_test_command(): assert 'python -m pytest tests -q' in read(BACKUP)
def test_windows_path(): assert r'D:\RecruitFlow-AI' in read(BACKUP)
def test_backup_plan(): assert 'Backup if the live application fails' in read(BACKUP)
def test_recording_manual_verification(): assert 'cannot verify that a video was recorded' in read(BACKUP)
def test_code_fences_balanced(): assert read(BACKUP).count('```') % 2 == 0
