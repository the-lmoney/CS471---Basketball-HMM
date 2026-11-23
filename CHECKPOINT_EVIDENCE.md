# Core Algorithm Checkpoint evidence

Air Force Opponent Tempo Intelligence Agent — CS471.
Verified November 22, 2026 (America/Denver), using Python 3.10.11 on Windows.
The four required commands below were executed successfully. All displayed outputs
are captured from execution, not hardcoded demonstration responses.

## 1. Fixed model and mathematical timing

State order: `[FAST, CONTROLLED]`. Symbol order: `[QUICK, NORMAL, LONG]`.
Initial distribution: `[0.50, 0.50]`.

| Current state | Next FAST | Next CONTROLLED | Emit QUICK | Emit NORMAL | Emit LONG |
|---|---:|---:|---:|---:|---:|
| FAST | 0.80 | 0.20 | 0.60 | 0.30 | 0.10 |
| CONTROLLED | 0.20 | 0.80 | 0.10 | 0.30 | 0.60 |

Observation durations: QUICK 1–12 seconds, NORMAL 13–22, LONG 23–60.
The CLI accepts categories, not raw seconds. Names are display-only; all scenarios
are synthetic and use the same fixed parameters.

First update: `b_1(j) = pi(j) B[j,o_1] / sum_k pi(k) B[k,o_1]`.
Later updates: `predicted_t(j) = sum_i b_(t-1)(i) A[i,j]`, followed by the emission
weight and normalization. No transition precedes the first observation, and no
future observation enters an earlier belief.

Next forecast: `next_state(j) = sum_i b_t(i) A[i,j]`, then
`P(next QUICK) = sum_j next_state(j) B[j,QUICK]`.

**MODEL-IMPLIED DEMO REFERENCE**: `0.50*0.60 + 0.50*0.10 = 0.35`.
HIGH QUICK-RISK at/above 0.45; LOW QUICK-RISK at/below 0.25; otherwise
NEAR BASELINE (1e-12 floating-point equality tolerance). These are advisory
comparisons to the model, not historical team QUICK rates.

## 2. UC Davis: mixed sequence

```bash
python -m tempo_scout demo --team "UC Davis" --sequence QUICK,NORMAL,LONG,QUICK
```

Exit status: 0. Actual standard output:

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

## 3. Nevada: QUICK-heavy

```bash
python -m tempo_scout demo --team "Nevada" --sequence QUICK,QUICK,QUICK
```

Exit status: 0. Actual standard output:

```text
Air Force Opponent Tempo Intelligence Agent
CS471 - Core Algorithm Checkpoint
Selected team: Nevada (display only)
SYNTHETIC SCENARIO: no historical or live team data is used.
Fixed HMM: hidden FAST / CONTROLLED; observed QUICK / NORMAL / LONG.
Durations: QUICK 1-12 s; NORMAL 13-22 s; LONG 23-60 s.
MODEL-IMPLIED DEMO REFERENCE: 0.350000
Alert threshold: 10 percentage points from reference.
Each row uses observations through that row; forecast is for NEXT possession.

No.  Observation     P(FAST)  P(CONTROLLED)  P(next QUICK)  Alert
-----------------------------------------------------------------------------------------
  1  QUICK          0.857143       0.142857       0.457143  HIGH QUICK-RISK
  2  QUICK          0.937500       0.062500       0.481250  HIGH QUICK-RISK
  3  QUICK          0.950649       0.049351       0.485195  HIGH QUICK-RISK

Final interpretation: FAST is the more likely hidden tempo.
Next QUICK probability is 0.485195 (+13.52 percentage points vs. demo reference): HIGH QUICK-RISK.
Advisory model estimate only; this is not a historical team rate or causal claim.
```

## 4. Wyoming: LONG-heavy

```bash
python -m tempo_scout demo --team "Wyoming" --sequence LONG,LONG,LONG
```

Exit status: 0. Actual standard output:

```text
Air Force Opponent Tempo Intelligence Agent
CS471 - Core Algorithm Checkpoint
Selected team: Wyoming (display only)
SYNTHETIC SCENARIO: no historical or live team data is used.
Fixed HMM: hidden FAST / CONTROLLED; observed QUICK / NORMAL / LONG.
Durations: QUICK 1-12 s; NORMAL 13-22 s; LONG 23-60 s.
MODEL-IMPLIED DEMO REFERENCE: 0.350000
Alert threshold: 10 percentage points from reference.
Each row uses observations through that row; forecast is for NEXT possession.

No.  Observation     P(FAST)  P(CONTROLLED)  P(next QUICK)  Alert
-----------------------------------------------------------------------------------------
  1  LONG           0.142857       0.857143       0.242857  LOW QUICK-RISK
  2  LONG           0.062500       0.937500       0.218750  LOW QUICK-RISK
  3  LONG           0.049351       0.950649       0.214805  LOW QUICK-RISK

Final interpretation: CONTROLLED is the more likely hidden tempo.
Next QUICK probability is 0.214805 (-13.52 percentage points vs. demo reference): LOW QUICK-RISK.
Advisory model estimate only; this is not a historical team rate or causal claim.
```

## 5. Expected versus actual mathematical results

Expected fractions were independently derived by an AI reviewer, separate from
implementation. The required mixed-sequence checkpoints and contrasting final
values are asserted in the tests. This is not a claim of human teammate review.
With FAST posterior `p`, the next FAST prior is `q = 1/5+3p/5`;
QUICK updates to `6q/(1+5q)`, LONG to `q/(6-5q)`, and NORMAL leaves `q` unchanged.
The next-QUICK probability simplifies independently to `1/5+3p/10`.

| Scenario / step | Expected P(FAST) | Actual P(FAST) | Expected P(next QUICK) | Actual P(next QUICK) |
|---|---|---:|---|---:|
| UC Davis / 1 QUICK | 6/7 | 0.857142857143 | 16/35 | 0.457142857143 |
| UC Davis / 2 NORMAL | 5/7 | 0.714285714286 | 29/70 | 0.414285714286 |
| UC Davis / 3 LONG | 11/50 | 0.220000000000 | 133/500 | 0.266000000000 |
| UC Davis / 4 QUICK | 498/665 | 0.748872180451 | 1412/3325 | 0.424661654135 |
| Nevada / 1 QUICK | 6/7 | 0.857142857143 | 16/35 | 0.457142857143 |
| Nevada / 2 QUICK | 15/16 | 0.937500000000 | 77/160 | 0.481250000000 |
| Nevada / 3 QUICK | 366/385 | 0.950649350649 | 934/1925 | 0.485194805195 |
| Wyoming / 1 LONG | 1/7 | 0.142857142857 | 17/70 | 0.242857142857 |
| Wyoming / 2 LONG | 1/16 | 0.062500000000 | 7/32 | 0.218750000000 |
| Wyoming / 3 LONG | 19/385 | 0.049350649351 | 827/3850 | 0.214805194805 |

All required expected/actual assertions pass at 12 decimal places. CONTROLLED is
one minus FAST. The QUICK-heavy final forecast (0.485195) exceeds the LONG-heavy
forecast (0.214805), while repeated QUICKs strengthen FAST belief and repeated
LONGs strengthen CONTROLLED belief.

The mixed scenario's third row remains NEAR BASELINE: 0.266 is above the 0.25
LOW threshold. Its final FAST belief is 0.748872, but the next-QUICK forecast is
0.424662: hidden tempo belief and next observation probability are distinct.

## 6. Actual test execution

```bash
python -m unittest discover -s tests -v
```

Result: **30 executed, 30 passed, 0 failures, 0 errors, 0 skipped**, exit status 0.
Each test has a docstring stating its expected result and what passing proves.
Actual verbose test output (including those explanations):

```text
test_cli_normalizes_case_and_whitespace (test_hmm.CommandLineTests)
Friendly lowercase/spaced CLI tokens still give FAST=5/7 after QUICK,NORMAL. ... ok
test_empty_cli_sequence (test_hmm.CommandLineTests)
Empty and whitespace-only sequences exit nonzero: CLI rejects missing evidence. ... ok
test_invalid_cli_observations (test_hmm.CommandLineTests)
Unknown or missing tokens exit nonzero with a useful error and no traceback. ... ok
test_three_required_demonstrations (test_hmm.CommandLineTests)
All required commands succeed and show expected endpoints plus synthetic labeling. ... ok
test_contrasting_scenarios (test_hmm.FilteringTests)
QUICK x3 beats LONG x3; exact endpoints verify meaningful scenario contrast. ... ok
test_episode_reset (test_hmm.FilteringTests)
Repeated episodes match despite intervening LONGs: no belief persists in model. ... ok
test_filtering_has_no_future_leakage (test_hmm.FilteringTests)
A prefix is unchanged when observations are appended: filtering is causal. ... ok
test_first_long (test_hmm.FilteringTests)
LONG gives (1/7, 6/7), forecast 17/70 and LOW: controlled tempo evidence. ... ok
test_first_normal (test_hmm.FilteringTests)
NORMAL preserves equal belief and 0.35 forecast: equal emissions add no bias. ... ok
test_first_quick (test_hmm.FilteringTests)
QUICK gives (6/7, 1/7), forecast 16/35 and HIGH: Bayes plus prediction. ... ok
test_fixed_parameters (test_hmm.FilteringTests)
Exact approved state/symbol order and parameters prevent model drift. ... ok
test_forecast_predicts_next_not_current_possession (test_hmm.FilteringTests)
After QUICK, forecast is 16/35, not current-state 37/70: transition is used. ... ok
test_full_mixed_sequence (test_hmm.FilteringTests)
All four exact mixed checkpoints match: sequential inference is consistent. ... ok
test_iterable_observations (test_hmm.FilteringTests)
A generator gives the same 5/7 result: sequential iterable input is supported. ... ok
test_long_sequence_probabilities_are_normalized (test_hmm.FilteringTests)
Every belief sums to 1 over 3000 observations: per-step scaling stays stable. ... ok
test_no_transition_before_first_observation (test_hmm.FilteringTests)
Asymmetric prior gives QUICK FAST=54/55: first observation uses pi directly. ... ok
test_sequential_quick_normal (test_hmm.FilteringTests)
QUICK,NORMAL ends at FAST=5/7: prediction occurs between observations. ... ok
test_demo_reference_and_threshold (test_hmm.ScoutingTests)
Reference is 0.35 and threshold 0.10: alerts use the approved demo convention. ... ok
test_inclusive_alert_boundaries (test_hmm.ScoutingTests)
0.45 is HIGH and 0.25 LOW: equality at ten percentage points is included. ... ok
test_invalid_alert_forecasts (test_hmm.ScoutingTests)
Nonfinite and out-of-range forecasts raise ValueError: invalid alerts cannot appear. ... ok
test_values_near_alert_boundaries (test_hmm.ScoutingTests)
Values 1e-8 inside are NEAR, outside are HIGH/LOW: tolerance is narrow. ... ok
test_empty_sequences (test_hmm.ValidationTests)
Empty lists, tuples and iterators raise ValueError: no fictional posterior. ... ok
test_forecast_rejects_invalid_posteriors (test_hmm.ValidationTests)
Forecast rejects malformed or invalid beliefs: callers cannot bypass probability rules. ... ok
test_impossible_first_observation (test_hmm.ValidationTests)
Zero QUICK likelihood raises ValueError: zero normalization is never divided through. ... ok
test_impossible_later_observation (test_hmm.ValidationTests)
Valid QUICK then impossible QUICK raises ValueError: later normalization is checked. ... ok
test_invalid_observation_symbols (test_hmm.ValidationTests)
Unknown, non-string and lowercase model symbols raise ValueError: strict alphabet. ... ok
test_malformed_dimensions (test_hmm.ValidationTests)
Wrong vector/matrix sizes raise ValueError: state and symbol axes are enforced. ... ok
test_mutable_parameter_inputs_are_copied (test_hmm.ValidationTests)
Changing input lists leaves model unchanged: validation survives caller mutation. ... ok
test_nonfinite_and_out_of_range_probabilities (test_hmm.ValidationTests)
NaN, infinity, negative and >1 entries fail in all three parameter arrays. ... ok
test_probability_rows_must_sum_to_one (test_hmm.ValidationTests)
Non-unit initial, transition and emission sums fail: parameters are distributions. ... ok

----------------------------------------------------------------------
Ran 30 tests in 1.098s

OK
```

## 7. Why the correctness checks matter

| Required check | Expected behavior | What the passing result establishes |
|---|---|---|
| First QUICK | FAST=6/7, CONTROLLED=1/7, next QUICK=16/35, HIGH | Correct first Bayesian update, forecast and alert |
| First LONG | FAST=1/7, CONTROLLED=6/7, next QUICK=17/70, LOW | Correct controlled-tempo evidence handling |
| First NORMAL | Beliefs 0.5/0.5, forecast 0.35, NEAR | Equal emissions preserve the initial balance |
| Sequential QUICK,NORMAL | FAST=5/7 after NORMAL | Exactly one transition between observations |
| Probability normalization | Beliefs sum to 1, probabilities finite/in range over 3,000 observations | Per-step scaling remains numerically stable |
| Contrasting scenarios | QUICK x3 has greater final FAST and next-QUICK probability than LONG x3 | Observations influence scouting estimates in the intended direction |
| Episode reset | Identical result after an unrelated intervening episode | No retained belief contaminates a new demonstration |
| Invalid model/input | ValueError for bad symbols, empty inputs, malformed probabilities and zero likelihood | Invalid distributions and impossible evidence fail explicitly |

Additional checks strengthen the required categories:

- **First-step timing:** with initial `[0.9,0.1]`, first QUICK must produce FAST
  `54/55`. The default `[0.5,0.5]` is stationary, so this custom fixture is needed
  to expose a mistaken transition before the first observation.
- **Forecast timing:** after first QUICK, next-QUICK probability is `16/35`, not
  current-state emission mixture `37/70`. This detects omission of the next transition.
- **No future leakage:** appending future observations leaves all prefix beliefs identical.
- **Inclusive alerts:** 0.45 is HIGH, 0.25 LOW, while values 1e-8 inside remain NEAR.
- **CLI:** all three examples run as subprocesses; invalid/empty input exits nonzero
  with a useful error and no traceback; lowercase/spaced CLI tokens are normalized.
- **Validation persistence:** mutating caller-owned lists cannot alter model parameters.

## 8. GitHub and reproducibility status

Repository: [the-lmoney/CS471---Basketball-HMM](https://github.com/the-lmoney/CS471---Basketball-HMM).
Branch: `main`. GitHub metadata confirms that visibility is **private**; it was not changed.
No third-party Python packages, data files, training step or network connection are
needed to run the checkpoint after cloning. [README.md](README.md) supplies setup
and the exact commands. Python 3.10.11 was used for recorded verification.

Initial repository inspection found no commits or existing work. The local Windows
Store Python alias did not run, so verification selected the existing Thonny Python
installation through a process-local PATH change. Git authentication required
explicit selection of the stored `the-lmoney` account; credentials were not printed.

### Observed publication and fresh-checkout verification

`git push -u origin main` succeeded (with interactive credential prompts disabled).
Both independent Git commands returned the same published checkpoint SHA:

```text
git rev-parse HEAD
be3bd2f3cf9d0ca0c9c52c3a4f510ebf37bd2b0e

git ls-remote origin refs/heads/main
be3bd2f3cf9d0ca0c9c52c3a4f510ebf37bd2b0e    refs/heads/main
```

The GitHub connector separately retrieved that commit from the private repository.
A new clone from GitHub at this exact revision then ran all three demonstration
commands and the test command from its own root, without installed project packages
or data. The output matched the scenarios above. Its test summary was:

```text
Ran 30 tests in 1.169s

OK
```

The fresh clone's working tree remained clean. All commits inspected with
`git log --format="%h | %an | %ae | %s" --stat` and `git show --format=fuller`
used `Codex (AI assistance) <codex@local.invalid>` for author and committer.
Neither human teammate's identity was assigned to independently AI-produced work.

This record is added in a subsequent documentation-only commit; the tested
algorithm and tests are unchanged from the SHA above. To independently confirm
the latest publication after any documentation update, run `git rev-parse HEAD`
and `git ls-remote origin refs/heads/main` and compare their SHAs. The final
session handoff reports that latest observed result; a commit cannot contain its
own SHA as file content.

Instructor access remains **unconfirmed**: no instructor username was supplied.
The owner can access the repository, and the GitHub connector reports partner
`SeniAkinola` has write permission; neither proves instructor access. The user will
handle access and human contribution confirmations later.

## 9. Rubric evidence mapping and audit

| Category | Available points | Evidence |
|---|---:|---|
| Core Algorithm Execution | 20 | `hmm.py` and mathematical tests |
| Functional Demonstration | 10 | CLI and actual scenario output |
| Basic Correctness Verification | 10 | Tests and explained expected/actual results |
| GitHub Repository and Reproducibility | 5 | README and remote verification |
| Team Progress and Accountability | 5 | `TEAM_PROGRESS.md` and verified contributions |

| Excellent criterion audit | Supported evidence / remaining qualification |
|---|---|
| Correct essential operations and expected results | Supported: validated fixed model; normalized sequential updates; independent exact checkpoints; distinct next-state forecast |
| Representative, interpretable demonstration | Supported: three synthetic scenarios, aligned six-decimal probabilities, per-row alerts and final interpretation |
| Multiple meaningful checks with expected behavior and explained results | Supported: 30 passing tests, docstrings, actual verbose output and explanation tables |
| Organized, reproducible, accessible repository | Supported: README, successful push, matching remote SHA, and fresh GitHub clone execution; instructor private access still requires confirmation |
| Completed work, remaining tasks, challenges and specific contributions | Supported by honest planned/actual distinction and AI commit evidence; both humans must still confirm substantive contributions and reviews |

This is evidence targeting the available **50 points**, not an awarded grade or a
claim that unconfirmed human participation/access requirements have been met.

## 10. Unresolved items and scope

- Human teammate implementation/review attribution and the actual 65% / 35% split
  remain unconfirmed. [TEAM_PROGRESS.md](TEAM_PROGRESS.md) records planned roles,
  exact intended emails, actual AI commit evidence and next review responsibilities.
- Confirm instructor access to the private repository before submission.
- No unresolved mathematical or test failures were observed.

The full capstone was not built. NCAA ingestion, possession parsing, historical
season evaluation, Baum-Welch training, team-specific fitted models, Brier scoring,
ten-team scouting, dashboards, live data and causal defense models remain deferred.
