import sys

from PyQt6.QtWidgets import QApplication, QMainWindow
from model.options_parser.options_parser import OptionsParser
from model.tab_handlers.SMEAR_tab_handler import SMEARTabHandler
from model.tab_handlers.STATFI_tab_handler import STATFITabHandler
from model.tab_handlers.tab_handler import TabHandler
from model.tab_handlers.compare_tab_handler import CompareTabHandler
from ui.Ui_main_window import Ui_MainWindow


class Window(QMainWindow, Ui_MainWindow):
    _SMEAR_tab_handler: SMEARTabHandler
    _STATFI_tab_handler: STATFITabHandler
    _compare_tab_handler: CompareTabHandler

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._initTabHandlers()
        self._options_parser = OptionsParser(self)
        self._connectSignalsSlots()

    def getTabHandler(self, tab_name: str) -> TabHandler:
        return getattr(self, f"_{tab_name}_tab_handler")

    def _connectSignalsSlots(self):
        self.SMEAR_fetch_button.clicked.connect(self._fetchAndPlot)
        self.STATFI_fetch_button.clicked.connect(self._fetchAndPlot)
        self.compare_fetch_button.clicked.connect(self._fetchAndPlot)
        self.SMEAR_reset_button.clicked.connect(self._reset)
        self.STATFI_reset_button.clicked.connect(self._reset)
        self.compare_reset_button.clicked.connect(self._reset)
        self.SMEAR_summary_button.clicked.connect(self._showSMEARSummary)
        self.SMEAR_save_plot_button.clicked.connect(self._savePlot)
        self.STATFI_save_plot_button.clicked.connect(self._savePlot)
        self.compare_save_plot_button.clicked.connect(self._savePlot)
        self.actionExport_Settings.triggered.connect(self._options_parser.saveOptions)
        self.actionImport_Settings.triggered.connect(self._options_parser.loadOptions)

    def _initTabHandlers(self):
        self._SMEAR_tab_handler = SMEARTabHandler(
            self,
            self.SMEAR_gas_group,
            self.SMEAR_stations_list,
            self.SMEAR_start_time_edit,
            self.SMEAR_end_time_edit,
            self.SMEAR_aggregation_group,
            self.SMEAR_fetch_button,
            self.SMEAR_plot,
            self.SMEAR_summary_button,
            self.SMEAR_save_plot_button,
        )
        self._STATFI_tab_handler = STATFITabHandler(
            self,
            self.STATFI_figures_list,
            self.STATFI_years_list,
            self.STATFI_visualization_group,
            self.STATFI_fetch_button,
            self.STATFI_plot,
            self.STATFI_save_plot_button,
        )
        self._compare_tab_handler = CompareTabHandler(
            self,
            self.compare_STATFI_figures_list,
            self.compare_STATFI_years_list,
            self.compare_SMEAR_gas_group,
            self.compare_SMEAR_stations_list,
            self.compare_SMEAR_years_list,
            self.compare_fetch_button,
            self.compare_plot,
            self.compare_save_plot_button,
        )

    def _fetchAndPlot(self):
        self._getCurrentTabHandler().fetchAndVisualise()

    def _reset(self):
        self._getCurrentTabHandler().resetOptions()

    def _savePlot(self):
        self._getCurrentTabHandler().savePlot(self)

    def _getCurrentTabHandler(self) -> TabHandler:
        tab_name = self.sender().objectName().split("_")[0]
        return self.getTabHandler(tab_name)

    def _showSMEARSummary(self):
        self._SMEAR_tab_handler.showAggregatedInfo()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
