"""Terminal demonstration; model mathematics live in :mod:`tempo_scout.hmm`."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .hmm import DEFAULT_MODEL, OBSERVATIONS
from .scouting import ALERT_THRESHOLD, DEMO_REFERENCE, classify_alert


def parse_sequence(value: str) -> tuple[str, ...]:
    """Accept comma-separated categories, ignoring surrounding space and case."""
    observations = tuple(symbol.strip().upper() for symbol in value.split(","))
    if not value.strip() or any(not symbol for symbol in observations):
        raise argparse.ArgumentTypeError(
            "sequence must contain observations with no empty entries"
        )
    invalid = [symbol for symbol in observations if symbol not in OBSERVATIONS]
    if invalid:
        raise argparse.ArgumentTypeError(
            f"invalid observation {invalid[0]!r}; choose QUICK, NORMAL, or LONG"
        )
    return observations


def main(argv: Sequence[str] | None = None) -> int:
    """Run a fresh synthetic episode and print sequential model estimates."""
    parser = argparse.ArgumentParser(
        description="Air Force Opponent Tempo Intelligence Agent - CS471 checkpoint"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="run a synthetic fixed-HMM scenario")
    demo.add_argument("--team", required=True, help="display-only opponent name")
    demo.add_argument(
        "--sequence", required=True, type=parse_sequence,
        help="comma-separated QUICK, NORMAL, LONG observations",
    )
    args = parser.parse_args(argv)
    if not args.team.strip():
        parser.error("team name must not be empty")

    try:
        beliefs = DEFAULT_MODEL.filter_sequence(args.sequence)
    except ValueError as error:
        parser.error(str(error))

    print("Air Force Opponent Tempo Intelligence Agent")
    print("CS471 - Core Algorithm Checkpoint")
    print(f"Selected team: {args.team.strip()} (display only)")
    print("SYNTHETIC SCENARIO: no historical or live team data is used.")
    print("Fixed HMM: hidden FAST / CONTROLLED; observed QUICK / NORMAL / LONG.")
    print("Durations: QUICK 1-12 s; NORMAL 13-22 s; LONG 23-60 s.")
    print(f"MODEL-IMPLIED DEMO REFERENCE: {DEMO_REFERENCE:.6f}")
    print(f"Alert threshold: {100 * ALERT_THRESHOLD:.0f} percentage points from reference.")
    print("Each row uses observations through that row; forecast is for NEXT possession.")
    print()
    print(
        f"{'No.':>3}  {'Observation':<11}  {'P(FAST)':>10}  "
        f"{'P(CONTROLLED)':>13}  {'P(next QUICK)':>13}  Alert"
    )
    print("-" * 89)
    for number, (observation, posterior) in enumerate(
        zip(args.sequence, beliefs), start=1
    ):
        forecast = DEFAULT_MODEL.predict_next_quick(posterior)
        print(
            f"{number:>3}  {observation:<11}  {posterior[0]:>10.6f}  "
            f"{posterior[1]:>13.6f}  {forecast:>13.6f}  {classify_alert(forecast)}"
        )

    final_belief = beliefs[-1]
    final_forecast = DEFAULT_MODEL.predict_next_quick(final_belief)
    if final_belief[0] > final_belief[1]:
        mode = "FAST is the more likely hidden tempo"
    elif final_belief[0] < final_belief[1]:
        mode = "CONTROLLED is the more likely hidden tempo"
    else:
        mode = "FAST and CONTROLLED are equally likely"
    print()
    print(f"Final interpretation: {mode}.")
    print(
        f"Next QUICK probability is {final_forecast:.6f} "
        f"({100 * (final_forecast - DEMO_REFERENCE):+.2f} percentage points "
        f"vs. demo reference): {classify_alert(final_forecast)}."
    )
    print("Advisory model estimate only; this is not a historical team rate or causal claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
