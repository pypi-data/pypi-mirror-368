from abc import ABC

class ABCModule(ABC):
    def __init__(self, name: str) -> None:
        self.name: str = name

    def __repr__(self) -> str:
        return self.name