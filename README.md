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

**the-lmoney (HMM/CLI):** HMM: Defined FAST/CONTROLLED states and QUICK/NORMAL/LONG observations using the approved fixed probabilities; validated dimensions, ranges, and probability sums.
Filtering: Updated state beliefs after each observation, normalized them, and applied transitions only between observations.
Forecasting: Applied one additional transition, then combined QUICK emission probabilities to predict the next possession. 

**SeniAkinola (verification/docs):** Alerts: Compared forecasts against the model-implied 0.35 reference: HIGH at ≥0.45, LOW at ≤0.25, otherwise NEAR BASELINE.
CLI: Added team/sequence arguments, readable probability tables, synthetic-data labels, final interpretations, and clear input errors.

**Challenges:** The main challenges were updating the model’s probabilities in the correct order, checking our calculations against independently calculated answers, handling invalid inputs without crashing, and making sure rounding did not cause incorrect alerts near the cutoff values.

 **Remaining checkpoint work and next responsibilities:** To complete our final project, we still need to move beyond the basic Hidden Markov Model (HMM) demonstration and implement it using real basketball data. This includes collecting and cleaning historical possession data for all ten Mountain West teams, training the HMM to recognize different offensive tempos, and testing how accurately it predicts the next possession. We also need to compare our predictions against each team's average pace using Brier scores to measure accuracy. Finally, we plan to create clear scouting reports that show each team's tempo patterns, predictions, and useful insights for Air Force coaches.

## AI assistance

Both Lucas and Seni collabored on this project for both design and implementation. We heavily leveraged Codex as well to assist us throughout the project. We would explain the conceptuals of what we needed and Codex would build out the implementation of our ideas. We also leveraged Codex for assistance with the ReadMe file, unit testing, and more.
