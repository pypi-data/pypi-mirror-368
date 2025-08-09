from dataclasses import dataclass


@dataclass
class ConfigLoadSetRequest:
    maxCurrent: int


@dataclass
class ConfigLoadResponse:
    maxCurrent: int
