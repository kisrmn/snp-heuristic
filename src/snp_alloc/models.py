from pydantic import BaseModel, ConfigDict, Field


def round_down(qty: int, step: int) -> int:
    lots = qty // step
    return lots * step


def round_up(qty: int, step: int) -> int:
    lots = (qty + step - 1) // step
    return lots * step


class Request(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    request_id: str = Field(min_length=1)
    dest_location: str = ""
    priority: int = Field(ge=1)
    demand_qty: int = Field(ge=0)
    min_lot: int = Field(ge=0)
    rounding_value: int = Field(ge=0)

    @property
    def step(self) -> int:
        if self.rounding_value == 0:
            return 1
        return self.rounding_value

    @property
    def min_qty(self) -> int:
        lower_bound = max(self.min_lot, self.step)
        return round_up(lower_bound, self.step)

    @property
    def demand_rounded_down(self) -> int:
        return round_down(self.demand_qty, self.step)

    @property
    def demand_rounded_up(self) -> int:
        return round_up(self.demand_qty, self.step)


class Supply(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    case_id: str = Field(min_length=1)
    period: str
    item: str
    source_location: str
    available_qty: int = Field(ge=0)
