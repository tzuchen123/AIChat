from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class StandardResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def ok(cls, data: Any) -> "StandardResponse":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, code: str, message: str) -> "StandardResponse":
        return cls(success=False, error=ErrorDetail(code=code, message=message))
