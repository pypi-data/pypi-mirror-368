from _typeshed import Incomplete
from dependency.core.container.injectable import Injectable
from dependency.core.declaration.base import ABCProvider
from dependency.core.declaration.component import Component
from dependency.core.declaration.dependent import Dependent as Dependent
from dependency_injector import containers as containers, providers
from typing import Callable

class Provider(ABCProvider):
    provider: Incomplete
    imports: Incomplete
    dependents: Incomplete
    def __init__(self, imports: list[Component], dependents: list[type[Dependent]], provided_cls: type, inject: Injectable) -> None: ...
    unresolved_dependents: Incomplete
    def resolve_dependents(self, dependents: list[type[Dependent]]) -> None: ...
    def resolve(self, container: containers.DynamicContainer, providers: list['Provider'], **kwargs) -> None: ...

class HasDependent:
    def declare_dependents(self, dependents: list[type[Dependent]]) -> None: ...

def provider(component: type[Component], imports: list[type[Component]] = [], dependents: list[type[Dependent]] = [], provider: type[providers.Provider] = ...) -> Callable[[type], Provider]: ...
