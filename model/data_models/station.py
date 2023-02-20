from datetime import datetime
from model.utils.consts import ALL_SMEAR_STATIONS  # type: ignore


class Station:
    _station_id: str
    _concentrations: list[float]
    _time_stamps: list[datetime]

    def __init__(self, station_id: str):
        self._station_id = station_id
        self._concentrations = []
        self._time_stamps = []

    def setConcentrations(self, concentrations: list[float]):
        self._concentrations = concentrations

    def setTimeStamps(self, time_stamps: list[datetime]):
        self._time_stamps = time_stamps

    def getIdentifier(self) -> str:
        return self._station_id

    def getName(self) -> str:
        for station_name in ALL_SMEAR_STATIONS:
            for gas_info in ALL_SMEAR_STATIONS[station_name].values():
                if self._station_id == f"{gas_info['table']}.{gas_info['variable']}":
                    return station_name
        raise Exception(f"No station name found for id {self._station_id}")

    def getTimeStamps(self) -> list[datetime]:
        return self._time_stamps

    def getConcentrations(self) -> list[float]:
        return self._concentrations
