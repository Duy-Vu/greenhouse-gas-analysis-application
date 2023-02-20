from typing import Any


class Factory:
    @staticmethod
    def build(data: Any) -> list[Any]:
        raise NotImplementedError("This is an abstract method.")
