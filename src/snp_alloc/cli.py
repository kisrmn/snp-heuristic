"""Точка входа: считает все кейсы из CSV и печатает план."""

import argparse
from pathlib import Path

from snp_alloc.allocate import allocate
from snp_alloc.io import Case, load_cases
from snp_alloc.models import Request, ceil_to


def _note(r: Request, available: int) -> str:
    notes = []
    if r.rounding_value == 0:
        notes.append("rounding_value=0 -> 1")
    if r.demand_qty and r.min_qty > min(ceil_to(r.demand_qty, r.step), available):
        notes.append(f"min_lot {r.min_lot} unreachable")
    return ", ".join(notes)


def print_case(case: Case) -> None:
    s = case.supply
    plan = allocate(s.available_qty, case.requests)
    print(f"\n{s.case_id}  {s.period} {s.item} @ {s.source_location}  available={s.available_qty}")
    print(f"  {'request':<8}{'prio':>5}{'demand':>8}{'min_lot':>8}{'round':>6}{'shipped':>9}  note")
    for r in sorted(case.requests, key=lambda r: (r.priority, r.request_id)):
        print(
            f"  {r.request_id:<8}{r.priority:>5}{r.demand_qty:>8}{r.min_lot:>8}"
            f"{r.rounding_value:>6}{plan[r.request_id]:>9}  {_note(r, s.available_qty)}"
        )
    for rid, reason in case.rejected.items():
        print(f"  {rid:<8}{'rejected':>27}{0:>9}  {reason}")
    print(f"  unallocated: {s.available_qty - sum(plan.values())}")


def main() -> None:
    parser = argparse.ArgumentParser(description="SNP Heuristic: shortage allocation")
    parser.add_argument("--data", type=Path, default=Path("data"), help="dir with CSV files")
    cases, errors = load_cases(parser.parse_args().data)
    for case in cases:
        print_case(case)
    for err in errors:
        print(f"\nERROR {err}")


if __name__ == "__main__":
    main()
