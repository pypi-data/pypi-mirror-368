import pytest
from abc import ABC, abstractmethod
from dependency_injector import containers, providers
from dependency.core.agrupation import Module, module
from dependency.core.declaration import Component, component, instance
from dependency.core.exceptions import DependencyError

class TInterface(ABC):
    @abstractmethod
    def method(self) -> str:
        pass

@module(
    module=None,
)
class TModule(Module):
    pass

@component(
    module=TModule,
    interface=TInterface,
)
class TComponent(Component):
    pass

@instance(
    component=TComponent,
    imports=[],
    provider=providers.Singleton,
)
class TInstance(TInterface):
    def method(self) -> str:
        return "Hello, World!"

def test_declaration():
    with pytest.raises(DependencyError):
        print(TComponent.provide())

    container = containers.DynamicContainer()
    setattr(container, TModule.injection.name, TModule.injection.inject_cls())
    for provider in list(TModule.injection.resolve_providers()):
        provider.do_bootstrap(container)

    component: TInterface = TComponent.provide()
    assert isinstance(component, TInterface)
    assert component.method() == "Hello, World!"