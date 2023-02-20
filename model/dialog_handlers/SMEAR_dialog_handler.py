from datetime import date, datetime

import numpy as np
from model.data_models.station import Station
from PyQt6 import QtCore
from PyQt6.QtWidgets import QDialog, QHeaderView, QTableWidgetItem
from model.data_models.user_options import SMEAROptions
from ui.Ui_SMEAR_summary_dialog import Ui_Dialog


class _SMEARSummaryDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class SMEARDialogHandler:
    _stations: list[Station]
    _ui_options: SMEAROptions
    _summary_dialog: _SMEARSummaryDialog

    def __init__(self, stations: list[Station], ui_options: SMEAROptions):
        self._stations = stations
        self._ui_options = ui_options
        self._summary_dialog = _SMEARSummaryDialog()

    def setupSummaryDialog(self):
        self._summary_dialog.setFixedSize(self._summary_dialog.size())

        self._updateSummaryTable()
        self._styleSummaryTable()

        self._prepareDailyAggregation()
        self._updateDailyAggregation()

        self._summary_dialog.show()

    def _updateSummaryTable(self):
        vertical_headers = ["MIN", "MAX", "AVG"]
        data = self._calculateSummaryTable()
        self._summary_dialog.table.setColumnCount(len(data))
        self._summary_dialog.table.setRowCount(len(vertical_headers))
        horizontal_headers = self._fillSummaryTable(data)
        self._summary_dialog.table.setHorizontalHeaderLabels(horizontal_headers)
        self._summary_dialog.table.setVerticalHeaderLabels(vertical_headers)

    def _styleSummaryTable(self):
        self._summary_dialog.table.resizeColumnsToContents()
        self._summary_dialog.table.resizeRowsToContents()
        table_header = self._summary_dialog.table.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _prepareDailyAggregation(self):
        self._summary_dialog.daily_date_edit.setMinimumDate(
            self._ui_options.start_date_time.date()
        )
        self._summary_dialog.daily_date_edit.setMaximumDate(
            self._ui_options.end_date_time.date()
        )
        self._summary_dialog.daily_station_dropdown.addItems(
            [station.getName() for station in self._stations]
        )
        self._summary_dialog.daily_date_edit.dateChanged.connect(
            self._updateDailyAggregation
        )
        self._summary_dialog.daily_station_dropdown.currentTextChanged.connect(
            self._updateDailyAggregation
        )

    def _calculateSummaryTable(self) -> dict[str, list[float]]:
        data: dict[str, list[float]] = {}
        for station in self._stations:
            try:
                data[station.getName()] = self._getAggregatedConcentration(
                    station.getConcentrations()
                )
            except ValueError:
                data[station.getName()] = [np.nan] * 3
        return data

    def _fillSummaryTable(self, data: dict[str, list[float]]) -> list[str]:
        horizontal_headers = []
        for station_index, station_name in enumerate(sorted(data.keys())):
            horizontal_headers.append(station_name)
            for value_index, value in enumerate(data[station_name]):
                new_item = QTableWidgetItem(f"{value:.2f}")
                new_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
                self._summary_dialog.table.setItem(value_index, station_index, new_item)
        return horizontal_headers

    def _updateDailyAggregation(self):
        (
            chosen_date,
            chosen_station_name,
            chosen_stations,
        ) = self._getChosenDailySummaryOptions()
        (
            daily_min,
            daily_max,
            daily_avg,
            daily_min_station,
            daily_max_station,
        ) = self._calculateDailyAggregation(chosen_date, chosen_stations)

        self._summary_dialog.daily_minimum_value.setText(f"{daily_min:.2f}")
        self._summary_dialog.daily_maximum_value.setText(f"{daily_max:.2f}")
        self._summary_dialog.daily_average_value.setText(f"{daily_avg:.2f}")

        if len(chosen_stations) > 1:
            self._summary_dialog.daily_minimum_station.setText(daily_min_station)
            self._summary_dialog.daily_maximum_station.setText(daily_max_station)
            self._summary_dialog.daily_average_station.setText("All stations")
        else:
            self._summary_dialog.daily_minimum_station.setText(chosen_station_name)
            self._summary_dialog.daily_maximum_station.setText(chosen_station_name)
            self._summary_dialog.daily_average_station.setText(chosen_station_name)

    def _getChosenDailySummaryOptions(self) -> tuple[date, str, list[Station]]:
        chosen_date: date = self._summary_dialog.daily_date_edit.date().toPyDate()
        chosen_station_name: str = (
            self._summary_dialog.daily_station_dropdown.currentText()
        )
        chosen_stations: list[Station] = (
            [
                station
                for station in self._stations
                if station.getName() == chosen_station_name
            ]
            if chosen_station_name != "All stations"
            else self._stations
        )
        return chosen_date, chosen_station_name, chosen_stations

    def _calculateDailyAggregation(
        self, chosen_date: date, chosen_stations: list[Station]
    ) -> tuple[float, float, float, str, str]:
        daily_aggregations: dict[str, list[float]] = {}
        missing_data_station_names: list[str] = []
        for station in chosen_stations:
            try:
                daily_aggregations[
                    station.getName()
                ] = self._getAggregatedConcentration(
                    self._getConcentrationsInDate(station, chosen_date)
                )
            except ValueError:
                missing_data_station_names.append(station.getName())
        self._handleMissingDailyData(missing_data_station_names)

        daily_aggregations_matrix = np.array(list(daily_aggregations.values()))
        daily_min = np.min(daily_aggregations_matrix[:, 0])
        daily_max = np.max(daily_aggregations_matrix[:, 1])
        daily_avg = np.mean(daily_aggregations_matrix[:, 2])

        daily_min_station = list(daily_aggregations.keys())[
            np.where(daily_aggregations_matrix[:, 0] == daily_min)[0][0]
        ]
        daily_max_station = list(daily_aggregations.keys())[
            np.where(daily_aggregations_matrix[:, 1] == daily_max)[0][0]
        ]

        return daily_min, daily_max, daily_avg, daily_min_station, daily_max_station

    def _getConcentrationsInDate(
        self, station: Station, chosen_date: date
    ) -> list[float]:
        start_datetime: datetime = datetime(
            chosen_date.year, chosen_date.month, chosen_date.day, 0, 0, 0
        )
        end_datetime: datetime = datetime(
            chosen_date.year, chosen_date.month, chosen_date.day, 23, 59, 59
        )
        timestamps = station.getTimeStamps()
        timestamps_in_date_indices: list[int] = []
        for timestamp_index, timestamp in enumerate(timestamps):
            if start_datetime <= timestamp <= end_datetime:
                timestamps_in_date_indices.append(timestamp_index)
        try:
            concentrations_in_date = station.getConcentrations()[
                timestamps_in_date_indices[0] : timestamps_in_date_indices[-1] + 1
            ]
            return concentrations_in_date
        except IndexError:
            return []

    def _getAggregatedConcentration(self, concentrations: list[float]) -> list[float]:
        if not concentrations:
            raise ValueError("No data to aggregate")
        return [
            np.min(concentrations),
            np.max(concentrations),
            np.mean(concentrations),
        ]

    def _handleMissingDailyData(self, missing_data_station_names: list[str]):
        self._disableMissingStations(missing_data_station_names)
        if missing_data_station_names:
            self._showWarningInSummaryDialog(
                f"No data is available from {', '.join(missing_data_station_names)} "
                "in the chosen date. "
                "Displaying aggregated value from available data."
            )
        else:
            self._clearWarningInSummaryDialog()

    def _disableMissingStations(self, missing_data_station_names):
        is_station_available_list: list[bool] = [True] + [
            station.getName() not in missing_data_station_names
            for station in self._stations
        ]
        for station_index, is_station_available in enumerate(is_station_available_list):
            self._summary_dialog.daily_station_dropdown.model().item(
                station_index
            ).setEnabled(is_station_available)

    def _showWarningInSummaryDialog(self, message: str):
        self._summary_dialog.warning.setText(message)

    def _clearWarningInSummaryDialog(self):
        self._summary_dialog.warning.setText("")
