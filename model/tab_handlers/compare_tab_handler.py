from typing import Any
from datetime import datetime
from model.factories.figure_factory import FigureFactory  # type: ignore
from model.factories.station_factory import StationFactory  # type: ignore
from model.tab_handlers.tab_handler import TabHandler
from model.utils.consts import (  # type: ignore
    ALL_SMEAR_STATIONS,
    ALL_STATFI_LABELS,
    YEAR_END_STATFI_DATA,
    YEAR_START_STATFI_DATA,
)
from model.data_models.user_options import SMEARGas, CompareOptions, ComparePlotOptions
from model.plotters.compare_plotter import ComparePlotter
from model.utils.data_fetcher import DataFetcher  # type: ignore

from ui.mplwidget import MplWidget
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSlot
from ui.QtWaitingSpinner import QtWaitingSpinner
from PyQt6.QtWidgets import (
    QMainWindow,
    QRadioButton,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QButtonGroup,
)


class CompareTabHandler(TabHandler, QObject):
    _ui_options: CompareOptions

    def __init__(
        self,
        parent_view: QMainWindow,
        ui_STATFI_figures_list: QListWidget,
        ui_STATFI_years_list: QListWidget,
        ui_SMEAR_gas_radio_buttons: QGroupBox,
        ui_SMEAR_stations_list: QListWidget,
        ui_SMEAR_years_list: QListWidget,
        _ui_fetch_data_button: QPushButton,
        ui_plot: MplWidget,
        ui_save_plot_button: QPushButton,
    ):
        QObject.__init__(self)
        self._parent_view = parent_view
        self._ui_STATFI_figures_list = ui_STATFI_figures_list
        self._ui_STATFI_years_list = ui_STATFI_years_list
        self._ui_SMEAR_gas_radio_buttons = ui_SMEAR_gas_radio_buttons
        self._ui_SMEAR_stations_list = ui_SMEAR_stations_list
        self._ui_SMEAR_years_list = ui_SMEAR_years_list
        self._ui_SMEAR_gas_radio_buttons_group = QButtonGroup()
        self._ui_fetch_data_button = _ui_fetch_data_button
        self._ui_save_plot_button = ui_save_plot_button
        self._ui_waiting_spinner = QtWaitingSpinner(self._parent_view)
        self._plotter = ComparePlotter(ui_plot)

        self._setupComponents()
        self._ui_options = self.getUIOptions()
        self._mightToggleFetchButton()

    def fetchAndVisualise(self):
        self._fetchInBackground(
            DataFetcher.fetchComparisonData, self.getUIOptions(), "_visualise"
        )

    def getUIOptions(self) -> CompareOptions:
        # STATFI
        figures = self._ui_STATFI_figures_list.selectedItems()
        STATFI_years = self._ui_STATFI_years_list.selectedItems()

        # SMEAR
        gas: SMEARGas = self._getSelectedSMEARGas()
        stations: list[QListWidgetItem] = self._ui_SMEAR_stations_list.selectedItems()
        SMEAR_years = self._ui_SMEAR_years_list.selectedItems()

        return CompareOptions(
            STATFI_figure_names=[figure.text() for figure in figures],
            STATFI_years=[year.text() for year in STATFI_years],
            SMEAR_gas=gas,
            SMEAR_stations=[station.text() for station in stations],
            SMEAR_years=[year.text() for year in SMEAR_years],
        )

    def setUIOptions(self, options: CompareOptions):
        self._ui_options = options

        # STATFI
        self._ui_STATFI_figures_list.clearSelection()
        self._ui_STATFI_years_list.clearSelection()

        for figure_name in options.STATFI_figure_names:
            self._ui_STATFI_figures_list.findItems(
                figure_name, QtCore.Qt.MatchFlag.MatchExactly
            )[0].setSelected(True)
        for year in options.STATFI_years:
            self._ui_STATFI_years_list.findItems(
                year, QtCore.Qt.MatchFlag.MatchExactly
            )[0].setSelected(True)

        # SMEAR
        self._ui_SMEAR_stations_list.clearSelection()
        self._ui_SMEAR_years_list.clearSelection()

        self._ui_SMEAR_gas_radio_buttons.findChild(  # type: ignore
            QRadioButton, f"compare_{options.SMEAR_gas.value.lower()}_radio_button"
        ).setChecked(True)
        for station in options.SMEAR_stations:
            # Avoid adding duplicate station.
            if not len(
                self._ui_SMEAR_stations_list.findItems(
                    station, QtCore.Qt.MatchFlag.MatchExactly
                )
            ):
                self._ui_SMEAR_stations_list.addItem(station)
            # Avoid self._ui_SMEAR_stations_list.findItems(
            # IndexError: list index out of range
            # print(len(self._ui_SMEAR_stations_list))
            self._ui_SMEAR_stations_list.findItems(
                station, QtCore.Qt.MatchFlag.MatchExactly
            )[0].setSelected(True)

    def _getSelectedSMEARGas(self) -> SMEARGas:
        return SMEARGas[self._ui_SMEAR_gas_radio_buttons_group.checkedButton().text()]

    def _addAvailableStationsToSelectionList(self):
        self._ui_SMEAR_stations_list.clear()
        self._ui_SMEAR_years_list.clear()
        for station in ALL_SMEAR_STATIONS:
            if self._getSelectedSMEARGas().value in ALL_SMEAR_STATIONS[station]:
                self._ui_SMEAR_stations_list.addItem(station)

    def _fetchMetaData(self):
        self._SMEARperiodStarts: list[str] = []
        self._SMEARperiodEnds: list[str] = []
        if self._ui_SMEAR_stations_list.selectedItems():
            stations = self._ui_SMEAR_stations_list.selectedItems()
            for station in stations:
                gas = self._getSelectedSMEARGas().value
                data = ALL_SMEAR_STATIONS[station.text()][gas]
                self._fetchInBackground(
                    DataFetcher.fetchSMEARVariableMetadata,
                    {"table": data["table"], "variable": data["variable"]},
                    "_setBoundariesToSMEARYearsList",
                )

    @pyqtSlot(dict)
    def _visualise(self, compare_data: dict[str, Any]):
        self._ui_waiting_spinner.stop()
        if not compare_data:
            return

        if self._hasRequestError(compare_data):
            self._showErrorMessage(
                self._parent_view, str(compare_data["error_message"])
            )
            return

        figures = FigureFactory.build(compare_data["STATFI"][0])
        stations = [
            StationFactory.build(SMEARdata) for SMEARdata in compare_data["SMEAR"]
        ]
        self._plotter.plotData(
            [figures, stations], ComparePlotOptions(self._getSelectedSMEARGas())
        )

        self._ui_options = self.getUIOptions()
        self._enablePlotActionButtons()

    @pyqtSlot(dict)
    def _setBoundariesToSMEARYearsList(self, metadata: dict[str, Any]):
        self._ui_waiting_spinner.stop()
        if self._hasRequestError(metadata):
            self._showErrorMessage(self._parent_view, str(metadata["error_message"]))
            return
        self._ui_SMEAR_years_list.clear()
        self._parent_view.setEnabled(True)
        self._SMEARperiodStarts.append(metadata["periodStart"])
        if metadata["periodEnd"] is not None:
            self._SMEARperiodEnds.append(metadata["periodEnd"])

        periodStart = max(self._SMEARperiodStarts)
        yearStart = datetime.strptime(periodStart, "%Y-%m-%dT%H:%M:%S.%f").strftime(
            "%Y"
        )

        yearEnd = datetime.now().strftime("%Y")
        if self._SMEARperiodEnds:
            periodEnd = min(self._SMEARperiodEnds)
            yearEnd = datetime.strptime(periodEnd, "%Y-%m-%dT%H:%M:%S.%f").strftime(
                "%Y"
            )

        for year in range(int(yearStart), int(yearEnd) + 1):
            self._ui_SMEAR_years_list.addItem(str(year))

        # Set whatever year in current options as selected. The for loop above already adds the year.
        for year in self._ui_options.SMEAR_years:
            # TODO: Years have to be added before they can be found and selected (though yet to be highlighted
            # in the UI) even though station has already been selected and metadata has been fetched
            self._ui_SMEAR_years_list.findItems(year, QtCore.Qt.MatchFlag.MatchExactly)[
                0
            ].setSelected(True)

    def _setupComponents(self):
        # STATFI
        for label_name in ALL_STATFI_LABELS.keys():
            self._ui_STATFI_figures_list.addItem(label_name)
        for i in range(YEAR_START_STATFI_DATA, YEAR_END_STATFI_DATA + 1):
            self._ui_STATFI_years_list.addItem(str(i))

        self._ui_STATFI_figures_list.itemSelectionChanged.connect(
            self._mightToggleFetchButton
        )
        self._ui_STATFI_years_list.itemSelectionChanged.connect(
            self._mightToggleFetchButton
        )

        # SMEAR
        for station in ALL_SMEAR_STATIONS:
            self._ui_SMEAR_stations_list.addItem(station)

        self._ui_SMEAR_stations_list.sortItems()
        self._ui_SMEAR_stations_list.itemSelectionChanged.connect(
            self._mightToggleFetchButton
        )
        self._ui_SMEAR_years_list.itemSelectionChanged.connect(
            self._mightToggleFetchButton
        )

        radio_buttons: list = self._ui_SMEAR_gas_radio_buttons.findChildren(
            QRadioButton
        )
        for button in radio_buttons:
            self._ui_SMEAR_gas_radio_buttons_group.addButton(button)

        self._ui_SMEAR_gas_radio_buttons_group.buttonClicked.connect(
            self._addAvailableStationsToSelectionList
        )

        self._ui_SMEAR_stations_list.itemSelectionChanged.connect(self._fetchMetaData)

    def _isFiguresListValid(self) -> bool:
        if self._ui_STATFI_figures_list.selectedItems():
            return True
        return False

    def _isStationsListValid(self) -> bool:
        if self._ui_SMEAR_stations_list.selectedItems():
            return True
        return False

    def _isYearsListValid(self) -> bool:
        if (
            self._ui_STATFI_years_list.selectedItems()
            and self._ui_SMEAR_years_list.selectedItems()
        ):
            return True
        return False

    def _mightToggleFetchButton(self):
        should_enable = (
            self._isFiguresListValid()
            and self._isStationsListValid()
            and self._isYearsListValid()
        )
        self._ui_fetch_data_button.setEnabled(should_enable)
        return

    def _enablePlotActionButtons(self):
        if not self._ui_save_plot_button.isEnabled():
            self._ui_save_plot_button.setEnabled(True)
