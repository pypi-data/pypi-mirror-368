from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

from ..exceptions import WallboxError


@dataclass
class ErrorData:
    kind: str
    message: str
    field: Optional[str] = None


T = TypeVar("T")


@dataclass
class MessageRequest(Generic[T]):
    key: str
    body: Optional[T] = None


@dataclass
class MessageResponse(Generic[T]):
    key: str
    body: Optional[T] = None
    error: Optional[ErrorData] = None

    def raise_if_error(self):
        if self.error:
            raise WallboxError(kind=self.error.kind, message=self.error.message, field=self.error.field)
        return self.body
