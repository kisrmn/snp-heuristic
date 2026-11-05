"""Схемы входа. Pydantic отсекает некорректные строки ещё до алгоритма."""

from pydantic import BaseModel, ConfigDict, Field


def ceil_to(qty: int, step: int) -> int:
    """Наименьшее кратное `step`, не меньшее `qty`."""
    return -(-qty // step) * step


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
        """Кратность отгрузки; 0 трактуем как «без ограничения», так же как min_lot=0."""
        return self.rounding_value or 1

    @property
    def min_qty(self) -> int:
        """Минимальная допустимая ненулевая отгрузка: min_lot, поднятый до кратности."""
        return ceil_to(max(self.min_lot, self.step), self.step)


class Supply(BaseModel):
    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    case_id: str = Field(min_length=1)
    period: str
    item: str
    source_location: str
    available_qty: int = Field(ge=0)
