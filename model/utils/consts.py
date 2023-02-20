StationsDict = dict[str, dict[str, dict[str, str]]]

OPTIONS_DIRECTORY = "./options"

ALL_SMEAR_STATIONS: StationsDict = {
    "Värriö": {
        "CO2": {"table": "VAR_EDDY", "variable": "av_c"},
        "SO2": {"table": "VAR_META", "variable": "SO2_1"},
        "NO": {"table": "VAR_META", "variable": "NO_1"},
    },
    "Hyytiälä": {
        "CO2": {"table": "HYY_META", "variable": "CO2icos168"},
        "SO2": {"table": "HYY_META", "variable": "SO2168"},
        "NO": {"table": "HYY_META", "variable": "NO168"},
    },
    "Kumpula": {
        "CO2": {"table": "KUM_EDDY", "variable": "av_c_ep"},
        "SO2": {"table": "KUM_META", "variable": "SO_2"},
        "NO": {"table": "KUM_META", "variable": "NO"},
    },
    "Siikaneva 1": {
        "CO2": {"table": "SII1_EDDY", "variable": "av_c"},
    },
    "Siikaneva 2": {
        "CO2": {"table": "SII2_EDDY", "variable": "av_c"},
    },
    "Kuivajärvi": {
        "CO2": {"table": "KVJ_EDDY", "variable": "av_c_LI72"},
    },
    "Viikki": {
        "CO2": {"table": "VII_EDDY", "variable": "av_c"},
    },
    "Haltiala": {
        "CO2": {"table": "HAL_EDDY", "variable": "av_c"},
    },
}

# Store the title as keys because the UI shows the titles, and we need to convert
# titles to ids.
ALL_STATFI_LABELS: dict[str, str] = {
    "Greenhouse gas emissions, indexed, year 1990 = 100": "Khk_yht_index",
    "Intensity of greenhouse gas emissions": "Khk_yht_las",
    "Intensity of greenhouse gases, indexed, year 1990 = 100": "Khk_yht_las_index",
    "Greenhouse gas emissions 2), CO2 equivalent 1000 t": "Khk_yht",
}

NETWORK_ERROR_MSG: str = "Network error, check your connection"

YEAR_START_STATFI_DATA: int = 1990
YEAR_END_STATFI_DATA: int = 2017
