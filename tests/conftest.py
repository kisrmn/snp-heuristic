from pathlib import Path

import pytest

from snp_alloc.io import Case, load_cases
from snp_alloc.models import Request

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="session")
def cases() -> dict[str, Case]:
    loaded, errors = load_cases(DATA_DIR)
    assert errors == []
    return {c.supply.case_id: c for c in loaded}


def req(rid: str, priority: int, demand: int, min_lot: int = 0, rounding: int = 1) -> Request:
    return Request(
        request_id=rid,
        priority=priority,
        demand_qty=demand,
        min_lot=min_lot,
        rounding_value=rounding,
    )
