from _typeshed import Incomplete
from dependency_injector import containers
from typing import Callable

def container(provided_cls: type, provider_cls: type) -> type[containers.DynamicContainer]: ...

class Injectable:
    inject_name: Incomplete
    inject_cls: Incomplete
    provided_cls: Incomplete
    provider_cls: Incomplete
    def __init__(self, inject_name: str, inject_cls: type, provided_cls: type, provider_cls: type = ...) -> None: ...
    def populate_container(self, container: containers.DynamicContainer, injetion: Callable[[type, type], type[containers.DynamicContainer]] = ..., **kwargs) -> None: ...
