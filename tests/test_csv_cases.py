import random

import pytest

from snp_alloc.allocate import allocate

EXPECTED = {
    # Кратность 25 при спросе 40: всем по 25, остаток 25 уходит R-101 (ничья по id).
    "CASE_01": {"R-101": 50, "R-102": 25, "R-103": 25},
    # Пропорция 25 < min_lot 30: обслуживаем троих, четвёртый получает 0.
    "CASE_02": {"R-201": 40, "R-202": 30, "R-203": 30, "R-204": 0},
    # R-302 (спрос -10) отклонена при чтении; rounding 0 у R-304 трактуется как 1.
    "CASE_03": {"R-301": 0, "R-304": 30, "R-303": 30},
    # 97 на 5 одинаковых заявок: 20, 20, 19, 19, 19 по request_id, порядок строк не важен.
    "CASE_04": {"R-401": 20, "R-402": 20, "R-403": 19, "R-404": 19, "R-405": 19},
    # Избыток: из остатка округляем вверх до кратности.
    "CASE_05": {"R-501": 50, "R-502": 40, "R-503": 10},
    # min_lot 250 недостижим; min_lot 30 при кратности 25 равен 50; R-603 получает 84 из остатка.
    "CASE_06": {"R-601": 100, "R-602": 0, "R-603": 84},
    # Жёсткий приоритет: R-701 забирает всё.
    "CASE_07": {"R-701": 100, "R-702": 0, "R-703": 0},
}


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_expected_plan(cases, case_id):
    """Фиксирует план каждого CSV-кейса; при смене правила покажет, какой кейс изменился."""
    case = cases[case_id]
    assert allocate(case.supply.available_qty, case.requests) == EXPECTED[case_id]


def test_invalid_request_rejected(cases):
    """demand=-10 отклоняется при чтении; без этого строка попала бы в расчёт или уронила кейс."""
    assert "R-302" in cases["CASE_03"].rejected


@pytest.mark.parametrize("case_id", sorted(EXPECTED))
def test_hard_constraints(cases, case_id):
    """Три зафиксированных требования; если сломать любое из них, план станет невалидным."""
    case = cases[case_id]
    available = case.supply.available_qty
    plan = allocate(available, case.requests)
    assert sum(plan.values()) <= available
    for r in case.requests:
        q = plan[r.request_id]
        assert q == 0 or (q >= r.min_qty and q % r.step == 0)
    for seed in range(5):
        shuffled = case.requests[:]
        random.Random(seed).shuffle(shuffled)
        assert allocate(available, shuffled) == plan
