import numpy as np
from model.data_models.figure import Figure
from model.data_models.user_options import STATFIPlotOptions, STATFIPlotType
from model.plotters.plotter import Plotter
from ui.mplwidget import MplWidget


class STATFIPlotter(Plotter):
    _plot: MplWidget

    def __init__(self, plot):
        self._plot: MplWidget = plot

    def plotData(self, data: list[Figure], options: STATFIPlotOptions):
        if not data:
            return
        years: list[int] = data[0].getYears()
        nameTexts: list[str] = [figure.getNameText() for figure in data]
        plotData: list[list[float]] = [
            list(figure.getYearlyData().values()) for figure in data
        ]

        self._plot.canvas.ax.clear()
        if options.plot_type == STATFIPlotType.BAR_CHART:
            self._plotBarChart(plotData, years, nameTexts)
        elif options.plot_type == STATFIPlotType.LINE_GRAPH:
            self._plotLineGraph(plotData, years, nameTexts)
        else:
            raise ValueError("Unknown plot_by value")

    def _plotBarChart(
        self, data: list[list[float]], years: list[int], nameTexts: list[str]
    ):
        year_label_locations = np.arange(len(years))
        x_location_increment = 0.25

        self._plot.canvas.ax.set_xticks(
            year_label_locations + x_location_increment, years
        )
        for i in np.arange(0, len(data)):
            self._plot.canvas.ax.bar(
                year_label_locations + x_location_increment * i,
                data[i],
                width=x_location_increment,
                label=nameTexts[i],
            )
        self._plot.canvas.ax.legend()
        self._plot.canvas.draw()

    def _plotLineGraph(
        self, data: list[list[float]], years: list[int], nameTexts: list[str]
    ):
        for i in np.arange(0, len(data)):
            self._plot.canvas.ax.plot(
                years,
                data[i],
                label=nameTexts[i],
                marker="o",
                linewidth=1,
                markersize=4,
            )
        self._plot.canvas.ax.set_xticks(years)
        self._plot.canvas.ax.legend()
        self._plot.canvas.draw()
