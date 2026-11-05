from pathlib import Path

import pytest

from snp_alloc.csv_reader import Case, load_cases
from snp_alloc.models import Request

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="session")
def cases() -> dict[str, Case]:
    loaded = load_cases(data_dir=DATA_DIR)
    return {case.supply.case_id: case for case in loaded}


def make_request(
    request_id: str,
    priority: int,
    demand_qty: int,
    min_lot: int = 0,
    rounding_value: int = 1,
) -> Request:
    return Request(
        request_id=request_id,
        priority=priority,
        demand_qty=demand_qty,
        min_lot=min_lot,
        rounding_value=rounding_value,
    )
