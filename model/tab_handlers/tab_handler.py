from pathlib import Path
from typing import Any
from model.plotters.plotter import Plotter

from model.utils.file_manager import newFile  # type: ignore
from ui.QtWaitingSpinner import QtWaitingSpinner
from model.utils.data_fetcher import DataFetcherWrapper  # type: ignore
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QMessageBox, QMainWindow


class TabHandler:
    _ui_options: Any
    _plotter: Plotter
    _ui_waiting_spinner: QtWaitingSpinner

    def resetOptions(self):
        self.setUIOptions(self._ui_options)

    def fetchAndVisualise(self):
        raise NotImplementedError("This is an abstract method.")

    def getUIOptions(self) -> Any:
        raise NotImplementedError("This is an abstract method.")

    def setUIOptions(self, options: Any):
        raise NotImplementedError("This is an abstract method.")

    def savePlot(self, window):
        filename = newFile(
            window,
            "Save plot as an image",
            "untitled.png",
            "Images (*.png *.xpm *.jpg)",
        )
        if filename == "":
            return
        self._plotter.savePlot(Path(filename))

    def _fetchInBackground(self, callable, param, callback):
        self._fetcher_wrapper = DataFetcherWrapper(self, callable, param, callback)
        self._ui_waiting_spinner.show()
        self._ui_waiting_spinner.start()
        QThreadPool.globalInstance().start(self._fetcher_wrapper)

    def _hasRequestError(self, data: dict[str, Any]) -> bool:
        if "error_message" in data:
            return True
        return False

    def _showErrorMessage(self, parent_view: QMainWindow, message: str):
        QMessageBox.about(parent_view, "Error", message)
