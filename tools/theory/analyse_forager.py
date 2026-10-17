"""Pre-registered tests for the forager replication (docs/research/PREREG_AN.md)."""

import json
import sys

from neuralmind.research.stats import paired_diff

TESTS = [
    ("N1", "Under Hebbian credit and a scalar baseline, shaping lowers the forward action's food weights",
     "w_food_forward", "hebb_scalar", "hebb_noshape", "less"),
    ("N2", "Under Hebbian credit, a state baseline keeps the forward action's food weights higher than a scalar one",
     "w_food_forward", "hebb_state", "hebb_scalar", "greater"),
    ("N3", "Under score-function credit, shaping lowers the forward action's food weights (predicted: not supported)",
     "w_food_forward", "score_scalar", "score_noshape", "less"),
    ("N4", "Under score-function credit, shaping raises foraging", "food_per_1000", "score_scalar", "score_noshape", "greater"),
    ("N5", "Under Hebbian credit, a state baseline raises foraging over a scalar one", "food_per_1000", "hebb_state", "hebb_scalar", "greater"),
]

if __name__ == "__main__":
    raw = json.load(open(sys.argv[1]))["raw"]
    for tid, text, metric, a, b, direction in TESTS:
        ci = paired_diff([r[metric] for r in raw[a]], [r[metric] for r in raw[b]])
        ok = ci["hi"] < 0 if direction == "less" else ci["lo"] > 0
        print(f"| {tid} | {text} | {ci['mean']:+.3f} [{ci['lo']:+.3f}, {ci['hi']:+.3f}] | {'supported' if ok else 'not supported'} |")
