from dataclasses import dataclass

from .helpers import Color, ColorFull


@dataclass
class User:
    name: str
    admin: bool
    color: Color
    id: int
    publicKey: list[int] = None


@dataclass
class UserData:
    id: int
    user: User


@dataclass
class UserAddRequest:
    name: str
    password: str
    color: ColorFull
    admin: bool


@dataclass
class UserDeleteRequest:
    id: int
