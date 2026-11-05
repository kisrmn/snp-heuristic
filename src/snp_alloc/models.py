from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

RequestId: TypeAlias = str


def round_down(qty: int, step: int) -> int:
    lots = qty // step
    return lots * step


def round_up(qty: int, step: int) -> int:
    lots, remainder = divmod(qty, step)
    if remainder:
        lots += 1
    return lots * step


class Request(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    request_id: RequestId = Field(min_length=1)
    dest_location: str = ""
    priority: int = Field(ge=1)
    demand_qty: int = Field(ge=0)
    min_lot: int = Field(ge=0)
    rounding_value: int = Field(ge=0)

    @property
    def sort_key(self) -> tuple[int, RequestId]:
        return self.priority, self.request_id

    @property
    def rounding_step(self) -> int:
        if self.rounding_value == 0:
            return 1
        return self.rounding_value

    @property
    def min_shipment_qty(self) -> int:
        lower_bound = max(self.min_lot, self.rounding_step)
        return round_up(qty=lower_bound, step=self.rounding_step)

    @property
    def demand_rounded_down(self) -> int:
        return round_down(qty=self.demand_qty, step=self.rounding_step)

    @property
    def demand_rounded_up(self) -> int:
        return round_up(qty=self.demand_qty, step=self.rounding_step)


class Supply(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    case_id: str = Field(min_length=1)
    period: str
    item: str
    source_location: str
    available_qty: int = Field(ge=0)
