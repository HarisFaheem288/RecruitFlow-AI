# RecruitFlow AI — Demo Recording and Backup Plan

## 1. Windows setup

Open **Command Prompt** and execute:

```cmd
cd /d D:\RecruitFlow-AI
.venv\Scripts\activate.bat
python -m pytest tests -q
python -m streamlit run app.py
```

The app should open in a browser. If Streamlit prints a local URL, open that URL. Do not assume a fixed port.

Open a second CMD window if you need to inspect project files without stopping the app.

## 2. Prepare the demo workspace

1. Open `README.md` in VS Code.
2. Open `evaluation\18_final_evaluation_report.md` in VS Code.
3. Open the running Streamlit app in a browser.
4. Keep `data\resumes\` ready if the UI supports local resume uploads.
5. Verify the demonstration job and saved review data exist in the app.
6. Identify one example with clear evidence and one needing review.
7. Avoid destructive changes to saved human decisions during the recording.

## 3. Recording method

Use a screen recorder already installed on your computer (for example, Windows Snipping Tool screen recording, Xbox Game Bar where supported, or OBS Studio). Capture the application window and microphone. Recording is a manual step; the project does not generate a video automatically.

Suggested filename: `RecruitFlow_AI_5_Minute_Demo.mp4`.

Suggested local folder: `D:\RecruitFlow-AI\outputs\demo\`.

## 4. Timing and rehearsal

Use the time-coded script in `docs\27_five_minute_demo_script.md`. Rehearse once with a stopwatch. Keep a short pause for app loading. If the workflow takes longer than expected, show previously saved reviews and explicitly say they were generated earlier.

## 5. Backup if the live application fails

- **App will not start:** Capture the error for later debugging; use the README, project structure, final evaluation report, and passing test output for a narrated backup walkthrough. Do not claim the UI is currently working if it is not.
- **Upload or screening takes too long:** Use existing saved candidate reviews; say they were previously generated.
- **Human audit entry unavailable:** Explain the feature and show its code/tests; do not invent a reviewer action.
- **Evaluation file missing:** Do not quote numbers from memory; regenerate or verify from existing JSON files before recording.
- **Recording stops:** Restart from the beginning or make a clearly disclosed edited recording, depending on submission rules.

## 6. Demo evidence checklist

- [ ] 215 or more tests passing on the current project state.
- [ ] Ten synthetic resumes, not real applicants.
- [ ] Structured screening output visible.
- [ ] Human review and audit functionality explained accurately.
- [ ] Timing comparison explicitly marked as different-scope measurements.
- [ ] Synthetic-reference agreement described without a production accuracy claim.
- [ ] Video played back locally with audible narration.

## 7. What this task does not verify

The documentation tests validate the script and preparation files only. They cannot verify that a video was recorded, that the UI controls match the walkthrough, that the voiceover lasted five minutes, or that the submitted video is playable. Those require manual verification.
