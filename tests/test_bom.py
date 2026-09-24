"""BOM honesty: every row priced, known total vs ₹1,800 target (hardware README §6)."""
import csv, pathlib

BOM = pathlib.Path(__file__).resolve().parents[1] / "BOM.csv"
TARGET = 1800

def _rows():
    with open(BOM) as f:
        return list(csv.DictReader(f))

def test_bom_parses():
    rows = _rows()
    assert rows, "BOM.csv empty"
    for r in rows:
        int(r["qty_unit"]); int(r["unit_cost_inr"])

def test_no_unpriced_rows():
    rows = _rows()
    unpriced = [r["item"] for r in rows if int(r["unit_cost_inr"]) <= 0]
    assert not unpriced, f"unpriced rows — budget unverifiable until filled: {unpriced}"

def test_known_total_within_target():
    total = sum(int(r["qty_unit"]) * int(r["unit_cost_inr"]) for r in _rows())
    assert total <= TARGET, f"₹{total} already over ₹{TARGET} before enclosure"
