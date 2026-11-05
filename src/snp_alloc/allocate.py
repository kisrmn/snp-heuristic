"""Ядро: распределение доступного объёма одной позиции между заявками.

Правило:
1. Жёсткий приоритет: уровень 1 обслуживается раньше уровня 2 и т.д. Если старшему уровню
   остаток уже не подходит (партия не влезает), он достаётся младшему, объём не простаивает.
2. Внутри уровня объём раздаётся по одной партии: следующую партию получает заявка
   с наименьшей долей удовлетворения (allocated / demand), ничья решается по request_id.
   Первая партия заявки равна её min_qty, дальше шаг кратности. Итог близок к пропорции.
3. Проход 1: не больше demand (округление вниз до кратности). Проход 2: только из остатка,
   можно округлить вверх до ближайшей кратности (перегруз меньше одной партии).
"""

from collections.abc import Iterable
from fractions import Fraction
from itertools import groupby

from snp_alloc.models import Request, ceil_to


def _fill(alloc: dict[str, int], reqs: list[Request], caps: dict[str, int], left: int) -> int:
    """Раздаёт `left` по уровням приоритета, не превышая `caps`. Возвращает остаток."""
    for _, tier_iter in groupby(reqs, key=lambda r: r.priority):
        tier = list(tier_iter)
        while True:
            options = []
            for r in tier:
                got = alloc[r.request_id]
                step = r.step if got else r.min_qty
                if step <= left and got + step <= caps[r.request_id]:
                    options.append((Fraction(got, r.demand_qty), r.request_id, step))
            if not options:
                break
            _, rid, step = min(options)
            alloc[rid] += step
            left -= step
    return left


def allocate(available_qty: int, requests: Iterable[Request]) -> dict[str, int]:
    """Отгрузка по каждой заявке. Нераспределено = available_qty - sum(result)."""
    if available_qty < 0:
        raise ValueError(f"available_qty must be >= 0, got {available_qty}")
    reqs = sorted(requests, key=lambda r: (r.priority, r.request_id))
    ids = [r.request_id for r in reqs]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate request_id in one case")

    alloc = dict.fromkeys(ids, 0)
    down = {r.request_id: r.demand_qty // r.step * r.step for r in reqs}
    up = {r.request_id: ceil_to(r.demand_qty, r.step) for r in reqs}
    left = _fill(alloc, reqs, down, available_qty)
    _fill(alloc, reqs, up, left)
    return alloc
