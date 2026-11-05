import argparse
import logging
from pathlib import Path

from snp_alloc.allocate import allocate
from snp_alloc.io import Case, load_cases
from snp_alloc.models import Request

logger = logging.getLogger(__name__)


def _warnings(request: Request, available_qty: int) -> list[str]:
    warnings = []
    if request.rounding_value == 0:
        warnings.append("rounding_value is 0, treated as 1")

    if request.demand_qty > 0:
        reachable = min(request.demand_rounded_up, available_qty)
        if request.min_qty > reachable:
            warnings.append(f"min_lot {request.min_lot} is unreachable")
    return warnings


def _log_case(case: Case) -> None:
    supply = case.supply
    plan = allocate(supply.available_qty, case.requests)
    logger.info(
        f"{supply.case_id}: {supply.item} @ {supply.source_location}, "
        f"period {supply.period}, available {supply.available_qty}"
    )

    ordered = sorted(case.requests, key=lambda request: (request.priority, request.request_id))
    for request in ordered:
        shipped = plan[request.request_id]
        logger.info(
            f"  {request.request_id} priority {request.priority}: "
            f"demand {request.demand_qty}, min_lot {request.min_lot}, "
            f"rounding {request.rounding_value} -> shipped {shipped}"
        )
        for warning in _warnings(request, supply.available_qty):
            logger.warning(f"  {request.request_id}: {warning}")

    for request_id, reason in case.rejected.items():
        logger.warning(f"  {request_id} rejected: {reason}")

    shipped_total = sum(plan.values())
    unallocated = supply.available_qty - shipped_total
    logger.info(f"  unallocated: {unallocated}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    parser = argparse.ArgumentParser(description="SNP Heuristic: shortage allocation")
    parser.add_argument("--data", type=Path, default=Path("data"), help="dir with CSV files")
    args = parser.parse_args()

    for case in load_cases(args.data):
        _log_case(case)


if __name__ == "__main__":
    main()
