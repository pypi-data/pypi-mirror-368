from abc import ABC, abstractmethod
from typing import Any, Callable, Generator, Optional
from dependency_injector import containers, providers
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
        super().__init__()

    @property
    def name(self) -> str:
        """Return the name of the injection."""
        return self.__name.lower()
    
    @property
    def reference(self) -> str:
        """Return the reference for dependency injection."""
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
        """Inject all children into the current injection context."""
        for child in self.childs:
            setattr(self.container, child.name, child.inject_cls())
            yield from child.resolve_providers()

class ProviderDependency():
    def __init__(self,
        name: str,
        provided_cls: type,
        imports: list['ProviderInjection']
    ) -> None:
        self.name: str = name
        self.provided_cls: type = provided_cls
        self.imports: list['ProviderInjection'] = imports
        super().__init__()

    def __repr__(self) -> str:
        return self.name

class ProviderInjection(BaseInjection):
    def __init__(self,
            name: str,
            component_name: str,
            interface_cls: type,
            parent: Optional["ContainerInjection"] = None
            ) -> None:
        self.component_name: str = component_name
        self.interface_cls: type = interface_cls
        self.__provided_cls: Optional[type] = None
        self.provider_cls: type = providers.Singleton
        self.modules_cls: set[type] = set()
        self.imports: list["ProviderInjection"] = []
        self.depends: list[ProviderDependency] = []
        self.bootstrap: Optional[Callable] = None
        super().__init__(name=name, parent=parent)
    
    @property
    def provided_cls(self) -> type:
        """Return the provided class."""
        if self.__provided_cls is None:
            raise DependencyError(f"Component {self.component_name} was not provided")
        return self.__provided_cls

    def inject_cls(self) -> Any:
        """Return the provider instance."""
        return self.provider_cls(self.provided_cls)

    def resolve_providers(self) -> Generator['ProviderInjection', None, None]:
        """Inject all children into the current injection context."""
        yield self

    def set_implementation(self,
        provided_cls: type,
        provider_cls: type,
        component_cls: type,
        imports: list["ProviderInjection"] = [],
        depends: list[ProviderDependency] = [],
        bootstrap: Optional[Callable] = None
    ) -> None:
        """Set the parameters for the provider.

        Args:
            provided_cls (type): The class that is provided by the provider.
            provider_cls (type): The class that is used to create the provider.
            component_cls (type): The class of the component that is being provided.
            imports (list["ProviderInjection"], optional): A list of provider injections that are imported by this provider.
            depends (list[ProviderDependency], optional): A list of provider dependencies for this provider.
            bootstrap (Optional[Callable], optional): A bootstrap function for the provider.
        """
        self.__provided_cls = provided_cls
        self.provider_cls = provider_cls
        self.modules_cls = set((component_cls,))
        self.imports = imports
        self.depends = depends
        self.bootstrap = bootstrap

    @property
    def dependency(self) -> ProviderDependency:
        """Return the dependency information for the provider."""
        return ProviderDependency(
            name=self.name,
            provided_cls=self.provided_cls,
            imports=self.imports)

    def add_wire_cls(self, wire_cls: type) -> None:
        """Add a class to the set of modules that need to be wired."""
        self.modules_cls.add(wire_cls)

    def do_prewiring(self) -> None:
        """Declare all modules that need to be wired on their respective providers."""
        for provider in self.imports:
            provider.add_wire_cls(self.provided_cls)
        for dependency in self.depends:
            for provider in dependency.imports:
                provider.add_wire_cls(dependency.provided_cls)

    def do_bootstrap(self, container: containers.DynamicContainer) -> None:
        """Wire all modules with their dependencies and bootstrap required components.

        Args:
            container (containers.DynamicContainer): The container to bootstrap the provider in.
        """
        container.wire(modules=self.modules_cls)
        if self.bootstrap is not None:
            self.bootstrap()