"""Common response schemas for API endpoints."""

from typing import Any, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, RootModel

__all__ = (
    "ResponseBase",
    "SuccessResponse",
    "FailedResponse",
    "BoolResponse",
    "StrResponse",
    "UUIDResponse",
    "ListResponse",
    "ListOfDictResponse",
    "DictResponse",
)


T = TypeVar("T")


class ResponseBase(BaseModel):
    """Base structure returned by every API endpoint."""

    success: bool


class SuccessResponse(ResponseBase, Generic[T]):
    """Successful API response wrapper."""

    success: bool = True
    data: Any


class FailedResponse(ResponseBase):
    """Error response wrapper."""

    success: bool = False
    message: str


class BoolResponse(RootModel[bool]):
    pass


class StrResponse(RootModel[str]):
    pass


class UUIDResponse(RootModel[UUID]):
    pass


class ListResponse(RootModel[list]):
    pass


class ListOfDictResponse(RootModel[list[dict[str, Any]]]):
    pass


class DictResponse(RootModel[dict[str, Any]]):
    pass
