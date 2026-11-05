import pytest
from pydantic import ValidationError

from snp_alloc.allocate import allocate
from snp_alloc.models import Request
from tests.conftest import make_request


def test_proportional_within_tier():
    """Внутри уровня делим пропорционально спросу (30:10 -> 15:5); при «поровну» было бы 10:10."""
    requests = [make_request("A", 1, 30), make_request("B", 1, 10)]
    plan = allocate(20, requests)
    assert plan == {"A": 15, "B": 5}


def test_unusable_remainder_goes_to_lower_priority():
    """Если партия старшему не влезает, остаток уходит младшему; иначе 30 шт. простаивали бы."""
    requests = [make_request("HI", 1, 100, min_lot=50), make_request("LO", 2, 30)]
    plan = allocate(30, requests)
    assert plan == {"HI": 0, "LO": 30}


def test_overship_never_takes_from_lower_priority():
    """Перегруз только из остатка: младший получает свой спрос раньше, чем старший сверх demand."""
    requests = [make_request("HI", 1, 40, rounding=25), make_request("LO", 2, 25)]
    plan = allocate(50, requests)
    assert plan == {"HI": 25, "LO": 25}


def test_no_overship_beyond_one_lot():
    """Даже при избытке перегруз меньше одной партии; иначе склад раздавался бы без спроса."""
    requests = [
        make_request("A", 1, 40, rounding=25),
        make_request("B", 1, 20, min_lot=50, rounding=10),
    ]
    plan = allocate(1000, requests)
    assert plan == {"A": 50, "B": 0}


def test_duplicate_request_id_raises():
    """Дубли id делают dict-результат неоднозначным, поэтому это ошибка, а не тихая перезапись."""
    requests = [make_request("A", 1, 5), make_request("A", 2, 5)]
    with pytest.raises(ValueError, match="duplicate"):
        allocate(10, requests)


def test_negative_demand_rejected_by_schema():
    """Схема не пропускает отрицательный спрос; без неё -10 давало бы отрицательную долю."""
    with pytest.raises(ValidationError):
        Request(request_id="X", priority=1, demand_qty=-10, min_lot=0, rounding_value=1)
