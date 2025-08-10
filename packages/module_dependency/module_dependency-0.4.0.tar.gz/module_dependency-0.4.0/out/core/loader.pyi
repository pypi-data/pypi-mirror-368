from _typeshed import Incomplete
from dependency.core.container import Container as Container
from dependency.core.module.base import Module

logger: Incomplete

def resolve_dependency(container: Container, appmodule: type[Module]) -> None: ...
