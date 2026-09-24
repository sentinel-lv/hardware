# hardware/data — characterisation dataset (deliverable M2)

Sweep per hardware/README §4: standoff 10–80cm, angle 0–90°, temp→55°C, RH 40–95%, spray, adjacent-line@1m, 50–250V variac.
Output CSVs + plots here, then hand to simulator/ for signal-model re-fit.

## Re-fit procedure (hand to simulator/)

1. Run `python3 hardware/validate_data.py` — must print OK (M2 gates inside).
2. From the validated CSVs compute: noise σ around nominal (replaces `GAUSS_SIGMA`
   in `simulator/sim/node.py`), collapse depth when de-energised (replaces `break_mask`
   0.02), rain-gust dip depth/duration (replaces `rain_burst` 0.35/1 s), and the
   standoff curve (replaces `nominal` 4.9 + gain note for commissioning).
3. Update the constants, re-run `python3 -m pytest simulator/tests backend/tests`,
   and confirm no vector outcome changes (thresholds must survive real data —
   if they don't, the thresholds were tuned to fantasy; say so in the PR).
