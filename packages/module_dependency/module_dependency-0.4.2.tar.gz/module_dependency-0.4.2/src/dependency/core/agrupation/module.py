from typing import Callable, Optional, TypeVar, cast
from dependency.core.agrupation.base import ABCModule
from dependency.core.injection.base import ContainerInjection

MODULE = TypeVar('MODULE', bound='Module')

class Module(ABCModule):
    """Module Base Class
    """
    def __init__(self, name: str, injection: ContainerInjection) -> None:
        self.__injection: ContainerInjection = injection
        super().__init__(name)
    
    @property
    def injection(self) -> ContainerInjection:
        return self.__injection

def module(
    module: Optional[type[Module]] = None
    ) -> Callable[[type[MODULE]], MODULE]:
    """Decorator for Module class

    Returns:
        Callable[[type[Module]], Module]: Decorator function that wraps the module class.
    """
    # Cast due to mypy not supporting class decorators
    _module = cast(Optional[Module], module)
    def wrap(cls: type[MODULE]) -> MODULE:
        if not issubclass(cls, Module):
            raise TypeError(f"Class {cls} is not a subclass of Module")

        injection = ContainerInjection(
            name=cls.__name__,
            parent=_module.injection if _module else None)

        return cls(
            name=cls.__name__,
            injection=injection)
    return wrap