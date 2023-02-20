from model.data_models.figure import Figure
from model.utils.consts import ALL_STATFI_LABELS, YEAR_END_STATFI_DATA, YEAR_START_STATFI_DATA  # type: ignore
from model.data_models.user_options import (
    STATFIOptions,
    STATFIPlotType,
    STATFIPlotOptions,
)
from model.factories.figure_factory import FigureFactory  # type: ignore
from model.tab_handlers.tab_handler import TabHandler
from model.utils.data_fetcher import DataFetcher  # type: ignore
from model.plotters.STATFI_plotter import STATFIPlotter
from PyQt6.QtWidgets import (
    QDateTimeEdit,
    QGroupBox,
    QListWidget,
    QPushButton,
    QRadioButton,
    QButtonGroup,
)
from typing import Any
from PyQt6 import QtCore
from PyQt6.QtCore import QObject, pyqtSlot
from ui.mplwidget import MplWidget
from ui.QtWaitingSpinner import QtWaitingSpinner
from PyQt6.QtWidgets import QMainWindow


class STATFITabHandler(TabHandler, QObject):
    _ui_options: STATFIOptions
    _ui_plot_type_radio_buttons: QGroupBox
    _ui_figures_list: QListWidget
    _ui_start_time_edit: QDateTimeEdit
    _ui_end_time_edit: QDateTimeEdit
    _ui_fetch_data_button: QPushButton
    _ui_save_plot_button: QPushButton
    _plotter: STATFIPlotter
    _parent_view: QMainWindow

    _figures: list[Figure] = []

    def __init__(
        self,
        parent_view: QMainWindow,
        ui_figures_list: QListWidget,
        ui_years_list: QListWidget,
        ui_radio_buttons: QGroupBox,
        ui_fetch_data_button: QPushButton,
        ui_plot: MplWidget,
        ui_save_plot_button: QPushButton,
    ):
        QObject.__init__(self)
        self._parent_view = parent_view
        self._ui_figures_list = ui_figures_list
        self._ui_years_list = ui_years_list
        self._ui_plot_type_radio_buttons = ui_radio_buttons
        self._ui_plot_type_radio_buttons_group = QButtonGroup()
        self._ui_fetch_data_button = ui_fetch_data_button
        self._ui_save_plot_button = ui_save_plot_button
        self._ui_waiting_spinner = QtWaitingSpinner(self._parent_view)
        self._plotter = STATFIPlotter(ui_plot)

        self._setupComponents()
        self._ui_options = self.getUIOptions()
        self._mightToggleFetchButton()

    def fetchAndVisualise(self):
        self._fetchInBackground(
            DataFetcher.fetchSTATFIData, self.getUIOptions(), "_visualise"
        )

    def getUIOptions(self) -> STATFIOptions:
        figures = self._ui_figures_list.selectedItems()
        years = self._ui_years_list.selectedItems()
        return STATFIOptions(
            figure_names=[figure.text() for figure in figures],
            years=[year.text() for year in years],
            plot_type=self._getSelectedPlotType(),
        )

    def setUIOptions(self, options: STATFIOptions):
        self._ui_options = options
        self._ui_figures_list.clearSelection()
        self._ui_years_list.clearSelection()
        for figure_name in options.figure_names:
            self._ui_figures_list.findItems(
                figure_name, QtCore.Qt.MatchFlag.MatchExactly
            )[0].setSelected(True)
        for year in options.years:
            self._ui_years_list.findItems(year, QtCore.Qt.MatchFlag.MatchExactly)[
                0
            ].setSelected(True)
        self._ui_plot_type_radio_buttons.findChildren(QRadioButton)[  # type: ignore
            0 if options.plot_type == STATFIPlotType.BAR_CHART else 1
        ].setChecked(True)

    @pyqtSlot(dict)
    def _visualise(self, figures_data: dict[str, Any]):
        self._ui_waiting_spinner.stop()
        if self._hasRequestError(figures_data):
            self._showErrorMessage(
                self._parent_view, str(figures_data["error_message"])
            )
            return

        self._figures = FigureFactory.build(figures_data)

        if self._isDataAvailable():
            self._plotter.plotData(
                self._figures, STATFIPlotOptions(self._getSelectedPlotType())
            )
        else:
            self._plotter.showEmptyText()

        self._ui_options = self.getUIOptions()
        self._togglePlotActionButtons()

    def _mightToggleFetchButton(self):
        should_enable = self._isFiguresListValid() and self._isYearsListValid()
        self._ui_fetch_data_button.setEnabled(should_enable)

    def _isFiguresListValid(self) -> bool:
        if self._ui_figures_list.selectedItems():
            return True
        return False

    def _isYearsListValid(self) -> bool:
        if self._ui_years_list.selectedItems():
            return True
        return False

    def _setupComponents(self):
        for label_name in ALL_STATFI_LABELS.keys():
            self._ui_figures_list.addItem(label_name)
        for i in range(YEAR_START_STATFI_DATA, YEAR_END_STATFI_DATA + 1):
            self._ui_years_list.addItem(str(i))
        self._ui_figures_list.itemSelectionChanged.connect(self._mightToggleFetchButton)
        self._ui_years_list.itemSelectionChanged.connect(self._mightToggleFetchButton)
        radio_buttons: list = self._ui_plot_type_radio_buttons.findChildren(
            QRadioButton
        )
        for button in radio_buttons:
            self._ui_plot_type_radio_buttons_group.addButton(button)

    def _getSelectedPlotType(self) -> STATFIPlotType:
        button_text: str = self._ui_plot_type_radio_buttons_group.checkedButton().text()
        return (
            STATFIPlotType.BAR_CHART
            if button_text == "Bar chart"
            else STATFIPlotType.LINE_GRAPH
        )

    def _isDataAvailable(self) -> bool:
        return len(self._figures) > 0

    def _togglePlotActionButtons(self):
        if self._isDataAvailable():
            self._ui_save_plot_button.setEnabled(True)
        else:
            self._ui_save_plot_button.setEnabled(False)
