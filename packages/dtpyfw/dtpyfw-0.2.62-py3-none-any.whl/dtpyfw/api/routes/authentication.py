from typing import List
from dataclasses import dataclass
from enum import Enum
from fastapi import Depends, Request
from fastapi.security import APIKeyHeader, APIKeyQuery

from ...core.exception import RequestException


__all__ = (
    "AuthType",
    "Auth",
    "auth_data_class_to_dependency",
)


class AuthType(Enum):
    HEADER = "header"
    QUERY = "query"


@dataclass
class Auth:
    auth_type: AuthType
    header_key: str | None = None
    real_value: str | None = None


class HeaderAuthChecker:
    def __init__(self, key: str, real_value: str):
        self.key = key
        self.real_value = real_value

    def __call__(self, request: Request):
        controller = f"{__name__}.HeaderAuthChecker.__call__"
        auth_token = request.headers.get(self.key)
        if auth_token is None or auth_token != self.real_value:
            raise RequestException(
                controller=controller,
                message="Wrong credential.",
                status_code=403,
            )


class QueryAuthChecker:
    def __init__(self, key: str, real_value: str):
        self.key = key
        self.real_value = real_value

    def __call__(self, request: Request):
        controller = f"{__name__}.QueryAuthChecker.__call__"
        auth_token = request.query_params.get(self.key)
        if auth_token is None or auth_token != self.real_value:
            raise RequestException(
                controller=controller,
                message="Wrong credential.",
                status_code=403,
            )


def auth_data_class_to_dependency(authentication: Auth) -> List[Depends]:
    if authentication.auth_type == AuthType.HEADER:
        checker = HeaderAuthChecker(
            key=authentication.header_key, real_value=authentication.real_value
        )
        return [
            Depends(checker),
            Depends(APIKeyHeader(name=authentication.header_key)),
        ]
    elif authentication.auth_type == AuthType.QUERY:
        checker = QueryAuthChecker(
            key=authentication.header_key, real_value=authentication.real_value
        )
        return [
            Depends(checker),
            Depends(APIKeyQuery(name=authentication.header_key)),
        ]
    else:
        return []
