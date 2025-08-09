from dataclasses import dataclass


@dataclass
class UtilRestartData:
    restart: bool = True


@dataclass
class UtilAtmelRestartResponse:
    status: bool = True


# TODO: NOT TESTED ONE
@dataclass
class FactoryResetResponse:
    pass
