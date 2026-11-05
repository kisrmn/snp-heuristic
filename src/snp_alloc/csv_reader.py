import csv
import logging
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from snp_alloc.models import Request, RequestId, Supply

logger = logging.getLogger(__name__)


@dataclass
class Case:
    supply: Supply
    requests: list[Request] = field(default_factory=list)
    rejection_reasons: dict[RequestId, str] = field(default_factory=dict)


def _describe(error: ValidationError) -> str:
    messages = []
    for detail in error.errors():
        field_name = detail["loc"][0]
        messages.append(f"{field_name}: {detail['msg']}")
    return "; ".join(messages)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _load_supplies(path: Path) -> dict[str, Case]:
    cases: dict[str, Case] = {}
    for row in _read_rows(path=path):
        case_id = row.get("case_id", "")
        try:
            supply = Supply.model_validate(obj=row)
        except ValidationError as error:
            logger.warning(f"{case_id}: supply row skipped, {_describe(error=error)}")
            continue

        if case_id in cases:
            logger.warning(f"{case_id}: duplicate supply row skipped")
            continue
        cases[case_id] = Case(supply=supply)
    return cases


def _attach_requests(cases: dict[str, Case], path: Path) -> None:
    for row in _read_rows(path=path):
        case_id = row.get("case_id", "")
        request_id = row.get("request_id", "")
        case = cases.get(case_id)
        if case is None:
            logger.warning(f"{case_id}: request {request_id} has no supply row, skipped")
            continue

        try:
            request = Request.model_validate(obj=row)
        except ValidationError as error:
            case.rejection_reasons[request_id] = _describe(error=error)
            continue

        known_ids = {known.request_id for known in case.requests}
        if request.request_id in known_ids:
            case.rejection_reasons[request_id] = "duplicate request_id"
            continue
        case.requests.append(request)


def load_cases(data_dir: Path) -> list[Case]:
    cases = _load_supplies(path=data_dir / "supply.csv")
    _attach_requests(cases=cases, path=data_dir / "requests.csv")
    return [cases[case_id] for case_id in sorted(cases)]
