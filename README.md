# Air Force Opponent Tempo Intelligence Agent

CS471 core checkpoint: a fixed HMM estimates FAST/CONTROLLED opponent tempo and predicts the next QUICK possession. Categories: QUICK 1–12 seconds, NORMAL 13–22, LONG 23–60. Examples are synthetic; team names are display-only. The **MODEL-IMPLIED DEMO REFERENCE** is 0.35: forecasts at least 0.45 are HIGH QUICK-RISK, at most 0.25 are LOW QUICK-RISK, otherwise NEAR BASELINE.

## Setup and execute

Use Python **3.10+** and Git. No extra packages or data are needed. This private repository requires GitHub access. For a new checkout:

```bash
git clone https://github.com/the-lmoney/CS471---Basketball-HMM.git
cd CS471---Basketball-HMM
```

From the project folder, run (use `python3` if that is your Python command):

```bash
python -m tempo_scout demo --team "UC Davis" --sequence QUICK,NORMAL,LONG,QUICK
python -m tempo_scout demo --team "Nevada" --sequence QUICK,QUICK,QUICK
python -m tempo_scout demo --team "Wyoming" --sequence LONG,LONG,LONG
python -m unittest discover -s tests -v
```

Verified: **30 tests passed, 0 failed**. First QUICK gives FAST = 6/7 and next QUICK = 16/35, checking conditioning and forecasting; QUICK,NORMAL gives FAST = 5/7, checking transition timing. Final next-QUICK forecasts: UC Davis **0.424662**, Nevada **0.485195**, Wyoming **0.214805**. Edit `tempo_scout/hmm.py` for the model, `scouting.py` for alerts, `__main__.py` for the CLI, and `tests/test_hmm.py` for checks.

## Document work here

**the-lmoney (HMM/CLI):** [completed work, files/commits, review]. **SeniAkinola (verification/docs):** [completed work, files/commits, review]. Completed checkpoint: fixed HMM, demonstrations, tests. **Challenges and resolutions:** [fill in]. **Remaining checkpoint work and next responsibilities:** [fill in; confirm instructor access]. Future work: historical data, possession parsing, model training, Brier-score evaluation, and ten-team reports.

## AI assistance

Codex generated the HMM, validation, filtering, forecasting, alerts, CLI, and 30 tests; independently checked numerical expectations; executed demonstrations and tests, including a fresh-checkout check; drafted and consolidated documentation; resolved local Python/Git setup issues; committed and pushed changes; and opened VS Code. The current human edits were preserved in Git history before consolidation. Record each teammate's actual work and review above. The full project, training, and historical-data features remain deferred.
