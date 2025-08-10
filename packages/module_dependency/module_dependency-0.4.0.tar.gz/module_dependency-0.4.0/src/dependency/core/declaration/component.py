from typing import Any, Callable, Optional, TypeVar, cast
from dependency_injector.wiring import Provide, inject
from dependency.core.agrupation.module import Module
from dependency.core.declaration.base import ABCComponent, ABCInstance
from dependency.core.injection.base import ProviderInjection
from dependency.core.exceptions import DependencyError

COMPONENT = TypeVar('COMPONENT', bound='Component')

class Component(ABCComponent):
    """Component Base Class
    """
    def __init__(self, interface_cls: type, injection: ProviderInjection) -> None:
        super().__init__(interface_cls=interface_cls)
        self.__injection: ProviderInjection = injection
        self.__instance: Optional[ABCInstance] = None
    
    @property
    def injection(self) -> ProviderInjection:
        return self.__injection

    @property
    def instance(self) -> Optional[ABCInstance]:
        return self.__instance
    
    @instance.setter
    def instance(self, instance: ABCInstance) -> None:
        if self.__instance:
            raise DependencyError(f"Component {self} is already instanced by {self.__instance}. Attempted to set new instance: {instance}")
        self.__instance = instance
    
    @staticmethod
    def provide() -> Any:
        pass

def component(
    module: type[Module],
    interface: type
) -> Callable[[type[COMPONENT]], COMPONENT]:
    """Decorator for Component class

    Args:
        module (ABCModule): Module instance to register the component.
        interface (type): Interface class to be used as a base class for the component.
    
    Raises:
        TypeError: If the wrapped class is not a subclass of Component.

    Returns:
        Callable[[type[Component]], Component]: Decorator function that wraps the component class.
    """
    # Cast due to mypy not supporting class decorators
    _module = cast(Module, module)
    def wrap(cls: type[COMPONENT]) -> COMPONENT:
        if not issubclass(cls, Component):
            raise TypeError(f"Class {cls} is not a subclass of Component")
        
        injection = ProviderInjection(
            name=interface.__name__,
            interface_cls=interface,
            parent=_module.injection)

        class WrapComponent(cls): # type: ignore
            def __init__(self) -> None:
                super().__init__(
                    interface_cls=interface,
                    injection=injection)

            @inject
            def provide(self, service: Any = Provide[injection.reference]) -> Any:
                if isinstance(service, Provide): # type: ignore
                    raise DependencyError(f"Component {cls.__name__} was not provided")
                return service
        return WrapComponent()
    return wrap