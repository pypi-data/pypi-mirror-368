from typing import List
from datetime import datetime, date
from pydantic import BaseModel, field_validator, ConfigDict

from ...core.enums import OrderingType


__all__ = (
    "Sorting",
    "SearchPayload",
    "NumberRange",
    "TimeRange",
    "DateRange",
    "BaseModelEnumValue",
    "ListPayloadResponse",
)


class Sorting(BaseModel):
    sort_by: str
    order_by: OrderingType = OrderingType.asc


class SearchPayload(BaseModel):
    page: int | None = 1
    items_per_page: int | None = 20
    sorting: List[Sorting] | None = None

    search: str | None = ""

    # Page number must be greater than or equal to one
    @field_validator("page")
    def validate_page(cls, page):
        if page is not None and page < 1:
            raise ValueError("page number must be greater than one")
        return page

    # Make limitation for items per page
    @field_validator("items_per_page")
    def validate_items_per_page(cls, items_per_page):
        if items_per_page is not None and items_per_page > 30:
            raise ValueError("Item per page should be lower than or equal to 30.")
        return items_per_page

    class Config:
        use_enum_values = True


class NumberRange(BaseModel):
    min: int | None = None
    max: int | None = None


class TimeRange(BaseModel):
    min: datetime | None = None
    max: datetime | None = None


class DateRange(BaseModel):
    min: date | None = None
    max: date | None = None


class BaseModelEnumValue(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class ListPayloadResponse(BaseModel):
    total_row: int | None = None
    last_page: int | None = None
    has_next: bool | None = None
