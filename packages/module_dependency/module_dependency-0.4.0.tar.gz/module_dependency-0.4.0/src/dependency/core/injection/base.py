from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Optional
from dependency_injector import containers
from dependency.core.exceptions import DependencyError

class BaseInjection(ABC):
    def __init__(self,
        name: str,
        parent: Optional["ContainerInjection"] = None
    ) -> None:
        self.__name = name
        self.__parent = parent
        if parent:
            parent.childs.append(self)

    @property
    def name(self) -> str:
        """Return the name of the injection."""
        return self.__name.lower()
    
    @property
    def reference(self) -> str:
        if not self.__parent:
            return self.name
        return f"{self.__parent.reference}.{self.name}"
    
    @abstractmethod
    def inject_cls(self) -> Any:
        """Return the class to be injected."""
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    @abstractmethod
    def resolve_providers(self) -> Generator['ProviderInjection', None, None]:
        """Inject all children into the current injection context."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def __repr__(self) -> str:
        return self.__name

class ContainerInjection(BaseInjection):
    def __init__(self,
            name: str,
            parent: Optional["ContainerInjection"] = None
            ) -> None:
        self.childs: list[BaseInjection] = []
        self.container = containers.DynamicContainer()
        super().__init__(name=name, parent=parent)

    def inject_cls(self) -> containers.DynamicContainer:
        """Return the container instance."""
        return self.container
    
    def resolve_providers(self) -> Generator['ProviderInjection', None, None]:
        for child in self.childs:
            setattr(self.container, child.name, child.inject_cls())
            yield from child.resolve_providers()

class ProviderDependency():
    def __init__(self,
        name: str,
        imports: list['ProviderInjection']
    ) -> None:
        self.name: str = name
        self.imports: list['ProviderInjection'] = imports

class ProviderInjection(BaseInjection):
    def __init__(self,
            name: str,
            interface_cls: type,
            parent: Optional["ContainerInjection"] = None
            ) -> None:
        self.interface_cls: type = interface_cls
        self.provided_cls: type
        self.provider_cls: type
        self.component_cls: type
        self.imports: list["ProviderInjection"] = []
        self.bootstrap: Optional[Callable] = None
        super().__init__(name=name, parent=parent)

    def inject_cls(self) -> Any:
        """Return the provider instance."""
        if self.provider_cls is None:
            raise DependencyError("ProviderInjection must have provided_cls and provider_cls set before injection.")
        return self.provider_cls(self.provided_cls)

    def resolve_providers(self) -> Generator['ProviderInjection', None, None]:
        yield self

    def set_implementation(self,
        provided_cls: type,
        provider_cls: type,
        component_cls: type,
        imports: list["ProviderInjection"] = [],
        depends: list[ProviderDependency] = [],
        bootstrap: Optional[Callable] = None
    ) -> None:
        """Set the parameters for the provider."""
        self.provided_cls = provided_cls
        self.provider_cls = provider_cls
        self.component_cls = component_cls
        self.imports = imports
        self.depends = depends
        self.bootstrap = bootstrap

    def do_bootstrap(self, container: containers.DynamicContainer) -> None:
        container.wire(modules=[self.component_cls])
        if self.bootstrap is not None:
            self.bootstrap()