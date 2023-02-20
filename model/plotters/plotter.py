from pathlib import Path
from typing import Any
from ui.mplwidget import MplWidget


class Plotter:
    _plot: MplWidget

    def plotData(self, data: list[Any], options: Any) -> None:
        raise NotImplementedError("This is an abstract method.")

    def showEmptyText(self) -> None:
        self._plot.canvas.ax.clear()
        self._plot.canvas.ax.text(
            0.5,
            0.5,
            "No data to plot",
            horizontalalignment="center",
            verticalalignment="center",
        )
        self._plot.canvas.draw()

    def savePlot(self, file_path: Path):
        self._plot.canvas.fig.savefig(fname=file_path, format="png")
