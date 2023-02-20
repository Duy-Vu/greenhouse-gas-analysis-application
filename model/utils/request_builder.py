from typing import Any
from model.data_models.user_options import SMEAROptions, STATFIOptions


SMEAR_BASE_URL = "https://smear-backend.rahtiapp.fi/search/timeseries"
STATFI_BASE_URL = "https://pxnet2.stat.fi:443/PXWeb/api/v1/en/ymp/taulukot/Kokodata.px"


def createSMEARUrl(options: SMEAROptions) -> str:
    # An example URL:
    # 'https://smear-backend.rahtiapp.fi/search/timeseries
    # ?aggregation=MAX&interval=60&from=2022-01-19T14:00:00.000
    # &to=2022-01-19T17:00:00.000&tablevariable=KUM_EDDY.av_c_ep'
    url = SMEAR_BASE_URL
    url += "?aggregation=" + options.aggregation_method.value
    url += "&interval=" + options.interval
    url += "&from=" + options.start_date_time.isoformat()
    url += "&to=" + options.end_date_time.isoformat()
    for station_index in range(len(options.table_names)):
        url += (
            "&tablevariable="
            + options.table_names[station_index]
            + "."
            + options.variable_names[station_index]
        )
    return url


def createSTATFIDataObject(options: STATFIOptions) -> dict[str, Any]:
    return {
        "query": [
            {
                "code": "Tiedot",
                "selection": {"filter": "item", "values": options.figure_ids},
            },
            {
                "code": "Vuosi",
                "selection": {"filter": "item", "values": options.years},
            },
        ],
        "response": {"format": "json-stat2"},
    }
