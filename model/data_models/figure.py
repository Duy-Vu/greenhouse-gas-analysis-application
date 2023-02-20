import numpy as np


class Figure:
    """Correspond to a STATFI's Tiedo. Each Figure is only one Tiedo,
    whose data can span multiple years
    """

    _nameValue: str
    _nameText: str
    _yearlyData: dict[int, float]

    def __init__(self, nameValue: str, years: list[int]):
        self._nameValue = nameValue
        self._nameText = ""
        self._yearlyData = {}
        for year in years:
            self._yearlyData[year] = np.nan

    def setYearlyData(self, year: int, data: float):
        if not data:
            data = np.nan
        self._yearlyData[year] = data

    def setNameText(self, nameText: str):
        self._nameText = nameText

    def getNameText(self) -> str:
        return self._nameText

    def getNameValue(self) -> str:
        return self._nameValue

    def getYearlyData(self) -> dict[int, float]:
        return self._yearlyData

    def getYears(self) -> list[int]:
        return list(self._yearlyData.keys())
