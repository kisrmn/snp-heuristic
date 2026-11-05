"""Чтение CSV в кейсы. Невалидные строки не роняют расчёт, а попадают в `rejected`/`errors`."""

import csv
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from snp_alloc.models import Request, Supply


@dataclass
class Case:
    supply: Supply
    requests: list[Request] = field(default_factory=list)
    rejected: dict[str, str] = field(default_factory=dict)  # request_id -> причина


def _reason(err: ValidationError) -> str:
    return "; ".join(f"{e['loc'][0]}: {e['msg']}" for e in err.errors())


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_cases(data_dir: Path) -> tuple[list[Case], list[str]]:
    """Кейсы в порядке case_id и список ошибок уровня файла/кейса."""
    cases: dict[str, Case] = {}
    errors: list[str] = []
    for row in _rows(data_dir / "supply.csv"):
        cid = row.get("case_id", "")
        try:
            supply = Supply.model_validate(row)
        except ValidationError as e:
            errors.append(f"{cid}: supply skipped ({_reason(e)})")
            continue
        if cid in cases:
            errors.append(f"{cid}: duplicate supply row skipped")
            continue
        cases[cid] = Case(supply)

    for row in _rows(data_dir / "requests.csv"):
        cid, rid = row.get("case_id", ""), row.get("request_id", "")
        case = cases.get(cid)
        if case is None:
            errors.append(f"{cid}: request {rid} has no supply row, skipped")
            continue
        try:
            req = Request.model_validate(row)
        except ValidationError as e:
            case.rejected[rid] = _reason(e)
            continue
        if any(r.request_id == req.request_id for r in case.requests):
            case.rejected[rid] = "duplicate request_id"
            continue
        case.requests.append(req)
    return [cases[cid] for cid in sorted(cases)], errors
