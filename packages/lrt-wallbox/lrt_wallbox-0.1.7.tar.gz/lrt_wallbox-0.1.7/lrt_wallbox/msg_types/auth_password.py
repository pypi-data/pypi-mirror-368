from dataclasses import dataclass


@dataclass
class AuthPasswordRequest:
    name: str
    password: str


@dataclass
class AuthPasswordResponse:
    authenticated: bool
