from _typeshed import Incomplete
from abc import ABC

class ABCComponent(ABC):
    base_cls: Incomplete
    def __init__(self, base_cls: type) -> None: ...

class ABCProvider(ABC):
    provided_cls: Incomplete
    def __init__(self, provided_cls: type) -> None: ...

class ABCDependent(ABC): ...
