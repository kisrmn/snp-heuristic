import argparse
import logging
from pathlib import Path

from snp_alloc.allocate import allocate
from snp_alloc.csv_reader import Case, load_cases
from snp_alloc.models import Request

logger = logging.getLogger(__name__)


def _request_warnings(request: Request, available_qty: int) -> list[str]:
    messages = []
    if request.rounding_value == 0:
        messages.append("rounding_value is 0, treated as 1")

    if request.demand_qty > 0:
        reachable = min(request.demand_rounded_up, available_qty)
        if request.min_shipment_qty > reachable:
            messages.append(f"min_lot {request.min_lot} is unreachable")
    return messages


def _log_case(case: Case) -> None:
    supply = case.supply
    plan = allocate(available_qty=supply.available_qty, requests=case.requests)
    logger.info(
        f"{supply.case_id}: {supply.item} @ {supply.source_location}, "
        f"period {supply.period}, available {supply.available_qty}"
    )

    ordered = sorted(case.requests, key=lambda request: request.sort_key)
    for request in ordered:
        shipped = plan[request.request_id]
        logger.info(
            f"{supply.case_id} {request.request_id} priority {request.priority}: "
            f"demand {request.demand_qty}, min_lot {request.min_lot}, "
            f"rounding {request.rounding_value} -> shipped {shipped}"
        )
        request_warnings = _request_warnings(request=request, available_qty=supply.available_qty)
        for message in request_warnings:
            logger.warning(f"{supply.case_id} {request.request_id}: {message}")

    for request_id, reason in case.rejection_reasons.items():
        logger.warning(f"{supply.case_id} {request_id} rejected: {reason}")

    shipped_total = sum(plan.values())
    unallocated = supply.available_qty - shipped_total
    logger.info(f"{supply.case_id} unallocated: {unallocated}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    parser = argparse.ArgumentParser(description="SNP Heuristic: shortage allocation")
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data"),
        help="dir with CSV files",
    )
    args = parser.parse_args()

    for case in load_cases(data_dir=args.data):
        _log_case(case=case)


if __name__ == "__main__":
    main()
