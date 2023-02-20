from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import ClassVar

from model.utils.consts import ALL_SMEAR_STATIONS, ALL_STATFI_LABELS  # type: ignore


class SMEARGas(Enum):
    CO2 = "CO2"
    SO2 = "SO2"
    NO = "NO"


class SMEARAggregation(Enum):
    NONE = "NONE"
    MIN = "MIN"
    MAX = "MAX"
    AVG = "ARITHMETIC"


class STATFIPlotType(Enum):
    LINE_GRAPH = "LINE"
    BAR_CHART = "BAR"


@dataclass
class SMEAROptions:
    gas: SMEARGas
    aggregation_method: SMEARAggregation
    start_date_time: datetime
    end_date_time: datetime
    stations: list[str]
    interval: str = "60"
    variable_names: ClassVar[list[str]] = []
    table_names: ClassVar[list[str]] = []

    # Convert station names and gas to table and variable names, which
    # are used in SMEAR API.
    def __post_init__(self):
        self.table_names = [
            self._getTableName(station_name) for station_name in self.stations
        ]
        self.variable_names = [
            self._getVariableName(station_name) for station_name in self.stations
        ]

    def _getTableName(self, station_name: str):
        return ALL_SMEAR_STATIONS[station_name][self.gas.value]["table"]

    def _getVariableName(self, station_name: str):
        return ALL_SMEAR_STATIONS[station_name][self.gas.value]["variable"]


@dataclass
class STATFIOptions:
    figure_names: list[str]
    years: list[str]
    plot_type: STATFIPlotType = STATFIPlotType.LINE_GRAPH
    figure_ids: ClassVar[list[str]] = []

    def __post_init__(self):
        self.figure_ids = [
            ALL_STATFI_LABELS[figure_name] for figure_name in self.figure_names
        ]


@dataclass
class CompareOptions:
    STATFI_figure_names: list[str]
    STATFI_years: list[str]

    SMEAR_gas: SMEARGas
    SMEAR_stations: list[str]
    SMEAR_years: list[str]


@dataclass
class AllTabsOptions:
    SMEAR: SMEAROptions
    STATFI: STATFIOptions
    compare: CompareOptions


@dataclass
class SMEARPlotOptions:
    gas: SMEARGas
    aggregation_method: SMEARAggregation


@dataclass
class STATFIPlotOptions:
    plot_type: STATFIPlotType


@dataclass
class ComparePlotOptions:
    gas: SMEARGas
