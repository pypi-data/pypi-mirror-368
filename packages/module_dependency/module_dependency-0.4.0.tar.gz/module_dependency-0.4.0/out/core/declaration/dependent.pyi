from dependency.core.declaration.base import ABCComponent, ABCDependent, ABCProvider as ABCProvider
from typing import Callable, Sequence

class Dependent(ABCDependent):
    @classmethod
    def resolve_dependent(cls, providers: Sequence[ABCProvider]) -> list[str]: ...

def dependent(imports: Sequence[type[ABCComponent]] = []) -> Callable[[type[Dependent]], type[Dependent]]: ...
