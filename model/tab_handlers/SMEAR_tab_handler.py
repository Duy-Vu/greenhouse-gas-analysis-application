from datetime import datetime
from typing import Any
from model.data_models.station import Station
from model.data_models.user_options import (
    SMEARAggregation,
    SMEARGas,
    SMEAROptions,
    SMEARPlotOptions,
)
from model.dialog_handlers.SMEAR_dialog_handler import SMEARDialogHandler  # type: ignore
from model.factories.station_factory import StationFactory  # type: ignore
from model.plotters.SMEAR_plotter import SMEARPlotter
from model.tab_handlers.tab_handler import TabHandler
from model.utils.consts import ALL_SMEAR_STATIONS  # type: ignore
from model.utils.data_fetcher import DataFetcher  # type: ignore
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, pyqtSlot
from PyQt6.QtWidgets import (
    QDateTimeEdit,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QButtonGroup,
)

from ui.mplwidget import MplWidget
from ui.QtWaitingSpinner import QtWaitingSpinner
from PyQt6.QtWidgets import QMainWindow


class SMEARTabHandler(TabHandler, QObject):
    _ui_options: SMEAROptions
    _ui_gas_radio_buttons: QGroupBox
    _ui_stations_list: QListWidget
    _ui_start_time_edit: QDateTimeEdit
    _ui_end_time_edit: QDateTimeEdit
    _ui_aggregation_radio_buttons: QGroupBox
    _ui_summary_button: QPushButton
    _ui_fetch_data_button: QPushButton
    _ui_save_plot_button: QPushButton
    _plotter: SMEARPlotter
    _parent_view: QMainWindow

    _stations: list[Station] = []

    def __init__(
        self,
        parent_view: QMainWindow,
        ui_gas_radio_buttons: QGroupBox,
        ui_stations_list: QListWidget,
        ui_start_time_edit: QDateTimeEdit,
        ui_end_time_edit: QDateTimeEdit,
        ui_aggregration_radio_buttons: QGroupBox,
        ui_fetch_data_button: QPushButton,
        ui_plot: MplWidget,
        ui_summary_button: QPushButton,
        ui_save_plot_button: QPushButton,
    ):
        QObject.__init__(self)
        self._parent_view = parent_view
        self._ui_gas_radio_buttons = ui_gas_radio_buttons
        self._ui_stations_list = ui_stations_list
        self._ui_start_time_edit = ui_start_time_edit
        self._ui_end_time_edit = ui_end_time_edit
        self._ui_aggregation_radio_buttons = ui_aggregration_radio_buttons
        self._ui_summary_button = ui_summary_button
        self._ui_fetch_data_button = ui_fetch_data_button
        self._ui_save_plot_button = ui_save_plot_button
        self._ui_waiting_spinner = QtWaitingSpinner(self._parent_view)
        self._plotter = SMEARPlotter(ui_plot)
        self._ui_gas_radio_buttons_group = QButtonGroup()

        self._setupComponents()
        self._ui_options = self.getUIOptions()
        self._stations = []
        self._mightToggleFetchButton()

    def fetchAndVisualise(self):
        self._fetchInBackground(
            DataFetcher.fetchSMEARData, self.getUIOptions(), "_visualise"
        )

    def getUIOptions(self) -> SMEAROptions:
        gas: SMEARGas = self._getSelectedSMEARGas()
        stations: list[QListWidgetItem] = self._ui_stations_list.selectedItems()
        start_date_time: datetime = self._ui_start_time_edit.dateTime().toPyDateTime()
        end_date_time: datetime = self._ui_end_time_edit.dateTime().toPyDateTime()
        aggregation: SMEARAggregation = self._getSelectedAggregationMethod()
        return SMEAROptions(
            gas=gas,
            aggregation_method=aggregation,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            stations=[station.text() for station in stations],
        )

    def setUIOptions(self, options: SMEAROptions):
        self._ui_options = options

        self._ui_gas_radio_buttons.findChild(  # type: ignore
            QRadioButton, f"SMEAR_{options.gas.value.lower()}_radio_button"
        ).setChecked(True)
        self._ui_stations_list.clearSelection()
        for station in options.stations:
            if not self._ui_stations_list.findItems(
                station, QtCore.Qt.MatchFlag.MatchExactly
            ):
                self._ui_stations_list.addItem(station)
            self._ui_stations_list.findItems(station, QtCore.Qt.MatchFlag.MatchExactly)[
                0
            ].setSelected(True)
        self._ui_start_time_edit.setDateTime(
            options.start_date_time.replace(microsecond=0)
        )
        self._ui_end_time_edit.setDateTime(options.end_date_time.replace(microsecond=0))
        self._ui_aggregation_radio_buttons.findChild(  # type: ignore
            QRadioButton,
            f"SMEAR_{options.aggregation_method.name.lower()}_radio_button",
        ).setChecked(True)

    def showAggregatedInfo(self):
        self.resetOptions()
        self._SMEAR_dialog_handler = SMEARDialogHandler(
            self._stations, self._ui_options
        )
        self._SMEAR_dialog_handler.setupSummaryDialog()

    @pyqtSlot(dict)
    def _visualise(self, stations_data: dict[str, Any]):
        self._ui_waiting_spinner.stop()

        if self._hasRequestError(stations_data):
            self._showErrorMessage(
                self._parent_view, str(stations_data["error_message"])
            )
            return

        self._stations = StationFactory.build(stations_data)
        if self._isDataAvailable():
            self._plotter.plotData(
                self._stations,
                SMEARPlotOptions(
                    self._getSelectedSMEARGas(),
                    self._getSelectedAggregationMethod(),
                ),
            )
        else:
            self._plotter.showEmptyText()

        self._ui_options = self.getUIOptions()
        self._togglePlotActionButtons()

    @pyqtSlot(dict)
    def _setBoundariesToCalendar(self, metadata: dict[str, Any]):
        self._ui_waiting_spinner.stop()
        if self._hasRequestError(metadata):
            self._showErrorMessage(self._parent_view, str(metadata["error_message"]))
            return

        self._parent_view.setEnabled(True)
        periodStarts: list[str] = []
        periodEnds: list[str] = []
        periodStarts.append(metadata["periodStart"])
        periodEnds.append(metadata["periodEnd"])
        periodStart = QtCore.QDateTime.fromString(
            max(periodStarts), QtCore.Qt.DateFormat.ISODate
        )
        self._ui_start_time_edit.setMinimumDateTime(periodStart)
        self._ui_end_time_edit.setMinimumDateTime(periodStart)

        if None not in periodEnds:
            periodEnd = QtCore.QDateTime.fromString(
                min(periodEnds), QtCore.Qt.DateFormat.ISODate
            )
            self._ui_end_time_edit.setMaximumDateTime(periodEnd)
            self._ui_start_time_edit.setMaximumDateTime(periodEnd)

    def _mightToggleFetchButton(self):
        should_enable_fetch = self._isStationsListValid() and self._isDateTimeValid()
        self._ui_fetch_data_button.setEnabled(should_enable_fetch)

    def _isStationsListValid(self) -> bool:
        if self._ui_stations_list.selectedItems():
            return True
        return False

    def _isDateTimeValid(self) -> bool:
        start_time = self._ui_start_time_edit.dateTime()
        end_time = self._ui_end_time_edit.dateTime()
        if start_time < end_time:  # type: ignore
            return True
        return False

    def _addAvailableStationsToSelectionList(self):
        self._ui_stations_list.clear()
        for station in ALL_SMEAR_STATIONS:
            if self._getSelectedSMEARGas().value in ALL_SMEAR_STATIONS[station]:
                self._ui_stations_list.addItem(station)

    def _fetchMetaData(self):
        self._ui_start_time_edit.clearMinimumDateTime()
        self._ui_start_time_edit.clearMaximumDateTime()
        self._ui_end_time_edit.clearMinimumDateTime()
        self._ui_end_time_edit.clearMaximumDateTime()

        if self._ui_stations_list.selectedItems():
            stations = self._ui_stations_list.selectedItems()
            for station in stations:
                gas = self._getSelectedSMEARGas().value
                data = ALL_SMEAR_STATIONS[station.text()][gas]
                self._fetchInBackground(
                    DataFetcher.fetchSMEARVariableMetadata,
                    {"table": data["table"], "variable": data["variable"]},
                    "_setBoundariesToCalendar",
                )

    def _setupComponents(self):
        for station in ALL_SMEAR_STATIONS:
            self._ui_stations_list.addItem(station)

        self._ui_stations_list.sortItems()
        self._ui_stations_list.itemSelectionChanged.connect(
            self._mightToggleFetchButton
        )
        self._ui_start_time_edit.dateTimeChanged.connect(self._mightToggleFetchButton)
        self._ui_end_time_edit.dateTimeChanged.connect(self._mightToggleFetchButton)

        radio_buttons: list = self._ui_gas_radio_buttons.findChildren(QRadioButton)
        for button in radio_buttons:
            self._ui_gas_radio_buttons_group.addButton(button)

        self._ui_gas_radio_buttons_group.buttonClicked.connect(
            self._addAvailableStationsToSelectionList
        )

        self._ui_stations_list.itemSelectionChanged.connect(self._fetchMetaData)

    def _getSelectedSMEARGas(self) -> SMEARGas:
        return SMEARGas[self._ui_gas_radio_buttons_group.checkedButton().text()]

    def _getSelectedAggregationMethod(self) -> SMEARAggregation:
        radio_buttons: list = self._ui_aggregation_radio_buttons.findChildren(
            QRadioButton
        )
        for button in radio_buttons:
            if button.isChecked():
                return SMEARAggregation[button.text()]
        raise Exception("No aggregation method selected")

    def _togglePlotActionButtons(self):
        if self._isDataAvailable():
            self._ui_summary_button.setEnabled(True)
            self._ui_save_plot_button.setEnabled(True)
        else:
            self._ui_summary_button.setEnabled(False)
            self._ui_save_plot_button.setEnabled(False)

    def _isDataAvailable(self):
        for station in self._stations:
            if station.getConcentrations():
                return True
        return False
