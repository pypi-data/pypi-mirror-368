from dataclasses import dataclass


@dataclass
class SetupData:
    network: bool
    ambientLight: bool
    maxChargingPower: bool
