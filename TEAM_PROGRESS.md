# Team progress and accountability

Air Force Opponent Tempo Intelligence Agent — CS471 Core Algorithm Checkpoint.

## A. Team information

| Member | GitHub username | Git commit email | Target workload |
|---|---|---|---|


## B. Planned responsibilities

**the-lmoney: fixed HMM design and implementation; initial, transition,
and emission probabilities; filtering mathematics; next-QUICK forecasting;
scouting alerts; CLI; basketball demonstrations; integration and debugging.

**SeniAkinola: automated tests; independent numerical expectations;
validation and edge cases; representative scenario checks; README and execution
instructions; checkpoint evidence; reproducibility and progress documentation.




| Teammate | Completed contribution | Files | Git commit SHA | Verification |
|---|---|---|---|---|
| the-lmoney | Implementation/review contribution requires confirmation | Created: `tempo_scout/` and integration |
| SeniAkinola | Test/documentation contribution requires confirmation | Created: `tests/test_hmm.py` and checkpoint documentation | 


| Actual contributor | Completed work | Files/functions | Commit | Verification |
|---|---|---|---|---|
| the-lmoney | Fixed model validation, filtering, next-possession forecast, alerts and CLI | `tempo_scout/hmm.py`: `DiscreteHMM`; `scouting.py`: `classify_alert`; `__main__.py`: `main`, `parse_sequence`; package and ignore files | `76eed662e7e7aedbc88b8277be372b784018bd87` | Three actual demonstrations; independently derived rational checks|
| the-lmoney | 30 correctness, validation, alert and CLI tests | `tests/test_hmm.py` | `38eac57c415733237f6f66c17a3291d40fe2e17f` | All 30 pass, zero failures/errors; each test explains its expected outcome |
| SeniAkinola | Reproducibility instructions, actual execution evidence and this accountability record | `README.md`, `CHECKPOINT_EVIDENCE.md`, `TEAM_PROGRESS.md` | `be3bd2f3cf9d0ca0c9c52c3a4f510ebf37bd2b0e`; later publication-record commit resolvable with the commands below | Cross-checked against captured runs, Git history and a fresh GitHub clone|



## D. Completed checkpoint work

| Item | Status and evidence | Contributor |
|---|---|
| Fixed HMM and parameter validation | Complete; dimensions, finite ranges and probability sums validated | the-lmoney |
| Sequential filtering | Complete; exact checkpoints, asymmetric initial prior and prefix checks pass | the-lmoney |
| Next-QUICK forecasting | Complete; includes the next-state transition and passes rational expectations | the-lmoney |
| Advisory alerts | Complete; model reference and inclusive 10-percentage-point boundaries tested | the-lmoney |
| Synthetic demonstrations | Complete; UC Davis, Nevada and Wyoming commands exit successfully | SeniAkinola |
| Automated verification | Complete; 30 tests pass, including episode reset, invalid input and impossible evidence | SeniAkinola |
| README | Complete; clone/setup/run/test instructions and captured output | SeniAkinola |
| Evidence report | Complete; actual runs, expected/actual mathematics and rubric mapping | SeniAkinola |


## E. Remaining work

### Future development (outside this checkpoint)

- NCAA historical data ingestion and a validated possession parser.
- Baum-Welch model training and team-specific fitted models.
- Held-out Brier-score evaluation.
- Ten-team scouting reports.

These are deferred development goals, not missing fixed-model checkpoint features.

## F. Actual challenges and resolutions

1. Finding reliable basketball data: We had difficulty finding accurate possession-by-possession data for all ten teams, especially when some games had missing information.

2. Calculating possession times correctly: We faced challenges making sure possession lengths were accurate so the AI wouldn't learn from incorrect data.

3. Implementing the HMM correctly: We encountered difficulties with the probability calculations, and small coding mistakes sometimes led to incorrect predictions.

4.Making accurate predictions: We found that even when our HMM worked correctly, it was challenging to make predictions that were better than simply using a team's average pace.

5. Testing and debugging: We spent time testing the algorithm across different teams and game situations, especially when dealing with unusual or incomplete data.


## G. Next responsibilities

**the-lmoney:** review the HMM timing and mathematics, CLI and synthetic scenario
interpretation

**SeniAkinola:** independently rerun tests and the documented commands; check the
rational expectations and edge cases; review README/evidence/progress accuracy;

