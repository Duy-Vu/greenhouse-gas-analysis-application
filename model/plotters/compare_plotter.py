from typing import Any
from datetime import datetime

import numpy as np
import matplotlib.dates as mdates
from ui.mplwidget import MplWidget

from model.plotters.plotter import Plotter
from model.data_models.station import Station  # type: ignore
from model.data_models.user_options import ComparePlotOptions


class ComparePlotter(Plotter):
    _plot: MplWidget

    def __init__(self, plot: MplWidget):
        self._plot = plot
        self._STATFI_ax = self._plot.canvas.ax
        self._SMEAR_ax = self._STATFI_ax.twinx()

    def plotData(
        self,
        data: list[Any],
        options: ComparePlotOptions,
    ) -> None:

        self._STATFI_ax.clear()
        self._SMEAR_ax.clear()

        STATFI_data, SMEAR_data = data

        if not STATFI_data:
            return
        STATFI_years: list[int] = [int(year) for year in STATFI_data[0].getYears()]
        nameTexts: list[str] = [figure.getNameText() for figure in STATFI_data]
        plotData: list[list[float]] = [
            list(figure.getYearlyData().values()) for figure in STATFI_data
        ]

        if self._check_plot_breakdown(SMEAR_data, STATFI_years):
            self._plot_breakdown_data(plotData, STATFI_years, nameTexts, SMEAR_data)
        else:
            self._plot_average_year_data(plotData, STATFI_years, nameTexts, SMEAR_data)

        self._design_canvas(options.gas.name)
        self._plot.canvas.draw()

    def _check_consecutive_years(self, year_list: list[int]):
        for i in range(len(year_list) - 1):
            if year_list[i + 1] - year_list[i] != 1:
                return False
        return True

    def _check_plot_breakdown(
        self, SMEAR_data: list[list[Station]], STATFI_years: list[int]
    ):
        # Only allow plot breakdown data if:
        #   - Consecutive years if there are more than 1 year (ex: 2011-2013)
        #   - Same year list on both STATFI and SMEAR

        if len(SMEAR_data) != len(STATFI_years):
            return False

        if len(STATFI_years) > 1 and (not self._check_consecutive_years(STATFI_years)):
            return False

        for station_period_data, STATFI_year in zip(SMEAR_data, STATFI_years):
            no_timestamp = 0
            for station in station_period_data:
                timestamps = station.getTimeStamps()
                if not timestamps:
                    no_timestamp += 1
                    if no_timestamp == len(station_period_data):
                        return False

                    continue

                if timestamps[0].year != STATFI_year:
                    return False

                continue  # No need to check further from other stations

        return True

    def _plot_breakdown_data(
        self,
        plotData: list[list[float]],
        STATFI_years: list[int],
        nameTexts: list[str],
        SMEAR_data: list[list[Station]],
    ):
        # SMEAR
        gas_data: dict[str, dict[str, list[float]]] = {}
        minmax_yearly_timestamp = []

        for station_period_data, STATFI_year in zip(SMEAR_data, STATFI_years):
            min_timestamp = datetime(STATFI_year, 12, 31)
            max_timestamp = datetime(STATFI_year, 1, 1)

            for station in station_period_data:
                station_name = station.getName()
                if station_name not in gas_data:
                    gas_data[station_name] = {"years": [], "values": []}

                station_timestamp = station.getTimeStamps()
                station_value = station.getConcentrations()
                if station_timestamp:
                    gas_data[station_name]["years"].extend(station_timestamp)
                    gas_data[station_name]["values"].extend(station_value)

                min_timestamp = min([min(station_timestamp), min_timestamp])
                max_timestamp = max([max(station_timestamp), max_timestamp])

            middle_timestamp = min_timestamp + (max_timestamp - min_timestamp) / 2

            minmax_yearly_timestamp.append(middle_timestamp)

        for station_name, station_data in gas_data.items():
            self._SMEAR_ax.plot(
                station_data["years"],
                station_data["values"],
                label=station_name,
                alpha=0.6,
            )

        # STATFI
        for i in np.arange(0, len(plotData)):
            self._STATFI_ax.plot(
                minmax_yearly_timestamp,
                plotData[i],
                label=nameTexts[i],
                marker="*",
                linewidth=1,
                markersize=10,
                linestyle="dashed",
            )

        new_datetime_format = "%d %b, %y \n %H:%M"
        self._STATFI_ax.xaxis.set_major_formatter(
            mdates.DateFormatter(new_datetime_format)
        )
        self._STATFI_ax.tick_params(
            axis="x",
            which="both",
            labelsize="x-small",
            labelrotation=45,
        )

    def _plot_average_year_data(
        self,
        plotData: list[list[float]],
        STATFI_years: list[int],
        nameTexts: list[str],
        SMEAR_data: list[list[Station]],
        max_marker_num: int = 30,
    ):
        # SMEAR
        gas_data: dict[str, dict[str, list[float]]] = {}
        for station_period_data in SMEAR_data:
            for station in station_period_data:
                station_name = station.getName()
                if station_name not in gas_data:
                    gas_data[station_name] = {"years": [], "values": []}

                station_timestamp = station.getTimeStamps()
                station_value = station.getConcentrations()
                if station_timestamp:
                    gas_data[station_name]["years"].append(station_timestamp[0].year)
                    gas_data[station_name]["values"].append(np.mean(station_value))

        for station_name, station_data in gas_data.items():
            self._SMEAR_ax.plot(
                station_data["years"],
                station_data["values"],
                label=station_name,
                marker="o" if len(station_data["years"]) < max_marker_num else None,
                linewidth=1,
                markersize=6 if len(station_data["years"]) < max_marker_num else None,
            )

        # STATFI
        for i in np.arange(0, len(plotData)):
            self._STATFI_ax.plot(
                STATFI_years,
                plotData[i],
                label=nameTexts[i],
                marker="x" if len(STATFI_years) < max_marker_num else None,
                linewidth=1,
                markersize=6,
                linestyle="dashed" if len(STATFI_years) < max_marker_num else None,
            )

        string_xticks = np.unique(np.rint(self._STATFI_ax.get_xticks()))
        self._STATFI_ax.set_xticks(string_xticks)

    def _design_canvas(self, gas_name: str):
        STATFI_color = "tab:green"
        self._STATFI_ax.set_xlabel("Timestamps")
        self._STATFI_ax.set_ylabel("STATFI", color=STATFI_color)
        self._STATFI_ax.tick_params(axis="y", labelcolor=STATFI_color)
        self._STATFI_ax.legend(loc="upper left", fontsize="x-small")

        SMEAR_color = "tab:red"
        self._SMEAR_ax.set_ylabel(
            f"{gas_name} concentration (ppm) (from SMEAR)", color=SMEAR_color
        )
        self._SMEAR_ax.tick_params(axis="y", labelcolor=SMEAR_color)
        self._SMEAR_ax.legend(loc="upper right", fontsize="x-small")

        self._plot.canvas.fig.tight_layout()
