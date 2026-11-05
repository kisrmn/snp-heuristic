from hypothesis import given
from hypothesis import strategies as st

from snp_alloc.allocate import allocate
from snp_alloc.models import Request, ceil_to

requests_st = st.lists(
    st.builds(
        Request,
        request_id=st.text("ABCDEFGH", min_size=1, max_size=3),
        priority=st.integers(1, 3),
        demand_qty=st.integers(0, 200),
        min_lot=st.integers(0, 120),
        rounding_value=st.integers(0, 30),
    ),
    max_size=6,
    unique_by=lambda r: r.request_id,
)


@given(available=st.integers(0, 600), requests=requests_st, data=st.data())
def test_hard_constraints_on_random_input(available, requests, data):
    """Три требования задания и перегруз < 1 партии на случайных данных; ловит краевые случаи."""
    plan = allocate(available, requests)
    assert sum(plan.values()) <= available
    for r in requests:
        q = plan[r.request_id]
        assert q == 0 or (q >= r.min_qty and q % r.step == 0)
        assert q <= ceil_to(r.demand_qty, r.step)
    assert allocate(available, data.draw(st.permutations(requests))) == plan
