from typing import Literal, Annotated, Union
from uuid import UUID

from pydantic import BaseModel, Field

from .models import NumberRange, TimeRange

__all__ = (
    "FilterSelectValue",
    "FilterOption",
    "SelectedFilter",
    "SearchResponseAvailableFilters",
    "SearchResponseSelectedFilters",
)


class FilterOptionBase(BaseModel):
    label: str
    name: str


class FilterSelectValue(BaseModel):
    label: str
    value: UUID | bool | str | None = None


class FilterOptionSelect(FilterOptionBase):
    type: Literal["select"]
    value: list[FilterSelectValue]


class FilterOptionDate(FilterOptionBase):
    type: Literal["date"]
    value: TimeRange


class FilterOptionNumber(FilterOptionBase):
    type: Literal["number"]
    value: NumberRange
    
    
FilterOption = Annotated[
    Union[FilterOptionSelect, FilterOptionDate, FilterOptionNumber],
    Field(discriminator='type')
]


class SearchResponseAvailableFilters(BaseModel):
    available_filters: list[FilterOption]


class SelectedFilterBase(BaseModel):
    label: str
    name: str


class SelectedFilterSelect(SelectedFilterBase):
    type: Literal["select"]
    value: UUID | bool | str | None = None


class SelectedFilterDate(SelectedFilterBase):
    type: Literal["date"]
    value: TimeRange


class SelectedFilterNumber(SelectedFilterBase):
    type: Literal["number"]
    value: NumberRange


class SelectedFilterSearch(SelectedFilterBase):
    type: Literal["search"]
    value: str


SelectedFilter = Annotated[
    Union[SelectedFilterSelect, SelectedFilterDate, SelectedFilterNumber, SelectedFilterSearch],
    Field(discriminator='type')
]


class SearchResponseSelectedFilters(BaseModel):
    selected_filters: list[SelectedFilter]
