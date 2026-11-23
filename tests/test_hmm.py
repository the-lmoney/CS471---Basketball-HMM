"""Independent expected values and behavioral checks for the HMM checkpoint.

Each test's docstring states the expected result and what it establishes.
Fractions below are hand-derived expectations, not calls to the implementation.
"""

from __future__ import annotations

import math
from pathlib import Path
import subprocess
import sys
import unittest

from tempo_scout.hmm import DEFAULT_MODEL, OBSERVATIONS, STATES, DiscreteHMM
from tempo_scout.scouting import ALERT_THRESHOLD, DEMO_REFERENCE, classify_alert


class FilteringTests(unittest.TestCase):
    """Check inference and forecasting against independently derived results."""

    def assert_probability(self, actual: float, expected: float) -> None:
        self.assertAlmostEqual(actual, expected, places=12)

    def test_fixed_parameters(self) -> None:
        """Exact approved state/symbol order and parameters prevent model drift."""
        self.assertEqual(STATES, ("FAST", "CONTROLLED"))
        self.assertEqual(OBSERVATIONS, ("QUICK", "NORMAL", "LONG"))
        self.assertEqual(DEFAULT_MODEL.initial, (0.5, 0.5))
        self.assertEqual(DEFAULT_MODEL.transition, ((0.8, 0.2), (0.2, 0.8)))
        self.assertEqual(DEFAULT_MODEL.emission, ((0.6, 0.3, 0.1), (0.1, 0.3, 0.6)))

    def test_first_quick(self) -> None:
        """QUICK gives (6/7, 1/7), forecast 16/35 and HIGH: Bayes plus prediction."""
        posterior = DEFAULT_MODEL.filter_sequence(["QUICK"])[0]
        self.assert_probability(posterior[0], 6 / 7)
        self.assert_probability(posterior[1], 1 / 7)
        forecast = DEFAULT_MODEL.predict_next_quick(posterior)
        self.assert_probability(forecast, 16 / 35)
        self.assertEqual(classify_alert(forecast), "HIGH QUICK-RISK")

    def test_first_long(self) -> None:
        """LONG gives (1/7, 6/7), forecast 17/70 and LOW: controlled tempo evidence."""
        posterior = DEFAULT_MODEL.filter_sequence(["LONG"])[0]
        self.assert_probability(posterior[0], 1 / 7)
        self.assert_probability(posterior[1], 6 / 7)
        forecast = DEFAULT_MODEL.predict_next_quick(posterior)
        self.assert_probability(forecast, 17 / 70)
        self.assertEqual(classify_alert(forecast), "LOW QUICK-RISK")

    def test_first_normal(self) -> None:
        """NORMAL preserves equal belief and 0.35 forecast: equal emissions add no bias."""
        posterior = DEFAULT_MODEL.filter_sequence(["NORMAL"])[0]
        self.assert_probability(posterior[0], 0.5)
        self.assert_probability(posterior[1], 0.5)
        forecast = DEFAULT_MODEL.predict_next_quick(posterior)
        self.assert_probability(forecast, 0.35)
        self.assertEqual(classify_alert(forecast), "NEAR BASELINE")

    def test_sequential_quick_normal(self) -> None:
        """QUICK,NORMAL ends at FAST=5/7: prediction occurs between observations."""
        posterior = DEFAULT_MODEL.filter_sequence(["QUICK", "NORMAL"])[1]
        self.assert_probability(posterior[0], 5 / 7)
        self.assert_probability(posterior[1], 2 / 7)

    def test_full_mixed_sequence(self) -> None:
        """All four exact mixed checkpoints match: sequential inference is consistent."""
        expected_fast = (6 / 7, 5 / 7, 11 / 50, 498 / 665)
        expected_forecasts = (16 / 35, 29 / 70, 133 / 500, 1412 / 3325)
        expected_alerts = ("HIGH QUICK-RISK", "NEAR BASELINE", "NEAR BASELINE", "NEAR BASELINE")
        beliefs = DEFAULT_MODEL.filter_sequence(["QUICK", "NORMAL", "LONG", "QUICK"])
        self.assertEqual(len(beliefs), 4)
        for step, posterior in enumerate(beliefs):
            with self.subTest(step=step + 1):
                self.assert_probability(posterior[0], expected_fast[step])
                self.assert_probability(posterior[1], 1 - expected_fast[step])
                forecast = DEFAULT_MODEL.predict_next_quick(posterior)
                self.assert_probability(forecast, expected_forecasts[step])
                self.assertEqual(classify_alert(forecast), expected_alerts[step])

    def test_no_transition_before_first_observation(self) -> None:
        """Asymmetric prior gives QUICK FAST=54/55: first observation uses pi directly."""
        model = DiscreteHMM(initial=(0.9, 0.1))
        posterior = model.filter_sequence(["QUICK"])[0]
        self.assert_probability(posterior[0], 54 / 55)
        self.assert_probability(posterior[1], 1 / 55)

    def test_filtering_has_no_future_leakage(self) -> None:
        """A prefix is unchanged when observations are appended: filtering is causal."""
        prefix = ["LONG", "QUICK", "NORMAL"]
        prefix_beliefs = DEFAULT_MODEL.filter_sequence(prefix)
        extended_beliefs = DEFAULT_MODEL.filter_sequence(prefix + ["QUICK"] * 5)
        self.assertEqual(prefix_beliefs, extended_beliefs[:len(prefix)])

    def test_forecast_predicts_next_not_current_possession(self) -> None:
        """After QUICK, forecast is 16/35, not current-state 37/70: transition is used."""
        posterior = DEFAULT_MODEL.filter_sequence(["QUICK"])[0]
        forecast = DEFAULT_MODEL.predict_next_quick(posterior)
        self.assert_probability(forecast, 16 / 35)
        self.assertGreater(abs(forecast - 37 / 70), 0.05)

    def test_long_sequence_probabilities_are_normalized(self) -> None:
        """Every belief sums to 1 over 3000 observations: per-step scaling stays stable."""
        beliefs = DEFAULT_MODEL.filter_sequence(["QUICK", "NORMAL", "LONG"] * 1000)
        self.assertEqual(len(beliefs), 3000)
        for posterior in beliefs:
            self.assert_probability(math.fsum(posterior), 1.0)
            for probability in posterior:
                self.assertTrue(math.isfinite(probability))
                self.assertGreaterEqual(probability, 0.0)
                self.assertLessEqual(probability, 1.0)
            forecast = DEFAULT_MODEL.predict_next_quick(posterior)
            self.assertTrue(math.isfinite(forecast))
            self.assertGreaterEqual(forecast, 0.2 - 1e-12)
            self.assertLessEqual(forecast, 0.5 + 1e-12)

    def test_contrasting_scenarios(self) -> None:
        """QUICK x3 beats LONG x3; exact endpoints verify meaningful scenario contrast."""
        quick = DEFAULT_MODEL.filter_sequence(["QUICK"] * 3)
        long = DEFAULT_MODEL.filter_sequence(["LONG"] * 3)
        self.assert_probability(quick[-1][0], 366 / 385)
        self.assert_probability(long[-1][0], 19 / 385)
        quick_forecast = DEFAULT_MODEL.predict_next_quick(quick[-1])
        long_forecast = DEFAULT_MODEL.predict_next_quick(long[-1])
        self.assert_probability(quick_forecast, 934 / 1925)
        self.assert_probability(long_forecast, 827 / 3850)
        self.assertGreater(quick[-1][0], long[-1][0])
        self.assertGreater(quick_forecast, long_forecast)
        self.assertTrue(all(a[0] < b[0] for a, b in zip(quick, quick[1:])))
        self.assertTrue(all(a[0] > b[0] for a, b in zip(long, long[1:])))

    def test_episode_reset(self) -> None:
        """Repeated episodes match despite intervening LONGs: no belief persists in model."""
        model = DiscreteHMM()
        before = model.filter_sequence(["QUICK", "NORMAL"])
        model.filter_sequence(["LONG"] * 10)
        after = model.filter_sequence(["QUICK", "NORMAL"])
        self.assertEqual(before, after)
        self.assert_probability(after[0][0], 6 / 7)
        self.assertEqual(model.initial, (0.5, 0.5))

    def test_iterable_observations(self) -> None:
        """A generator gives the same 5/7 result: sequential iterable input is supported."""
        observations = (item for item in ["QUICK", "NORMAL"])
        self.assert_probability(DEFAULT_MODEL.filter_sequence(observations)[-1][0], 5 / 7)


class ValidationTests(unittest.TestCase):
    """Reject malformed mathematical inputs and impossible evidence explicitly."""

    def test_invalid_observation_symbols(self) -> None:
        """Unknown, non-string and lowercase model symbols raise ValueError: strict alphabet."""
        for symbol in ("SLOW", "", "quick", " QUICK ", None, 12):
            with self.subTest(symbol=symbol), self.assertRaises(ValueError):
                DEFAULT_MODEL.filter_sequence(["NORMAL", symbol])

    def test_empty_sequences(self) -> None:
        """Empty lists, tuples and iterators raise ValueError: no fictional posterior."""
        for observations in ([], (), iter(())):
            with self.subTest(observations=observations), self.assertRaises(ValueError):
                DEFAULT_MODEL.filter_sequence(observations)

    def test_malformed_dimensions(self) -> None:
        """Wrong vector/matrix sizes raise ValueError: state and symbol axes are enforced."""
        invalid_parameters = (
            {"initial": ()},
            {"initial": (1.0,)},
            {"initial": (0.5, 0.25, 0.25)},
            {"transition": ()},
            {"transition": ((0.8, 0.2),)},
            {"transition": ((1.0,), (0.2, 0.8))},
            {"transition": ((0.8, 0.1, 0.1), (0.2, 0.8))},
            {"emission": ((0.6, 0.4), (0.1, 0.3, 0.6))},
            {"emission": ((0.6, 0.3, 0.1),)},
            {"emission": ((0.6, 0.3, 0.1),) * 3},
        )
        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                DiscreteHMM(**parameters)

    def test_nonfinite_and_out_of_range_probabilities(self) -> None:
        """NaN, infinity, negative and >1 entries fail in all three parameter arrays."""
        for value in (float("nan"), float("inf"), -float("inf"), -0.01, 1.01):
            cases = (
                {"initial": (value, 0.5)},
                {"transition": ((0.8, 0.2), (value, 0.8))},
                {"emission": ((0.6, 0.3, 0.1), (0.1, value, 0.6))},
            )
            for parameters in cases:
                with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                    DiscreteHMM(**parameters)

    def test_probability_rows_must_sum_to_one(self) -> None:
        """Non-unit initial, transition and emission sums fail: parameters are distributions."""
        invalid_parameters = (
            {"initial": (0.4, 0.4)},
            {"initial": (0.0, 0.0)},
            {"transition": ((0.8, 0.1), (0.2, 0.8))},
            {"transition": ((0.8, 0.2), (0.2, 0.7))},
            {"emission": ((0.5, 0.3, 0.1), (0.1, 0.3, 0.6))},
            {"emission": ((0.6, 0.3, 0.1), (0.1, 0.3, 0.5))},
        )
        for parameters in invalid_parameters:
            with self.subTest(parameters=parameters), self.assertRaises(ValueError):
                DiscreteHMM(**parameters)

    def test_forecast_rejects_invalid_posteriors(self) -> None:
        """Forecast rejects malformed or invalid beliefs: callers cannot bypass probability rules."""
        invalid_posteriors = (
            (), (1.0,), (0.5, 0.25, 0.25), (0.0, 0.0), (0.5, 0.4),
            (-0.1, 1.1), (float("nan"), 0.5), (float("inf"), 0.5),
        )
        for posterior in invalid_posteriors:
            with self.subTest(posterior=posterior), self.assertRaises(ValueError):
                DEFAULT_MODEL.predict_next_quick(posterior)

    def test_impossible_first_observation(self) -> None:
        """Zero QUICK likelihood raises ValueError: zero normalization is never divided through."""
        model = DiscreteHMM(emission=((0.0, 0.5, 0.5), (0.0, 0.5, 0.5)))
        with self.assertRaises(ValueError):
            model.filter_sequence(["QUICK"])

    def test_impossible_later_observation(self) -> None:
        """Valid QUICK then impossible QUICK raises ValueError: later normalization is checked."""
        model = DiscreteHMM(
            initial=(1.0, 0.0),
            transition=((0.0, 1.0), (0.0, 1.0)),
            emission=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        )
        self.assertEqual(model.filter_sequence(["QUICK"]), ((1.0, 0.0),))
        with self.assertRaises(ValueError):
            model.filter_sequence(["QUICK", "QUICK"])

    def test_mutable_parameter_inputs_are_copied(self) -> None:
        """Changing input lists leaves model unchanged: validation survives caller mutation."""
        initial = [0.5, 0.5]
        transition = [[0.8, 0.2], [0.2, 0.8]]
        emission = [[0.6, 0.3, 0.1], [0.1, 0.3, 0.6]]
        model = DiscreteHMM(initial=initial, transition=transition, emission=emission)
        initial[0] = 0.0
        transition[0][0] = 0.0
        emission[0][0] = 0.0
        self.assertEqual(model.initial, (0.5, 0.5))
        self.assertEqual(model.transition, ((0.8, 0.2), (0.2, 0.8)))
        self.assertEqual(model.emission, ((0.6, 0.3, 0.1), (0.1, 0.3, 0.6)))
        self.assertAlmostEqual(model.filter_sequence(["QUICK"])[0][0], 6 / 7, places=12)


class ScoutingTests(unittest.TestCase):
    """Check the fixed demo reference and inclusive advisory thresholds."""

    def test_demo_reference_and_threshold(self) -> None:
        """Reference is 0.35 and threshold 0.10: alerts use the approved demo convention."""
        self.assertAlmostEqual(DEMO_REFERENCE, 0.35, places=12)
        self.assertAlmostEqual(ALERT_THRESHOLD, 0.10, places=12)

    def test_inclusive_alert_boundaries(self) -> None:
        """0.45 is HIGH and 0.25 LOW: equality at ten percentage points is included."""
        self.assertEqual(classify_alert(0.45), "HIGH QUICK-RISK")
        self.assertEqual(classify_alert(0.25), "LOW QUICK-RISK")
        self.assertEqual(classify_alert(0.0), "LOW QUICK-RISK")
        self.assertEqual(classify_alert(1.0), "HIGH QUICK-RISK")

    def test_values_near_alert_boundaries(self) -> None:
        """Values 1e-8 inside are NEAR, outside are HIGH/LOW: tolerance is narrow."""
        cases = (
            (0.45 - 1e-8, "NEAR BASELINE"),
            (0.45 + 1e-8, "HIGH QUICK-RISK"),
            (0.25 + 1e-8, "NEAR BASELINE"),
            (0.25 - 1e-8, "LOW QUICK-RISK"),
            (0.35, "NEAR BASELINE"),
        )
        for forecast, expected in cases:
            with self.subTest(forecast=forecast):
                self.assertEqual(classify_alert(forecast), expected)

    def test_invalid_alert_forecasts(self) -> None:
        """Nonfinite and out-of-range forecasts raise ValueError: invalid alerts cannot appear."""
        for forecast in (float("nan"), float("inf"), -float("inf"), -0.01, 1.01):
            with self.subTest(forecast=forecast), self.assertRaises(ValueError):
                classify_alert(forecast)


class CommandLineTests(unittest.TestCase):
    """Exercise the public module command as an instructor would run it."""

    @staticmethod
    def run_demo(team: str, sequence: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "tempo_scout", "demo", "--team", team, "--sequence", sequence],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_three_required_demonstrations(self) -> None:
        """All required commands succeed and show expected endpoints plus synthetic labeling."""
        cases = (
            ("UC Davis", "QUICK,NORMAL,LONG,QUICK", "0.748872", "0.424662"),
            ("Nevada", "QUICK,QUICK,QUICK", "0.950649", "0.485195"),
            ("Wyoming", "LONG,LONG,LONG", "0.049351", "0.214805"),
        )
        for team, sequence, fast, forecast in cases:
            with self.subTest(team=team):
                result = self.run_demo(team, sequence)
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                for expected in (team, fast, forecast, "MODEL-IMPLIED DEMO REFERENCE", "0.350000"):
                    self.assertIn(expected, result.stdout)
                self.assertIn("synthetic", result.stdout.lower())
                self.assertIn("P(FAST)", result.stdout)
                self.assertIn("P(CONTROLLED)", result.stdout)
                self.assertIn("P(next QUICK)", result.stdout)

    def test_invalid_cli_observations(self) -> None:
        """Unknown or missing tokens exit nonzero with a useful error and no traceback."""
        for sequence in ("QUICK,SLOW", "QUICK,,LONG", "QUICK,"):
            with self.subTest(sequence=sequence):
                result = self.run_demo("Test", sequence)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("error", result.stderr.lower())
                self.assertNotIn("Traceback", result.stderr)

    def test_empty_cli_sequence(self) -> None:
        """Empty and whitespace-only sequences exit nonzero: CLI rejects missing evidence."""
        for sequence in ("", "   "):
            with self.subTest(sequence=sequence):
                result = self.run_demo("Test", sequence)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("error", result.stderr.lower())
                self.assertNotIn("Traceback", result.stderr)

    def test_cli_normalizes_case_and_whitespace(self) -> None:
        """Friendly lowercase/spaced CLI tokens still give FAST=5/7 after QUICK,NORMAL."""
        result = self.run_demo("Test", " quick , normal ")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("0.714286", result.stdout)
        self.assertIn("0.414286", result.stdout)


if __name__ == "__main__":
    unittest.main()
