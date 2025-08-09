from dataclasses import dataclass


@dataclass
class InfoSerialGetResponse:
    serialNumber: str


@dataclass
class ESP:
    major: int
    minor: int
    patch: int


@dataclass
class Atmel:
    major: int
    minor: int
    revision: int
    buildNumber: int


@dataclass
class InfoFirmwaresGetResponse:
    esp: ESP
    atmel: Atmel
