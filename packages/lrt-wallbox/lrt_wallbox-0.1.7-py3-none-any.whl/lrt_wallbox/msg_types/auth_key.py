from dataclasses import dataclass


@dataclass
class AuthKeyInitRequest:
    user_id: int


@dataclass
class AuthKeyInitResponse:
    challenge: list[int]


@dataclass
class AuthKeyResponseRequest:
    encrypted: bytes


@dataclass
class AuthKeyResponseResponse:
    authenticated: bool
