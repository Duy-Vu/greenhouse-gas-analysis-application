import json
from dataclasses import asdict
from datetime import datetime
from typing import Any
from PyQt6.QtWidgets import QMainWindow

from model.data_models.user_options import (
    AllTabsOptions,
    CompareOptions,
    SMEARAggregation,
    SMEARGas,
    SMEAROptions,
    STATFIOptions,
    STATFIPlotType,
)
from model.utils.consts import OPTIONS_DIRECTORY  # type: ignore
from model.utils.file_manager import newFile, openFile  # type: ignore


class OptionsParser:
    _window: QMainWindow

    def __init__(self, window: QMainWindow):
        self._window = window

    def saveOptions(self):
        file_name = newFile(
            self._window,
            "Export current options",
            f"{OPTIONS_DIRECTORY}/{datetime.now().ctime()}.json",
            "JSON files (*.json)",
        )
        if not file_name:
            return
        options_dict = self._getAllTabOptionsDict()
        with open(
            file_name,
            "w",
            encoding="utf-8",
        ) as json_file:
            json.dump(
                options_dict,
                json_file,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

    def loadOptions(self):
        file_name = openFile(
            self._window,
            "Import saved options",
            OPTIONS_DIRECTORY,
            "JSON files (*.json)",
        )
        if not file_name:
            return
        with open(file_name, "r", encoding="utf-8") as json_file:
            try:
                options_dict = json.load(json_file)
                options = self._dictToAllTabsOptions(options_dict)
                self._setTabsUIOptions(options)
                self._window.getTabHandler("SMEAR").fetchAndVisualise()
                self._window.getTabHandler("STATFI").fetchAndVisualise()
                self._window.getTabHandler("compare").fetchAndVisualise()
            except json.decoder.JSONDecodeError:
                raise ValueError(f"Could not parse JSON in {file_name}")

    def _getAllTabOptionsDict(self):
        options_dict = self._allTabsOptionsToDict(
            AllTabsOptions(
                SMEAR=self._window._SMEAR_tab_handler.getUIOptions(),
                STATFI=self._window._STATFI_tab_handler.getUIOptions(),
                compare=self._window._compare_tab_handler.getUIOptions(),
            )
        )
        return options_dict

    def _allTabsOptionsToDict(self, options: AllTabsOptions) -> dict[str, Any]:
        return {
            "SMEAR": self._SMEAROptionsToDict(options.SMEAR),
            "STATFI": self._STATFIOptionsToDict(options.STATFI),
            "compare": self._CompareOptionsToDict(options.compare),
        }

    def _SMEAROptionsToDict(self, options: SMEAROptions) -> dict[str, Any]:
        SMEAR_options_dict = asdict(options)
        SMEAR_options_dict["gas"] = SMEAR_options_dict["gas"].name
        SMEAR_options_dict["aggregation_method"] = SMEAR_options_dict[
            "aggregation_method"
        ].name
        return SMEAR_options_dict

    def _STATFIOptionsToDict(self, options: STATFIOptions) -> dict[str, Any]:
        STATFI_options_dict = asdict(options)
        STATFI_options_dict["plot_type"] = STATFI_options_dict["plot_type"].name
        return STATFI_options_dict

    def _CompareOptionsToDict(self, options: CompareOptions) -> dict[str, Any]:
        compare_options_dict = asdict(options)
        compare_options_dict["SMEAR_gas"] = compare_options_dict["SMEAR_gas"].name
        return compare_options_dict

    def _dictToAllTabsOptions(self, options: dict[str, Any]):
        return AllTabsOptions(
            SMEAR=self._dictToSMEAROptions(options["SMEAR"]),
            STATFI=self._dictToSTATFIOptions(options["STATFI"]),
            compare=self._dictToCompareOptions(options["compare"]),
        )

    def _dictToSMEAROptions(self, SMEAR_options_dict: dict[str, Any]) -> SMEAROptions:
        SMEAR_time_format = "%Y-%m-%d %H:%M:%S"

        SMEAR_options_dict["gas"] = SMEARGas[SMEAR_options_dict["gas"]]
        SMEAR_options_dict["aggregation_method"] = SMEARAggregation[
            SMEAR_options_dict["aggregation_method"]
        ]
        SMEAR_options_dict["start_date_time"] = datetime.strptime(
            SMEAR_options_dict["start_date_time"], SMEAR_time_format
        )
        SMEAR_options_dict["end_date_time"] = datetime.strptime(
            SMEAR_options_dict["end_date_time"], SMEAR_time_format
        )
        return SMEAROptions(**SMEAR_options_dict)

    def _dictToSTATFIOptions(
        self, STATFI_options_dict: dict[str, Any]
    ) -> STATFIOptions:
        STATFI_options_dict["plot_type"] = STATFIPlotType[
            STATFI_options_dict["plot_type"]
        ]
        return STATFIOptions(**STATFI_options_dict)

    def _dictToCompareOptions(
        self, compare_options_dict: dict[str, Any]
    ) -> CompareOptions:
        compare_options_dict["SMEAR_gas"] = SMEARGas[compare_options_dict["SMEAR_gas"]]
        return CompareOptions(**compare_options_dict)

    def _setTabsUIOptions(self, options: AllTabsOptions):
        self._window._SMEAR_tab_handler.setUIOptions(options.SMEAR)  # type: ignore
        self._window._STATFI_tab_handler.setUIOptions(options.STATFI)  # type: ignore
        self._window._compare_tab_handler.setUIOptions(options.compare)  # type: ignore
