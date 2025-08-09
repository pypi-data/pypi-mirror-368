from dataclasses import dataclass, field
from typing import List

from cbor2 import CBORTag


@dataclass
class TransactionEntry:
    ocppCpState: str
    connectionState: str
    currentChargeRate: int
    authorizationState: str
    secondsSinceChargeStart: int
    currentTransactionEnergy: int


@dataclass
class TransactionStopResponse:
    energy: int
    endTime: str
    startTime: str
    startedBy: list[int]
    sessionNumber: int


@dataclass
class TransactionStartRequest:
    tag_id: List[int] = field(default_factory=list)

    def to_array(self):
        return self.tag_id
