import random

import pytest

from snp_alloc.allocate import allocate

EXPECTED = {
    "CASE_01": {"R-101": 50, "R-102": 25, "R-103": 25},
    "CASE_02": {"R-201": 40, "R-202": 30, "R-203": 30, "R-204": 0},
    "CASE_03": {"R-301": 0, "R-304": 30, "R-303": 30},
    "CASE_04": {"R-401": 20, "R-402": 20, "R-403": 19, "R-404": 19, "R-405": 19},
    "CASE_05": {"R-501": 50, "R-502": 40, "R-503": 10},
    "CASE_06": {"R-601": 100, "R-602": 0, "R-603": 84},
    "CASE_07": {"R-701": 100, "R-702": 0, "R-703": 0},
}


@pytest.mark.parametrize(argnames="case_id", argvalues=sorted(EXPECTED))
def test_expected_plan(cases, case_id):
    """Фиксирует план каждого CSV-кейса; при смене правила покажет, какой кейс изменился."""
    case = cases[case_id]
    plan = allocate(available_qty=case.supply.available_qty, requests=case.requests)
    assert plan == EXPECTED[case_id]


def test_invalid_request_rejected(cases):
    """demand=-10 отклоняется при чтении; без этого строка попала бы в расчёт или уронила кейс."""
    rejection_reasons = cases["CASE_03"].rejection_reasons
    assert "R-302" in rejection_reasons


@pytest.mark.parametrize(argnames="case_id", argvalues=sorted(EXPECTED))
def test_hard_constraints(cases, case_id):
    """Три зафиксированных требования; если сломать любое из них, план станет невалидным."""
    case = cases[case_id]
    available = case.supply.available_qty
    plan = allocate(available_qty=available, requests=case.requests)

    shipped_total = sum(plan.values())
    assert shipped_total <= available

    for request in case.requests:
        shipped = plan[request.request_id]
        if shipped == 0:
            continue
        assert shipped >= request.min_shipment_qty
        assert shipped % request.rounding_step == 0

    for seed in range(5):
        shuffled = list(case.requests)
        rng = random.Random(seed)
        rng.shuffle(shuffled)
        assert allocate(available_qty=available, requests=shuffled) == plan
