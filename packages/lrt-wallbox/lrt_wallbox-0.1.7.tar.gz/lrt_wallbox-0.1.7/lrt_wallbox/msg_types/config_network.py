from dataclasses import dataclass


@dataclass
class ConfigNetworkStatusResponse:
    wlan: str
    ethernet: str


@dataclass
class Wifi:
    mode: str
    ssid: str
    password: str


@dataclass
class Ethernet:
    mode: str


@dataclass
class ConfigNetworkGetResponse:
    wifi: Wifi
    ethernet: Ethernet
