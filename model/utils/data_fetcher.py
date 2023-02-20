from typing import Any
from datetime import datetime
from PyQt6.QtCore import QRunnable, QMetaObject, Qt, Q_ARG
import requests
from model.data_models.user_options import (
    CompareOptions,
    SMEAROptions,
    SMEARAggregation,
    STATFIOptions,
    STATFIPlotType,
)
from model.utils.request_builder import (  # type: ignore
    STATFI_BASE_URL,
    createSMEARUrl,
    createSTATFIDataObject,
)
from model.utils import consts  # type: ignore


def createErrorDict(message: str) -> dict[str, str]:
    error = {}
    error["error_message"] = message
    return error


class DataFetcher:
    @staticmethod
    def fetchSMEARData(options: SMEAROptions) -> dict[str, Any]:
        # Can be empty when loaded from a json.
        if not options.stations:
            return {}
        url = createSMEARUrl(options)
        try:
            response_API = requests.get(url)
        except requests.exceptions.RequestException as e:
            error_dict = createErrorDict(consts.NETWORK_ERROR_MSG)
            return error_dict

        status_code = response_API.status_code
        # TODO: If error occurs, warns the user through the UI
        if status_code >= 400 and status_code <= 599:
            error_dict = createErrorDict(
                "GET request to SMEAR failed with status code: " + str(status_code)
            )
            return error_dict
        return response_API.json()

    @staticmethod
    def fetchSTATFIData(options: STATFIOptions) -> dict[str, Any]:
        # Can be empty when loaded from a json.
        if not options.figure_names or not options.years:
            return {}
        url = STATFI_BASE_URL
        request_object = createSTATFIDataObject(options)
        try:
            response_API = requests.post(url, json=request_object)
        except requests.exceptions.RequestException as e:
            error_dict = createErrorDict(consts.NETWORK_ERROR_MSG)
            return error_dict

        status_code = response_API.status_code
        # TODO: If error occurs, warns the user through the UI
        if status_code >= 400 and status_code <= 599:
            error_dict = createErrorDict(
                "POST request to STATFI failed with status code: " + str(status_code)
            )
            return error_dict

        return response_API.json()

    @staticmethod
    def fetchComparisonData(options: CompareOptions) -> dict[str, Any]:
        if (
            not options.STATFI_figure_names
            or not options.STATFI_years
            or not options.SMEAR_stations
            or not options.SMEAR_years
        ):
            return {}

        compare_data: dict[str, list[dict[str, Any]]] = {}

        compare_data["STATFI"] = [
            DataFetcher.fetchSTATFIData(
                STATFIOptions(
                    figure_names=options.STATFI_figure_names,
                    years=options.STATFI_years,
                    plot_type=STATFIPlotType.BAR_CHART,
                )
            )
        ]

        SMEAR_data = []
        options.SMEAR_years.sort()
        for year in options.SMEAR_years:
            start_date_time = datetime(int(year), 1, 1, 0, 0, 0)
            end_date_time = datetime(int(year), 12, 31, 23, 59, 59)

            SMEAR_data.append(
                DataFetcher.fetchSMEARData(
                    SMEAROptions(
                        gas=options.SMEAR_gas,
                        aggregation_method=SMEARAggregation.AVG,
                        start_date_time=start_date_time,
                        end_date_time=end_date_time,
                        stations=options.SMEAR_stations,
                    )
                )
            )
        compare_data["SMEAR"] = SMEAR_data
        return compare_data

    @staticmethod
    def fetchSMEARVariableMetadata(options: dict[str, str]) -> dict[str, Any]:
        if not options:
            return {}
        url = "https://smear-backend.rahtiapp.fi/search/variable?tablevariable={table}.{variable}".format(
            table=options["table"], variable=options["variable"]
        )
        try:
            response_API = requests.get(url)
        except requests.exceptions.RequestException as e:
            error_dict = createErrorDict(consts.NETWORK_ERROR_MSG)
            return error_dict

        status_code = response_API.status_code
        if status_code >= 400 and status_code <= 599:
            error_dict = createErrorDict(
                "GET request to SMEAR failed with status code: " + str(status_code)
            )
            return error_dict
        # SMEAR tab handler only cares about first data in the array.
        return response_API.json()[0]


class DataFetcherWrapper(QRunnable):
    def __init__(self, owner, callable, param, callback):
        QRunnable.__init__(self)
        self._owner = owner
        self._callable = callable
        self._param = param
        self._callback = callback

    def run(self):
        data = self._callable(self._param)
        QMetaObject.invokeMethod(
            self._owner,
            self._callback,
            Qt.ConnectionType.QueuedConnection,
            Q_ARG(dict, data),
        )
