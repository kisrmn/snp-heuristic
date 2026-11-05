from hypothesis import given
from hypothesis import strategies as st

from snp_alloc.allocate import allocate
from snp_alloc.models import Request

request_strategy = st.builds(
    Request,
    request_id=st.text("ABCDEFGH", min_size=1, max_size=3),
    priority=st.integers(1, 3),
    demand_qty=st.integers(0, 200),
    min_lot=st.integers(0, 120),
    rounding_value=st.integers(0, 30),
)
requests_strategy = st.lists(
    request_strategy,
    max_size=6,
    unique_by=lambda request: request.request_id,
)


@given(available=st.integers(0, 600), requests=requests_strategy, data=st.data())
def test_hard_constraints_on_random_input(available, requests, data):
    """Три требования задания и перегруз < 1 партии на случайных данных; ловит краевые случаи."""
    plan = allocate(available, requests)

    shipped_total = sum(plan.values())
    assert shipped_total <= available

    for request in requests:
        shipped = plan[request.request_id]
        assert shipped <= request.demand_rounded_up
        if shipped == 0:
            continue
        assert shipped >= request.min_qty
        assert shipped % request.step == 0

    shuffled = data.draw(st.permutations(requests))
    assert allocate(available, shuffled) == plan
