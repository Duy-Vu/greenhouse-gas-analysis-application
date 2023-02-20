from datetime import datetime
from typing import Any
from model.factories.factory import Factory  # type: ignore
from model.data_models.station import Station


class StationFactory(Factory):
    @staticmethod
    def build(data: dict[str, Any]) -> list[Station]:
        stations = []
        datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
        try:
            station_ids = data["columns"]
            for station_id in station_ids:
                station = Station(station_id)
                timestamps = []
                concentrations = []
                for concentration_data in data["data"]:
                    concentration: float = concentration_data[station_id]
                    if concentration is not None:
                        timestamps.append(
                            datetime.strptime(
                                concentration_data["samptime"], datetime_format
                            )
                        )
                        concentrations.append(concentration)
                station.setTimeStamps(timestamps)
                station.setConcentrations(concentrations)
                stations.append(station)
            return stations
        except KeyError:
            return stations
