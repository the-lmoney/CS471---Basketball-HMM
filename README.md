# Air Force Opponent Tempo Intelligence Agent

**CS471 — Artificial Intelligence: Core Algorithm Checkpoint**

This project demonstrates a two-state, three-symbol discrete Hidden Markov
Model (HMM) for basketball opponent scouting. Given observed possession-duration
categories, it estimates whether an opponent is operating in an unobserved
**FAST** or **CONTROLLED** tempo mode, then forecasts the probability that the
opponent's **next possession** will be **QUICK**.

The intended application is opponent preparation for Air Force men's basketball.
This checkpoint uses fixed proposal parameters and synthetic examples. Team names
are display labels: selecting UC Davis, Nevada, or Wyoming does not load team data
or change the model. The outputs are advisory model estimates, not measured team
rates or evidence about the causal effect of a defensive strategy.

## Implemented checkpoint

- Validated, immutable HMM parameters.
- Sequential forward filtering with a normalized posterior after every observation.
- Separate next-possession QUICK forecasting and scouting alert classification.
- Terminal demonstrations and clear input errors.
- Thirty automated tests, including mathematical, validation, and CLI checks.
- [Checkpoint evidence](CHECKPOINT_EVIDENCE.md) and [team progress](TEAM_PROGRESS.md).

This is the core algorithm checkpoint, not the full final capstone.

## Model and observation categories

Hidden-state order: `[FAST, CONTROLLED]`.
Observation-column order: `[QUICK, NORMAL, LONG]`.

| Observation | Possession duration |
|---|---|
| QUICK | 1–12 seconds |
| NORMAL | 13–22 seconds |
| LONG | 23–60 seconds |

The CLI accepts these categories directly; it does not parse raw durations or
historical play-by-play records.

Initial distribution: `pi = [0.50, 0.50]`.

Transition matrix `A[i,j] = P(next state j | current state i)`:

| Current state | Next FAST | Next CONTROLLED |
|---|---:|---:|
| FAST | 0.80 | 0.20 |
| CONTROLLED | 0.20 | 0.80 |

Emission matrix `B[j,o] = P(observation o | state j)`:

| State | QUICK | NORMAL | LONG |
|---|---:|---:|---:|
| FAST | 0.60 | 0.30 | 0.10 |
| CONTROLLED | 0.10 | 0.30 | 0.60 |

All vectors and matrix rows must have the correct dimensions, finite entries in
`[0,1]`, and sums equal to one within an absolute tolerance of `1e-12`. Supplied
lists are copied to tuples so later caller changes cannot alter a validated model.

## Filtering and forecasting mathematics

Let `b_t(j)` be the posterior probability of state `j` after observations
`o_1, ..., o_t`. For the **first** observation, update the initial distribution
directly, without applying a transition:

```text
w_1(j) = pi(j) * B[j,o_1]
b_1(j) = w_1(j) / sum_k w_1(k)
```

For each subsequent observation, predict the current state from the previous
posterior, then condition on the new observation:

```text
predicted_t(j) = sum_i b_(t-1)(i) * A[i,j]
w_t(j)        = predicted_t(j) * B[j,o_t]
b_t(j)        = w_t(j) / sum_k w_t(k)
```

Every update is normalized separately. A zero or nonfinite normalization is
rejected with `ValueError`. Earlier posteriors use only observations up to their
own step; appending future observations does not revise those beliefs. Every
`filter_sequence` call begins a fresh episode from `pi`.

To forecast the **next** possession after observation `t`, apply one more
transition before combining the QUICK emissions:

```text
next_state(j) = sum_i b_t(i) * A[i,j]
P(next QUICK) = sum_j next_state(j) * B[j,QUICK]
```

For these fixed parameters, the forecast also simplifies to
`0.20 + 0.30 * P(FAST)`. That expression is useful for independent checking; the
implementation computes the matrix-based prediction. It does not substitute
hardcoded scenario results.

### Scouting alerts

The **MODEL-IMPLIED DEMO REFERENCE** is
`0.50 * 0.60 + 0.50 * 0.10 = 0.35`. It is not a real team's historical QUICK rate.
The alert threshold is **10 percentage points**, not a 10% relative increase.

| Next-QUICK forecast | Advisory alert |
|---|---|
| At least 0.45 | HIGH QUICK-RISK |
| At most 0.25 | LOW QUICK-RISK |
| Between those thresholds | NEAR BASELINE |

Both thresholds are inclusive. Comparisons treat values within `1e-12` of a
boundary as equal to account for floating-point representation. Tests check
exactly `0.45` and `0.25`, plus values `1e-8` inside and outside both boundaries.

## Requirements and setup

- Python **3.10 or newer**; the checkpoint was verified with Python 3.10.11.
- Git to clone the repository.
- Python standard library only, including `argparse`, `dataclasses`, `math`, and
  `unittest`. There are **no third-party dependencies** and no `pip install` step.

Clone the repository and enter its root:

```bash
git clone https://github.com/the-lmoney/CS471---Basketball-HMM.git
cd CS471---Basketball-HMM
python --version
```

The repository is **private**. Cloning requires an authenticated GitHub account
with repository access. Instructor access has not been confirmed; the owner must
verify that the instructor can access the submitted repository and commit. See
[checkpoint evidence](CHECKPOINT_EVIDENCE.md) for publication and verification
status. Repository visibility is unchanged.

A virtual environment is optional because the project has no external
dependencies. To use one on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Run the commands below from the repository root. With the environment activated,
`python` refers to that environment. Without a virtual environment, use your
Python 3.10+ executable; on systems where it is named `python3`, substitute that
command for `python`.

## Demonstrations

```bash
python -m tempo_scout demo --team "UC Davis" --sequence QUICK,NORMAL,LONG,QUICK
python -m tempo_scout demo --team "Nevada" --sequence QUICK,QUICK,QUICK
python -m tempo_scout demo --team "Wyoming" --sequence LONG,LONG,LONG
```

Actual output from a successful UC Davis demonstration:

```text
Air Force Opponent Tempo Intelligence Agent
CS471 - Core Algorithm Checkpoint
Selected team: UC Davis (display only)
SYNTHETIC SCENARIO: no historical or live team data is used.
Fixed HMM: hidden FAST / CONTROLLED; observed QUICK / NORMAL / LONG.
Durations: QUICK 1-12 s; NORMAL 13-22 s; LONG 23-60 s.
MODEL-IMPLIED DEMO REFERENCE: 0.350000
Alert threshold: 10 percentage points from reference.
Each row uses observations through that row; forecast is for NEXT possession.

No.  Observation     P(FAST)  P(CONTROLLED)  P(next QUICK)  Alert
-----------------------------------------------------------------------------------------
  1  QUICK          0.857143       0.142857       0.457143  HIGH QUICK-RISK
  2  NORMAL         0.714286       0.285714       0.414286  NEAR BASELINE
  3  LONG           0.220000       0.780000       0.266000  NEAR BASELINE
  4  QUICK          0.748872       0.251128       0.424662  NEAR BASELINE

Final interpretation: FAST is the more likely hidden tempo.
Next QUICK probability is 0.424662 (+7.47 percentage points vs. demo reference): NEAR BASELINE.
Advisory model estimate only; this is not a historical team rate or causal claim.
```

The synthetic QUICK-heavy example ends with `P(FAST) = 0.950649` and
`P(next QUICK) = 0.485195` (HIGH QUICK-RISK). The LONG-heavy example ends with
`P(FAST) = 0.049351` and `P(next QUICK) = 0.214805` (LOW QUICK-RISK). This contrast
shows how the same fixed model responds to different observation sequences.
Full actual outputs are recorded in [checkpoint evidence](CHECKPOINT_EVIDENCE.md).

The CLI accepts surrounding whitespace and lowercase categories, for example
`--sequence " quick , normal "`. Unknown symbols, empty entries, and empty
sequences produce a readable error and a nonzero exit status. The Python model
API requires exact uppercase symbols. Use `python -m tempo_scout demo --help`
for command help.

## Automated correctness verification

```bash
python -m unittest discover -s tests -v
```

The suite contains **30 tests**. Each test's docstring identifies its expected
result and explains what passing proves. Numerical expectations use independently
derived fractions and floating-point comparisons, rather than values generated
by the function under test.

| Check | Expected result and significance |
|---|---|
| First QUICK | FAST `6/7`, CONTROLLED `1/7`, next QUICK `16/35`, HIGH: verifies Bayesian conditioning followed by next-state forecasting. |
| First LONG | FAST `1/7`, CONTROLLED `6/7`, next QUICK `17/70`, LOW: verifies evidence favoring CONTROLLED. |
| First NORMAL | Equal beliefs, forecast `0.35`, NEAR: identical NORMAL emissions introduce no state preference. |
| Sequential filtering | QUICK,NORMAL gives FAST `5/7`; all four mixed-sequence checkpoints match exact fractions. |
| First-step timing | With asymmetric initial belief `(0.9,0.1)`, first QUICK gives FAST `54/55`: detects an erroneous transition before the first observation, which the symmetric default prior would hide. |
| Forecast timing | After first QUICK, the next forecast is `16/35`, distinct from the current-state emission mixture `37/70`. |
| Normalization and stability | All beliefs remain finite, bounded, and normalized through 3,000 observations. |
| Contrasting scenarios | QUICK-heavy observations increase FAST belief; their final forecast exceeds the LONG-heavy forecast. |
| Episode reset and causality | Repeated episodes start identically, and appending observations leaves earlier beliefs unchanged. |
| Validation | Invalid dimensions, probabilities, symbols, empty input, posteriors, and impossible first/later observations raise errors. |
| Alerts and CLI | Inclusive boundaries, nearby probabilities, all three required commands, and graceful input failures are checked. |

For example, after first QUICK the unnormalized weights are `(0.30,0.05)`.
Dividing by `0.35` gives `(6/7,1/7)`. Applying the transition gives next-state
belief `(5/7,2/7)`, whose QUICK emission mixture is `16/35`. After a subsequent
NORMAL, equal emission probabilities preserve that transitioned belief, so FAST
is `5/7`. Together these checks distinguish conditioning, transition timing, and
forecasting. See [checkpoint evidence](CHECKPOINT_EVIDENCE.md) for recorded
expected-versus-actual results and the executed test summary.

## Project structure

```text
CS471---Basketball-HMM/
├── README.md
├── .gitignore
├── CHECKPOINT_EVIDENCE.md
├── TEAM_PROGRESS.md
├── tempo_scout/
│   ├── __init__.py       # Public model imports
│   ├── __main__.py       # Argument parsing and terminal presentation
│   ├── hmm.py            # Validated model, filtering, and forecasting
│   └── scouting.py       # Demo reference and advisory alerts
└── tests/
    └── test_hmm.py       # Mathematical, validation, and CLI checks
```

## Team accountability and AI assistance

The intended responsibility allocation is approximately **65% for `the-lmoney`**
(algorithm and integration) and **35% for `SeniAkinola`** (verification and
documentation). These are planned responsibilities, not measured completed work.
Codex generated the implementation, tests, and documentation with independent AI
review. Human authorship, contribution, and review must be confirmed separately;
AI agent activity does not establish either teammate's contribution. See
[TEAM_PROGRESS.md](TEAM_PROGRESS.md) for specific assignments, verified evidence,
commit attribution, discrepancies, and remaining reviews.

## Limitations and future capstone work

The fixed parameters are illustrative assumptions. No team-specific parameters
have been learned, no predictive performance on real games has been measured,
and possession durations are already categorized by the caller. Alerts compare
against the model-implied demo reference only. A high FAST posterior or QUICK
forecast is not a guarantee of the next possession's outcome.

Future capstone development remains deferred:

- NCAA historical data ingestion and a validated possession parser.
- Baum-Welch training and team-specific HMM parameters.
- Held-out Brier-score evaluation.
- Ten-team conference scouting reports.

This checkpoint includes no historical-data ingestion, Parquet or SportsDataverse
integration, live data, web dashboard, causal press-defense model, or additional
AI algorithm. Remaining checkpoint obligations, including human contribution
confirmation and instructor access, are tracked separately in
[TEAM_PROGRESS.md](TEAM_PROGRESS.md).
