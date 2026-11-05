from collections.abc import Iterable
from fractions import Fraction
from itertools import groupby

from snp_alloc.models import Request


def _next_lot(request: Request, allocated: int, left: int, overship: bool) -> int | None:
    lot = request.min_qty if allocated == 0 else request.step
    cap = request.demand_rounded_up if overship else request.demand_rounded_down
    if lot > left or allocated + lot > cap:
        return None
    return lot


def _fill(allocation: dict[str, int], requests: list[Request], left: int, overship: bool) -> int:
    for _, tier_requests in groupby(requests, key=lambda request: request.priority):
        tier = list(tier_requests)
        while True:
            candidates = []
            for request in tier:
                allocated = allocation[request.request_id]
                lot = _next_lot(request, allocated, left, overship)
                if lot is None:
                    continue
                fill_rate = Fraction(allocated, request.demand_qty)
                candidates.append((fill_rate, request.request_id, lot))

            if not candidates:
                break

            _, request_id, lot = min(candidates)
            allocation[request_id] += lot
            left -= lot
    return left


def allocate(available_qty: int, requests: Iterable[Request]) -> dict[str, int]:
    """Распределяет доступный объём одной позиции между заявками.

    Приоритет жёсткий: уровень 1 обслуживается раньше уровня 2. Если старшему уровню остаток
    не подходит (партия не влезает), он достаётся младшему. Внутри уровня объём раздаётся
    по одной партии: следующую получает заявка с наименьшей долей allocated / demand,
    ничья решается по request_id. Первая партия заявки равна min_qty, следующие равны step.

    Первый проход отгружает не больше demand (округление вниз до кратности). Второй проход
    раздаёт только остаток и может округлить вверх до ближайшей кратности.
    """
    if available_qty < 0:
        raise ValueError(f"available_qty must be >= 0, got {available_qty}")

    ordered = sorted(requests, key=lambda request: (request.priority, request.request_id))
    request_ids = [request.request_id for request in ordered]
    if len(set(request_ids)) != len(request_ids):
        raise ValueError("duplicate request_id in one case")

    allocation = dict.fromkeys(request_ids, 0)
    left = _fill(allocation, ordered, available_qty, overship=False)
    _fill(allocation, ordered, left, overship=True)
    return allocation
