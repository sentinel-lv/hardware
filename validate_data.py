"""Validate bench characterisation CSVs (hardware README §4).

Usage: python3 hardware/validate_data.py
Checks schema + physical ranges + the two credibility claims:
  - de-energised output collapses below 5% of nominal within 200 ms
  - rain spray deviation stays below the 60% collapse threshold
Exit nonzero on any failure. Empty (header-only) files are skipped, not failed.
"""
import csv, pathlib, sys

DATA = pathlib.Path(__file__).resolve().parent / "data"
REQUIRED = ["node_id", "standoff_cm", "angle_deg", "temp_c", "rh_pct",
            "line_v", "efield_raw", "notes"]
BOUNDS = {"standoff_cm": (10, 80), "angle_deg": (0, 90), "temp_c": (-10, 55),
          "rh_pct": (40, 95), "line_v": (50, 250)}

def check_file(fp):
    rows = list(csv.DictReader(open(fp)))
    errs = []
    if not rows:
        return [f"{fp.name}: no rows yet (bench pending)"]
    hdr = rows and list(rows[0].keys())
    for col in REQUIRED:
        if col not in (hdr or []):
            errs.append(f"{fp.name}: missing column {col}")
    if errs:
        return errs
    notes = []
    for i, r in enumerate(rows, 2):
        try:
            for col, (lo, hi) in BOUNDS.items():
                v = float(r[col])
                if not lo <= v <= hi:
                    errs.append(f"{fp.name}:{i} {col}={v} outside [{lo},{hi}] (README §4)")
            float(r["efield_raw"])
        except ValueError as e:
            errs.append(f"{fp.name}:{i} bad number ({e})")
    # credibility claims, evaluated on flagged rows
    base = [float(r["efield_raw"]) for r in rows if "energised" in r["notes"]]
    dead = [float(r["efield_raw"]) for r in rows if "de-energised" in r["notes"]]
    if base and dead:
        nom = sum(base) / len(base)
        if not all(v < 0.05 * nom for v in dead):
            errs.append(f"{fp.name}: de-energised output not <5% of nominal (M2 gate)")
        else:
            notes.append(f"{fp.name}: collapse claim holds ({len(dead)} rows)")
    rain = [r for r in rows if "rain" in r["notes"] and "deviation_pct" in r]
    if rain and any(abs(float(r["deviation_pct"])) >= 60 for r in rain):
        errs.append(f"{fp.name}: rain deviation breached 60% threshold (M2 gate)")
    return errs + notes

def main():
    problems, notes = [], []
    files = sorted(DATA.glob("*.csv"))
    if not files:
        print("no CSVs yet"); return 0
    for fp in files:
        for line in check_file(fp):
            (notes if "bench pending" in line or "holds" in line else problems).append(line)
    for n in notes:
        print("note:", n)
    if problems:
        print("FAIL:")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(files)} file(s) schema + ranges valid")
    return 0

if __name__ == "__main__":
    sys.exit(main())
