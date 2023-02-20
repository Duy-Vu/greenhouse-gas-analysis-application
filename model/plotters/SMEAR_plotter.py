import datetime
import matplotlib.dates as mdates  # type: ignore
from model.data_models.station import Station
from model.data_models.user_options import SMEARAggregation, SMEARPlotOptions
from model.plotters.plotter import Plotter
from ui.mplwidget import MplWidget


class SMEARPlotter(Plotter):
    _plot: MplWidget

    def __init__(self, plot: MplWidget):
        self._plot = plot

    def plotData(self, data: list[Station], options: SMEARPlotOptions):
        self._plot.canvas.ax.clear()
        for station in data:
            if self._isStationDataAvailable(station):
                gas_timestamps = station.getTimeStamps()
                gas_values = station.getConcentrations()
                station_name = station.getName()
                self._plotStationLine(gas_timestamps, gas_values, station_name)

        aggregation_string = self._getAggregationString(options)
        self._plot.canvas.ax.set_xlabel("Timestamps")
        self._plot.canvas.ax.set_ylabel(
            f"{aggregation_string} {options.gas.name} concentration (ppm)"
        )
        self._plot.canvas.ax.set_title(
            f"{aggregation_string} {options.gas.name} concentration between stations"
        )
        self._plot.canvas.ax.tick_params(
            axis="x",
            which="both",
            labelsize="x-small",
            labelrotation=45,
        )

        new_datetime_format = "%d %b, %y \n %H:%M"
        self._plot.canvas.ax.xaxis.set_major_formatter(
            mdates.DateFormatter(new_datetime_format)
        )
        self._plot.canvas.ax.legend(loc="best", fontsize="x-small")
        self._plot.canvas.fig.tight_layout()
        self._plot.canvas.draw()

    def _plotStationLine(
        self,
        timestamps: list[datetime.datetime],
        values: list[float],
        station_name: str,
        max_marker_num: int = 20,
    ):
        self._plot.canvas.ax.plot(
            timestamps,
            values,
            label=station_name,
            marker="o" if len(timestamps) < max_marker_num else None,
            markersize=4 if len(timestamps) < max_marker_num else None,
        )

    def _getAggregationString(self, options: SMEARPlotOptions):
        aggregation_string = (
            ""
            if options.aggregation_method == SMEARAggregation.NONE
            else options.aggregation_method.name.capitalize()
        )
        return aggregation_string

    def _isStationDataAvailable(self, station: Station):
        return True if station.getConcentrations() else False
