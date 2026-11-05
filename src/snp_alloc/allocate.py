from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction

from snp_alloc.models import Request, RequestId


@dataclass(frozen=True)
class Candidate:
    request_id: RequestId
    lot: int
    fill_rate: Fraction


def _split_into_tiers(requests: list[Request]) -> list[list[Request]]:
    tiers: dict[int, list[Request]] = defaultdict(list)
    for request in requests:
        tiers[request.priority].append(request)
    return [tiers[priority] for priority in sorted(tiers)]


def _next_lot(
    request: Request,
    allocated: int,
    remaining_qty: int,
    overship: bool,
) -> int | None:
    lot = request.min_shipment_qty if allocated == 0 else request.rounding_step
    cap = request.demand_rounded_up if overship else request.demand_rounded_down
    if lot > remaining_qty or allocated + lot > cap:
        return None
    return lot


def _best_candidate(
    tier: list[Request],
    allocation: dict[RequestId, int],
    remaining_qty: int,
    overship: bool,
) -> Candidate | None:
    candidates: list[Candidate] = []
    for request in tier:
        allocated = allocation[request.request_id]
        lot = _next_lot(
            request=request,
            allocated=allocated,
            remaining_qty=remaining_qty,
            overship=overship,
        )
        if lot is None:
            continue
        fill_rate = Fraction(numerator=allocated, denominator=request.demand_qty)
        candidate = Candidate(
            request_id=request.request_id,
            lot=lot,
            fill_rate=fill_rate,
        )
        candidates.append(candidate)

    if not candidates:
        return None
    return min(candidates, key=lambda candidate: (candidate.fill_rate, candidate.request_id))


def _fill(
    allocation: dict[RequestId, int],
    tiers: list[list[Request]],
    remaining_qty: int,
    overship: bool,
) -> int:
    for tier in tiers:
        while True:
            candidate = _best_candidate(
                tier=tier,
                allocation=allocation,
                remaining_qty=remaining_qty,
                overship=overship,
            )
            if candidate is None:
                break
            allocation[candidate.request_id] += candidate.lot
            remaining_qty -= candidate.lot
    return remaining_qty


def allocate(available_qty: int, requests: Iterable[Request]) -> dict[str, int]:
    if available_qty < 0:
        raise ValueError(f"available_qty must be >= 0, got {available_qty}")

    ordered = sorted(requests, key=lambda request: request.sort_key)
    request_ids = [request.request_id for request in ordered]
    has_duplicates = len(set(request_ids)) < len(request_ids)
    if has_duplicates:
        raise ValueError("duplicate request_id in one case")

    allocation = {request_id: 0 for request_id in request_ids}
    tiers = _split_into_tiers(requests=ordered)
    remaining_qty = available_qty
    for overship in (False, True):
        remaining_qty = _fill(
            allocation=allocation,
            tiers=tiers,
            remaining_qty=remaining_qty,
            overship=overship,
        )

    return allocation
