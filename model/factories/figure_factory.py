from typing import Any
from model.factories.factory import Factory  # type: ignore
from model.data_models.figure import Figure


class FigureFactory(Factory):
    @staticmethod
    def build(data: dict[str, Any]) -> list[Figure]:
        try:
            figure_index_dict = data["dimension"]["Tiedot"]["category"]["index"]
            figure_name_text_dict = data["dimension"]["Tiedot"]["category"]["label"]
            year_index_dict = data["dimension"]["Vuosi"]["category"]["index"]
            years_int = [int(year) for year in year_index_dict.keys()]
            yearly_values_list = [
                data["value"][i : i + len(years_int)]
                for i in range(0, len(data["value"]), len(years_int))
            ]
            figures = []
            for figure_name_value, figure_index in figure_index_dict.items():
                figure = Figure(nameValue=figure_name_value, years=years_int)
                figure.setNameText(figure_name_text_dict[figure_name_value])
                for year_string, year_index in year_index_dict.items():
                    figure.setYearlyData(
                        int(year_string), yearly_values_list[figure_index][year_index]
                    )
                figures.append(figure)
            return figures
        except KeyError:
            return []
