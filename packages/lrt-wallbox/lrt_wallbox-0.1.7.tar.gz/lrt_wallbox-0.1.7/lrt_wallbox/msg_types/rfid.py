from dataclasses import dataclass


@dataclass
class RfidGetResponse:
    name: str
    tagId: list[int]
    userId: int


@dataclass
class RfidScanRequest:
    duration: int


@dataclass
class RfidData:
    name: str
    tagId: list[int]


@dataclass
class RfidDeleteRequest:
    tagId: list[int]
